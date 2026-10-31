"""
engine.py — Decode + audio/video sync engine built directly on PyAV
(FFmpeg's real C libraries: libavformat, libavcodec, libswscale, libswresample).

Architecture (same pattern real players use, e.g. ffplay):

  Demux thread  -> reads packets, decodes them, pushes frames into
                   bounded video/audio queues (backpressure via queue size)
  Audio thread  -> pulls audio frames, writes samples into sounddevice's
                   output stream via a callback. Audio is the SYNC MASTER:
                   its playback position is the "clock" everything else
                   follows, because audio can't skip/wait without glitching.
  Video (main)  -> pulls decoded video frames, compares each frame's
                   timestamp (pts) to the current audio clock, and only
                   displays it once the clock catches up (or drops it if
                   we're already late), keeping video locked to audio.

This file has no GUI code — it's the reusable engine. ui.py builds the
pygame window + controls on top of it.
"""

import queue
import threading
import time

import av
import numpy as np
import sounddevice as sd


class MediaEngine:
    def __init__(self, path, video_queue_size=8, audio_queue_seconds=2.0):
        self.path = path
        self.container = av.open(path)

        self.video_stream = next((s for s in self.container.streams if s.type == "video"), None)
        self.audio_stream = next((s for s in self.container.streams if s.type == "audio"), None)
        if self.video_stream is None and self.audio_stream is None:
            raise RuntimeError("No playable video or audio stream found")

        self.duration = float(self.container.duration / av.time_base) if self.container.duration else 0.0

        self.video_queue = queue.Queue(maxsize=video_queue_size)
        self.audio_queue = queue.Queue(maxsize=64)

        # Playback state
        self.paused = threading.Event()
        self.paused.set()  # start paused; caller calls play()
        self.muted = False
        self.volume = 1.0
        self.stop_flag = threading.Event()
        self.seek_request = None  # seconds, set externally to trigger a seek
        self._seek_lock = threading.Lock()

        # Clock bookkeeping
        self._audio_clock = 0.0          # seconds, updated by audio callback
        self._audio_clock_lock = threading.Lock()
        self._stream_start_time = None   # wall-clock time playback last (re)started
        self._clock_offset = 0.0         # seconds into the media at that start time

        self._audio_out_stream = None
        self._demux_thread = None
        self._sample_rate = self.audio_stream.rate if self.audio_stream else 44100
        self._channels = min(self.audio_stream.channels, 2) if self.audio_stream else 2

        self.ended = threading.Event()

    # ------------------------------------------------------------ control
    def start(self):
        if self.audio_stream:
            try:
                self._start_audio_output()
            except Exception as e:
                print(f"[audio output unavailable, continuing video-only: {e}]")
                self.audio_stream = None
        self._demux_thread = threading.Thread(target=self._demux_loop, daemon=True)
        self._demux_thread.start()

    def play(self):
        self._stream_start_time = time.time()
        with self._audio_clock_lock:
            self._clock_offset = self._audio_clock if self.audio_stream else self._clock_offset
        self.paused.clear()

    def pause(self):
        # lock in how far we've gotten before freezing the clock
        # (call get_clock() before acquiring the lock ourselves — it
        # acquires the same lock internally, and it's not reentrant)
        self._clock_offset = self.get_clock()
        self.paused.set()

    def toggle_mute(self):
        self.muted = not self.muted
        return self.muted

    def set_volume(self, vol_0_to_1):
        self.volume = max(0.0, min(1.0, vol_0_to_1))

    def seek(self, seconds):
        seconds = max(0.0, min(seconds, self.duration if self.duration else seconds))
        with self._seek_lock:
            self.seek_request = seconds
        with self._audio_clock_lock:
            self._audio_clock = seconds
            self._clock_offset = seconds
        self._stream_start_time = time.time()
        self.ended.clear()

    def get_clock(self):
        """Current playback position in seconds (the master A/V sync clock)."""
        if self.audio_stream:
            with self._audio_clock_lock:
                return self._audio_clock
        # video-only fallback: derive from wall clock
        if self.paused.is_set() or self._stream_start_time is None:
            return self._clock_offset
        return self._clock_offset + (time.time() - self._stream_start_time)

    def stop(self):
        self.stop_flag.set()
        self.paused.clear()  # wake any waiting loop
        if self._audio_out_stream:
            try:
                self._audio_out_stream.stop()
                self._audio_out_stream.close()
            except Exception:
                pass
        # IMPORTANT: wait for the demux thread to actually exit before
        # closing the container. Closing libav's C structures while
        # another thread is still mid-iteration over them corrupts
        # memory and can segfault the whole process.
        if self._demux_thread and self._demux_thread.is_alive():
            self._demux_thread.join(timeout=2.0)
        try:
            self.container.close()
        except Exception:
            pass

    # ------------------------------------------------------------ demux/decode
    def _demux_loop(self):
        streams = [s for s in (self.video_stream, self.audio_stream) if s is not None]
        try:
            for packet in self.container.demux(streams):
                if self.stop_flag.is_set():
                    return

                with self._seek_lock:
                    pending_seek = self.seek_request
                    self.seek_request = None
                if pending_seek is not None:
                    self._do_seek(pending_seek)
                    continue

                for frame in packet.decode():
                    if self.stop_flag.is_set():
                        return
                    if packet.stream.type == "video":
                        self._push_video_frame(frame)
                    elif packet.stream.type == "audio":
                        self._push_audio_frame(frame)
            self.ended.set()
        except av.error.EOFError:
            self.ended.set()
        except Exception as e:
            print(f"[demux error] {e}")
            self.ended.set()

    def _do_seek(self, seconds):
        try:
            self.container.seek(int(seconds * av.time_base))
        except Exception as e:
            print(f"[seek error] {e}")
        # Drop any stale queued frames from before the seek
        for q in (self.video_queue, self.audio_queue):
            with q.mutex:
                q.queue.clear()

    def _push_video_frame(self, frame):
        if frame.pts is None:
            return
        pts_seconds = float(frame.pts * self.video_stream.time_base)
        while not self.stop_flag.is_set():
            try:
                self.video_queue.put((pts_seconds, frame), timeout=0.2)
                return
            except queue.Full:
                continue

    def _push_audio_frame(self, frame):
        if frame.pts is None:
            return
        pts_seconds = float(frame.pts * self.audio_stream.time_base)
        samples = frame.to_ndarray()  # shape: (channels, n) or (1, n) planar-merged by PyAV
        samples = self._normalize_audio(samples, frame)
        while not self.stop_flag.is_set():
            try:
                self.audio_queue.put((pts_seconds, samples), timeout=0.2)
                return
            except queue.Full:
                continue

    @staticmethod
    def _normalize_audio(samples, frame):
        """Convert whatever PyAV hands back into float32, shape (n_samples, channels)."""
        arr = samples.astype(np.float32)
        if arr.ndim == 2 and arr.shape[0] <= 8:
            arr = arr.T  # (channels, n) -> (n, channels)
        if arr.dtype != np.float32:
            arr = arr.astype(np.float32)
        # Common PCM ints come through as int16 sometimes depending on format; normalize range
        if np.issubdtype(samples.dtype, np.integer):
            maxval = np.iinfo(samples.dtype).max
            arr = arr / maxval
        return arr

    # ------------------------------------------------------------ audio output
    def _start_audio_output(self):
        self._audio_leftover = np.zeros((0, self._channels), dtype=np.float32)

        def callback(outdata, frames, time_info, status):
            if self.paused.is_set() or self.stop_flag.is_set():
                outdata.fill(0)
                return

            needed = frames
            chunks = [self._audio_leftover]
            have = self._audio_leftover.shape[0]

            while have < needed:
                try:
                    pts, samples = self.audio_queue.get_nowait()
                    with self._audio_clock_lock:
                        self._audio_clock = pts
                    if samples.shape[1] != self._channels:
                        samples = samples[:, :self._channels] if samples.shape[1] > self._channels \
                            else np.tile(samples, (1, self._channels))
                    chunks.append(samples)
                    have += samples.shape[0]
                except queue.Empty:
                    break

            block = np.concatenate(chunks, axis=0) if len(chunks) > 1 else chunks[0]
            if block.shape[0] >= needed:
                out_block = block[:needed]
                self._audio_leftover = block[needed:]
            else:
                pad = np.zeros((needed - block.shape[0], self._channels), dtype=np.float32)
                out_block = np.concatenate([block, pad], axis=0)
                self._audio_leftover = np.zeros((0, self._channels), dtype=np.float32)

            vol = 0.0 if self.muted else self.volume
            outdata[:] = out_block * vol

        self._audio_out_stream = sd.OutputStream(
            samplerate=self._sample_rate,
            channels=self._channels,
            dtype="float32",
            callback=callback,
            blocksize=1024,
        )
        self._audio_out_stream.start()

    # ------------------------------------------------------------ video pull
    def get_next_video_frame(self):
        """
        Pull the next video frame if the master clock says it's time to show it.
        Returns a numpy RGB array, or None if nothing is ready yet.
        If several queued frames are already due, drops the stale ones and
        keeps only the most recent — this keeps video locked to the audio
        clock instead of drifting behind.
        """
        with self.video_queue.mutex:
            dq = self.video_queue.queue  # underlying deque, protected by the mutex
            if not dq:
                return None

            clock = self.get_clock()
            if dq[0][0] > clock + 0.001:
                return None  # earliest queued frame isn't due yet

            chosen = None
            while dq and dq[0][0] <= clock + 0.001:
                _, chosen = dq.popleft()

        if chosen is None:
            return None
        return chosen.to_ndarray(format="rgb24")

    def is_finished(self):
        return self.ended.is_set() and self.video_queue.empty() and self.audio_queue.empty()
