"""
Headless sanity test for engine.py — verifies decode, queueing, clock
progression, and seeking work, without needing a display or audio device.
It monkeypatches sounddevice.OutputStream so it runs in a CI/sandbox
environment with no real audio hardware.
"""

import time
import types
import sys

import numpy as np

# ---- stub out sounddevice so this runs without a real audio device ----
import sounddevice as sd

class FakeStream:
    def __init__(self, samplerate, channels, dtype, callback, blocksize):
        self.callback = callback
        self.channels = channels
        self.blocksize = blocksize
        self._running = False

    def start(self):
        self._running = True

    def stop(self):
        self._running = False

    def close(self):
        pass

    def pump(self, n=50):
        """Manually invoke the audio callback n times, like a real device would."""
        outdata = np.zeros((self.blocksize, self.channels), dtype=np.float32)
        for _ in range(n):
            self.callback(outdata, self.blocksize, None, None)

sd.OutputStream = FakeStream
# -------------------------------------------------------------------------

from engine import MediaEngine

def run_test(path):
    print(f"\n=== Testing {path} ===")
    engine = MediaEngine(path)
    print(f"Duration: {engine.duration:.2f}s  "
          f"video={'yes' if engine.video_stream else 'no'}  "
          f"audio={'yes' if engine.audio_stream else 'no'}")

    engine.start()
    engine.play()

    # Let the demux thread fill queues
    time.sleep(0.5)
    print(f"Queued after 0.5s: video={engine.video_queue.qsize()} audio={engine.audio_queue.qsize()}")

    # Manually pump fake audio device to advance the audio clock
    if engine.audio_stream:
        engine._audio_out_stream.pump(n=20)
        print(f"Clock after pumping audio: {engine.get_clock():.3f}s")

    # Pull a few video frames
    got_frames = 0
    for _ in range(5):
        frame = engine.get_next_video_frame()
        if frame is not None:
            got_frames += 1
            assert frame.ndim == 3 and frame.shape[2] == 3, "expected RGB frame"
        if engine.audio_stream:
            engine._audio_out_stream.pump(n=5)
        time.sleep(0.05)
    print(f"Video frames retrieved: {got_frames}")

    # Test pause/play
    engine.pause()
    clock_before = engine.get_clock()
    time.sleep(0.3)
    clock_after = engine.get_clock()
    assert abs(clock_after - clock_before) < 0.01, "clock should not advance while paused"
    print(f"Pause holds clock steady: {clock_before:.3f}s -> {clock_after:.3f}s  OK")

    # Test seek
    engine.play()
    engine.seek(3.0)
    time.sleep(0.3)
    clock_now = engine.get_clock()
    print(f"Clock after seeking to 3.0s: {clock_now:.3f}s")
    assert 2.5 <= clock_now <= 4.0, f"seek landed far off target: {clock_now}"

    engine.stop()
    print("Stopped cleanly. TEST PASSED")


if __name__ == "__main__":
    run_test("test1.mp4")
    run_test("test2.mp4")
    print("\nAll tests passed.")
