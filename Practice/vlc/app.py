"""
app.py — Mini FFmpeg Player, full GUI edition.

No command line arguments needed. Launch it and:
  - Drag & drop video/audio files straight onto the window, or
  - Click the gallery / video icons on the left rail to pick media through a
    native file dialog.

Everything else — play/pause, seek, volume, mute, next/previous, playlist
management — is controlled entirely from the window. Built on the same
MediaEngine (PyAV + sounddevice) as before; this file is the UI layer only.
The visual skin below matches a dark "car head-unit" aesthetic (teal/black
diagonal background, amber accents, glass panels, animated equalizer) but
none of the underlying player behavior has changed.

Run:
  python app.py
(or double-click run.pyw on Windows / run.command on macOS — see README)
"""

import math
import os
import random
import sys
import threading
import time
import tkinter as tk
from datetime import datetime
from tkinter import filedialog

import pygame
import pygame.gfxdraw

try:
    # Only available on pygame 2.x (SDL2 backend). Used to give the borderless
    # window real minimize/maximize/move behavior since removing the native
    # title bar also removes the OS-provided controls for those.
    from pygame._sdl2.video import Window as _SDLWindow
except Exception:
    _SDLWindow = None

from engine import MediaEngine

# ----------------------------------------------------------------------
# Design tokens — dark teal/black head-unit theme with amber accent
# ----------------------------------------------------------------------
BG_TOP = (7, 12, 15)            # background gradient, top
BG_BOTTOM = (13, 24, 27)        # background gradient, bottom
BG_DIAG = (22, 46, 50)          # diagonal teal streak color
BG_DIAG_2 = (10, 18, 21)

GLASS = (24, 34, 38)            # glass panel fill
GLASS_LIGHT = (34, 47, 52)      # glass panel fill, lighter (hover/active)
GLASS_BORDER = (70, 90, 92)     # subtle panel border
GLASS_BORDER_SOFT = (46, 60, 63)

TEXT = (240, 242, 240)
TEXT_MUTED = (150, 165, 165)
TEXT_FAINT = (95, 110, 112)

ACCENT = (232, 140, 42)         # amber / orange — signature accent
ACCENT_DIM = (140, 88, 34)
ACCENT_GLOW = (255, 175, 90)
DANGER = (214, 92, 92)

EQ_BAR = (214, 214, 214)
EQ_BAR_DIM = (90, 98, 100)
EQ_GLOW = (196, 70, 40)

SUPPORTED_EXTENSIONS = (
    ".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv", ".wmv", ".m4v",
    ".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a",
)

FONT_CANDIDATES = ["Segoe UI", "Inter", "Helvetica Neue", "Arial", "DejaVu Sans"]

RAIL_W = 96             # left icon rail width
TOP_H = 200               # top zone: window controls + now-playing card + clock/temp cards
BOTTOM_H = 190            # bottom zone: seek row + transport row
PLAYLIST_W = 260         # slide-out playlist panel width

# NOTE: the temperature card is purely decorative (there is no weather data
# source wired into this app) — it mirrors the layout of the reference
# design but always shows a static placeholder value.
TEMP_DISPLAY = "24"


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_color(c1, c2, t):
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))


def rounded_rect(surface, rect, color, radius=8, width=0):
    pygame.draw.rect(surface, color, rect, width=width, border_radius=radius)


def rounded_rect_alpha(surface, rect, color, alpha, radius=12, width=0):
    """Draw a rounded rect with alpha blending onto `surface` (any size)."""
    rect = pygame.Rect(rect)
    tmp = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(tmp, (*color, alpha), tmp.get_rect(), width=width, border_radius=radius)
    surface.blit(tmp, rect.topleft)


class Anim:
    """A simple 0..1 value that eases toward a target each frame (hover states, etc.)."""
    def __init__(self, speed=10.0):
        self.value = 0.0
        self.target = 0.0
        self.speed = speed

    def set_target(self, t):
        self.target = t

    def update(self, dt):
        self.value += (self.target - self.value) * min(1.0, dt * self.speed)


# ----------------------------------------------------------------------
# Background: diagonal teal/black gradient panel, like the reference image
# ----------------------------------------------------------------------
def draw_background(surf, w, h):
    # vertical gradient base
    steps = 48
    for i in range(steps):
        t = i / (steps - 1)
        color = lerp_color(BG_TOP, BG_BOTTOM, t)
        y0 = int(h * i / steps)
        y1 = int(h * (i + 1) / steps) + 1
        pygame.draw.rect(surf, color, (0, y0, w, y1 - y0))

    # soft radial-ish glow near top center (behind now-playing card)
    glow = pygame.Surface((w, h), pygame.SRCALPHA)
    cx, cy, r = w // 2, 40, int(w * 0.35)
    for i in range(6, 0, -1):
        a = int(10 * i)
        pygame.gfxdraw.filled_circle(glow, cx, cy, int(r * i / 6), (ACCENT_GLOW[0], ACCENT_GLOW[1], ACCENT_GLOW[2], a))
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # diagonal streaks (teal wedges), left and right, echoing the reference art
    diag = pygame.Surface((w, h), pygame.SRCALPHA)
    def wedge(x0, alpha, wid, tilt, color):
        pts = [(x0, 0), (x0 + wid, 0), (x0 + wid + tilt, h), (x0 + tilt, h)]
        pygame.draw.polygon(diag, (*color, alpha), pts)
    wedge(int(w * 0.08), 26, int(w * 0.10), int(w * 0.18), BG_DIAG)
    wedge(int(w * 0.24), 16, int(w * 0.05), int(w * 0.12), BG_DIAG)
    wedge(int(w * 0.62), 20, int(w * 0.09), -int(w * 0.16), BG_DIAG)
    wedge(int(w * 0.80), 14, int(w * 0.05), -int(w * 0.10), BG_DIAG)
    surf.blit(diag, (0, 0))


# ----------------------------------------------------------------------
# Vector icon drawing (crisp, anti-aliased, theme-colored — no image assets)
# ----------------------------------------------------------------------
def draw_play_icon(surf, cx, cy, size, color):
    pts = [(cx - size * 0.32, cy - size * 0.48),
           (cx - size * 0.32, cy + size * 0.48),
           (cx + size * 0.5, cy)]
    pygame.gfxdraw.filled_polygon(surf, pts, color)
    pygame.gfxdraw.aapolygon(surf, pts, color)


def draw_pause_icon(surf, cx, cy, size, color):
    bar_w = size * 0.2
    gap = size * 0.14
    for dx in (-gap - bar_w / 2, gap + bar_w / 2):
        rect = pygame.Rect(0, 0, bar_w, size * 0.9)
        rect.center = (cx + dx, cy)
        rounded_rect(surf, rect, color, radius=int(bar_w * 0.3))


def draw_skip_icon(surf, cx, cy, size, color, forward=True):
    """Single-bar skip (⏮ / ⏭) — jumps to previous / next track."""
    d = 1 if forward else -1
    tri = [(cx - d * size * 0.42, cy - size * 0.42),
           (cx - d * size * 0.42, cy + size * 0.42),
           (cx + d * size * 0.16, cy)]
    pygame.gfxdraw.filled_polygon(surf, tri, color)
    pygame.gfxdraw.aapolygon(surf, tri, color)
    bar_rect = pygame.Rect(0, 0, size * 0.12, size * 0.86)
    bar_rect.center = (cx + d * size * 0.4, cy)
    rounded_rect(surf, bar_rect, color, radius=2)


def draw_seek_icon(surf, cx, cy, size, color, forward=True):
    """Double-triangle rewind / fast-forward (◀◀ / ▶▶) — seeks +/-10s."""
    d = 1 if forward else -1
    for off in (-0.28, 0.16):
        ox = cx + d * off * size
        tri = [(ox - d * size * 0.26, cy - size * 0.4),
               (ox - d * size * 0.26, cy + size * 0.4),
               (ox + d * size * 0.26, cy)]
        pygame.gfxdraw.filled_polygon(surf, tri, color)
        pygame.gfxdraw.aapolygon(surf, tri, color)


def draw_speaker_icon(surf, cx, cy, size, color, muted=False, volume=1.0):
    body = [
        (cx - size * 0.5, cy - size * 0.18),
        (cx - size * 0.2, cy - size * 0.18),
        (cx + size * 0.15, cy - size * 0.5),
        (cx + size * 0.15, cy + size * 0.5),
        (cx - size * 0.2, cy + size * 0.18),
        (cx - size * 0.5, cy + size * 0.18),
    ]
    pygame.gfxdraw.filled_polygon(surf, body, color)
    pygame.gfxdraw.aapolygon(surf, body, color)
    if muted:
        p1 = (cx + size * 0.28, cy - size * 0.28)
        p2 = (cx + size * 0.62, cy + size * 0.28)
        pygame.draw.line(surf, DANGER, p1, p2, 3)
        pygame.draw.line(surf, DANGER, (p1[0], p2[1]), (p2[0], p1[1]), 3)
    else:
        waves = 1 if volume < 0.5 else 2
        for i in range(waves):
            r = size * (0.3 + i * 0.18)
            rect = pygame.Rect(0, 0, r * 2, r * 2)
            rect.center = (cx + size * 0.1, cy)
            pygame.gfxdraw.arc(surf, rect.centerx, rect.centery, int(r), -35, 35, color)


def draw_image_icon(surf, cx, cy, size, color):
    """Gallery / picture icon."""
    rect = pygame.Rect(0, 0, size, size * 0.78)
    rect.center = (cx, cy)
    pygame.draw.rect(surf, color, rect, width=2, border_radius=4)
    pygame.gfxdraw.aacircle(surf, int(cx - size * 0.2), int(cy - size * 0.16), int(size * 0.09), color)
    pygame.gfxdraw.filled_circle(surf, int(cx - size * 0.2), int(cy - size * 0.16), int(size * 0.09), color)
    pts = [(rect.left + 4, rect.bottom - 6),
           (cx - size * 0.05, cy + size * 0.02),
           (cx + size * 0.18, cy - size * 0.14),
           (rect.right - 4, rect.bottom - 6)]
    pygame.draw.lines(surf, color, False, pts, 2)


def draw_music_note_icon(surf, cx, cy, size, color):
    """Eighth-note icon."""
    stem_x = cx + size * 0.18
    top_y = cy - size * 0.48
    bot_y = cy + size * 0.28
    pygame.draw.line(surf, color, (stem_x, top_y), (stem_x, bot_y), max(2, int(size * 0.09)))
    flag = [(stem_x, top_y), (stem_x + size * 0.32, top_y + size * 0.18), (stem_x, top_y + size * 0.34)]
    pygame.gfxdraw.filled_polygon(surf, flag, color)
    pygame.gfxdraw.aapolygon(surf, flag, color)
    r = size * 0.17
    for dx in (-0.02,):
        nx = stem_x + dx * size - r * 0.7
        pygame.gfxdraw.filled_ellipse(surf, int(nx), int(bot_y), int(r), int(r * 0.78), color)
        pygame.gfxdraw.aaellipse(surf, int(nx), int(bot_y), int(r), int(r * 0.78), color)


def draw_video_icon(surf, cx, cy, size, color):
    """Rounded frame with a play triangle inside — used for the 'open files' rail icon."""
    rect = pygame.Rect(0, 0, size, size * 0.86)
    rect.center = (cx, cy)
    pygame.draw.rect(surf, color, rect, width=2, border_radius=5)
    draw_play_icon(surf, cx + 1, cy, size * 0.42, color)


def draw_sliders_icon(surf, cx, cy, size, color):
    xs = [cx - size * 0.32, cx, cx + size * 0.32]
    knob_y = [cy - size * 0.15, cy + size * 0.22, cy - size * 0.3]
    for x, ky in zip(xs, knob_y):
        pygame.draw.line(surf, color, (x, cy - size * 0.48), (x, cy + size * 0.48), 2)
        pygame.gfxdraw.filled_circle(surf, int(x), int(ky), int(size * 0.09), color)
        pygame.gfxdraw.aacircle(surf, int(x), int(ky), int(size * 0.09), color)


def draw_chat_icon(surf, cx, cy, size, color):
    rect = pygame.Rect(0, 0, size, size * 0.72)
    rect.center = (cx, cy - size * 0.06)
    pygame.draw.rect(surf, color, rect, width=2, border_radius=6)
    tail = [(cx - size * 0.18, rect.bottom - 1), (cx - size * 0.04, rect.bottom - 1), (cx - size * 0.22, rect.bottom + size * 0.16)]
    pygame.gfxdraw.filled_polygon(surf, tail, color)
    pygame.gfxdraw.aapolygon(surf, tail, color)


def draw_gear_icon(surf, cx, cy, size, color):
    r_out = size * 0.42
    r_in = size * 0.24
    teeth = 8
    for i in range(teeth):
        a0 = (2 * math.pi / teeth) * i
        a1 = a0 + (2 * math.pi / teeth) * 0.5
        for a in (a0, a1):
            x1 = cx + math.cos(a) * r_out
            y1 = cy + math.sin(a) * r_out
            x2 = cx + math.cos(a) * (r_out + size * 0.12)
            y2 = cy + math.sin(a) * (r_out + size * 0.12)
            pygame.draw.line(surf, color, (x1, y1), (x2, y2), 2)
    pygame.gfxdraw.aacircle(surf, int(cx), int(cy), int(r_out), color)
    pygame.gfxdraw.aacircle(surf, int(cx), int(cy), int(r_in), color)


def draw_star_icon(surf, cx, cy, size, color, filled=False):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = size * 0.5 if i % 2 == 0 else size * 0.22
        pts.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
    if filled:
        pygame.gfxdraw.filled_polygon(surf, pts, color)
    pygame.gfxdraw.aapolygon(surf, pts, color)


def draw_repeat_icon(surf, cx, cy, size, color):
    r = size * 0.38
    rect_top = pygame.Rect(0, 0, r * 2, r * 2)
    rect_top.center = (cx, cy)
    pygame.gfxdraw.arc(surf, cx, cy, int(r), -160, 80, color)
    pygame.gfxdraw.arc(surf, cx, cy, int(r), 20, 260, color)
    a1 = math.radians(80)
    tip1 = (cx + math.cos(a1) * r, cy + math.sin(a1) * r)
    arrow1 = [(tip1[0] - size * 0.14, tip1[1] - size * 0.08),
              (tip1[0] + size * 0.1, tip1[1] - size * 0.02),
              (tip1[0] - size * 0.04, tip1[1] + size * 0.16)]
    pygame.gfxdraw.filled_polygon(surf, arrow1, color)
    a2 = math.radians(260)
    tip2 = (cx + math.cos(a2) * r, cy + math.sin(a2) * r)
    arrow2 = [(tip2[0] + size * 0.14, tip2[1] + size * 0.08),
              (tip2[0] - size * 0.1, tip2[1] + size * 0.02),
              (tip2[0] + size * 0.04, tip2[1] - size * 0.16)]
    pygame.gfxdraw.filled_polygon(surf, arrow2, color)


def draw_restore_icon(surf, cx, cy, size, color):
    """Circular 'undo' arrow."""
    r = size * 0.4
    pygame.gfxdraw.arc(surf, cx, cy, int(r), -210, 150, color)
    a = math.radians(150)
    tip = (cx + math.cos(a) * r, cy + math.sin(a) * r)
    arrow = [(tip[0] - size * 0.02, tip[1] - size * 0.18),
             (tip[0] + size * 0.18, tip[1] + size * 0.02),
             (tip[0] - size * 0.14, tip[1] + size * 0.12)]
    pygame.gfxdraw.filled_polygon(surf, arrow, color)


def draw_folder_icon(surf, cx, cy, size, color):
    body = pygame.Rect(0, 0, size, size * 0.72)
    body.center = (cx, cy + size * 0.06)
    rounded_rect(surf, body, color, radius=3)
    tab = pygame.Rect(0, 0, size * 0.45, size * 0.22)
    tab.midleft = (body.left + 2, body.top)
    rounded_rect(surf, tab, color, radius=3)


def draw_minimize_icon(surf, cx, cy, size, color):
    pygame.draw.line(surf, color, (cx - size * 0.32, cy + size * 0.02), (cx + size * 0.32, cy + size * 0.02), 2)


def draw_maximize_icon(surf, cx, cy, size, color, is_maximized=False):
    if not is_maximized:
        rect = pygame.Rect(0, 0, size * 0.56, size * 0.56)
        rect.center = (cx, cy)
        pygame.draw.rect(surf, color, rect, width=2, border_radius=2)
    else:
        back = pygame.Rect(0, 0, size * 0.5, size * 0.5)
        back.center = (cx + size * 0.09, cy - size * 0.09)
        pygame.draw.rect(surf, color, back, width=2, border_radius=2)
        front = pygame.Rect(0, 0, size * 0.5, size * 0.5)
        front.center = (cx - size * 0.09, cy + size * 0.09)
        pygame.draw.rect(surf, GLASS, front, border_radius=2)
        pygame.draw.rect(surf, color, front, width=2, border_radius=2)


def draw_close_icon(surf, cx, cy, size, color):
    d = size * 0.28
    pygame.draw.line(surf, color, (cx - d, cy - d), (cx + d, cy + d), 2)
    pygame.draw.line(surf, color, (cx - d, cy + d), (cx + d, cy - d), 2)


def draw_chevron(surf, cx, cy, size, color, direction="left"):
    d = -1 if direction == "left" else 1
    pts = [(cx + d * size * 0.2, cy - size * 0.4),
           (cx - d * size * 0.25, cy),
           (cx + d * size * 0.2, cy + size * 0.4)]
    pygame.draw.lines(surf, color, False, pts, 3)


# ----------------------------------------------------------------------
# Widgets
# ----------------------------------------------------------------------
class IconButton:
    def __init__(self, rect, icon_fn, on_click, radius=None, filled=False, ring=False, danger=False):
        self.rect = pygame.Rect(rect)
        self.icon_fn = icon_fn
        self.on_click = on_click
        self.hover = Anim(speed=12)
        self.radius = radius if radius is not None else self.rect.width // 2
        self.filled = filled
        self.ring = ring  # draws a persistent accent ring (e.g. "active" rail icon)
        self.danger = danger  # hover tints red instead of amber (close button)
        self.visible = True
        self.enabled = True

    def update(self, dt, mouse_pos):
        target = 1.0 if (self.visible and self.enabled and self.rect.collidepoint(mouse_pos)) else 0.0
        self.hover.set_target(target)
        self.hover.update(dt)

    def draw(self, surf):
        if not self.visible:
            return
        cx, cy = self.rect.center
        if self.filled:
            glow_r = int(self.radius * (1.0 + 0.18 * self.hover.value))
            glow = pygame.Surface((glow_r * 3, glow_r * 3), pygame.SRCALPHA)
            pygame.gfxdraw.filled_circle(glow, glow_r * 3 // 2, glow_r * 3 // 2, glow_r + 10,
                                          (*ACCENT_GLOW, 55))
            surf.blit(glow, (cx - glow_r * 3 // 2, cy - glow_r * 3 // 2), special_flags=pygame.BLEND_RGBA_ADD)
            bg = lerp_color(ACCENT_DIM, ACCENT, 0.55 + 0.45 * self.hover.value)
            pygame.gfxdraw.filled_circle(surf, cx, cy, self.radius, bg)
            pygame.gfxdraw.aacircle(surf, cx, cy, self.radius, bg)
            icon_color = (20, 16, 10)
        else:
            if self.ring:
                pygame.gfxdraw.aacircle(surf, cx, cy, self.radius, ACCENT)
                pygame.gfxdraw.aacircle(surf, cx, cy, self.radius - 1, ACCENT)
            if self.hover.value > 0.01:
                hover_fill = DANGER if self.danger else GLASS_LIGHT
                bg = lerp_color(GLASS, hover_fill, self.hover.value)
                pygame.gfxdraw.filled_circle(surf, cx, cy, self.radius, bg)
                pygame.gfxdraw.aacircle(surf, cx, cy, self.radius, bg)
            base_color = ACCENT if self.ring else TEXT_MUTED
            hover_target = TEXT if not self.danger else (255, 255, 255)
            icon_color = lerp_color(base_color, hover_target, self.hover.value) if self.enabled else TEXT_FAINT
        self.icon_fn(surf, cx, cy, self.radius * 1.05, icon_color)

    def handle_click(self, pos):
        if self.visible and self.enabled and self.rect.collidepoint(pos):
            self.on_click()
            return True
        return False


class Slider:
    """Horizontal pill-shaped seek bar, theme-styled with a soft thumb."""
    def __init__(self, rect, get_fraction, on_seek, track_color=GLASS_BORDER, fill_color=TEXT):
        self.rect = pygame.Rect(rect)
        self.get_fraction = get_fraction
        self.on_seek = on_seek
        self.track_color = track_color
        self.fill_color = fill_color
        self.dragging = False
        self.hover = Anim(speed=14)

    def update(self, dt, mouse_pos):
        hit = self.rect.inflate(0, 14).collidepoint(mouse_pos)
        self.hover.set_target(1.0 if (hit or self.dragging) else 0.0)
        self.hover.update(dt)

    def draw(self, surf):
        frac = max(0.0, min(1.0, self.get_fraction()))
        thickness = self.rect.height
        track_rect = pygame.Rect(self.rect.x, self.rect.centery - thickness // 2, self.rect.width, thickness)
        rounded_rect(surf, track_rect, self.track_color, radius=thickness // 2)
        fill_w = int(self.rect.width * frac)
        if fill_w > 0:
            fill_rect = pygame.Rect(self.rect.x, self.rect.centery - thickness // 2, fill_w, thickness)
            rounded_rect(surf, fill_rect, self.fill_color, radius=thickness // 2)
        if self.hover.value > 0.05:
            thumb_x = self.rect.x + fill_w
            r = int(lerp(thickness * 0.6, thickness * 1.1, self.hover.value))
            pygame.gfxdraw.filled_circle(surf, thumb_x, self.rect.centery, r, ACCENT)
            pygame.gfxdraw.aacircle(surf, thumb_x, self.rect.centery, r, ACCENT)

    def handle_mouse_down(self, pos):
        if self.rect.inflate(0, 14).collidepoint(pos):
            self.dragging = True
            self._seek_to(pos)
            return True
        return False

    def handle_mouse_up(self):
        self.dragging = False

    def handle_mouse_move(self, pos):
        if self.dragging:
            self._seek_to(pos)

    def _seek_to(self, pos):
        frac = (pos[0] - self.rect.x) / max(1, self.rect.width)
        self.on_seek(max(0.0, min(1.0, frac)))


class TextButton:
    def __init__(self, rect, label, on_click, icon_fn=None):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.on_click = on_click
        self.icon_fn = icon_fn
        self.hover = Anim(speed=12)

    def update(self, dt, mouse_pos):
        self.hover.set_target(1.0 if self.rect.collidepoint(mouse_pos) else 0.0)
        self.hover.update(dt)

    def draw(self, surf, font):
        bg = lerp_color(GLASS, GLASS_LIGHT, self.hover.value)
        rounded_rect(surf, self.rect, bg, radius=8)
        rounded_rect(surf, self.rect, lerp_color(GLASS_BORDER, ACCENT_DIM, self.hover.value), radius=8, width=1)
        text_color = lerp_color(TEXT_MUTED, TEXT, self.hover.value)
        pad = 14
        x = self.rect.x + pad
        if self.icon_fn:
            self.icon_fn(surf, x + 8, self.rect.centery, 16, text_color)
            x += 26
        label_surf = font.render(self.label, True, text_color)
        surf.blit(label_surf, (x, self.rect.centery - label_surf.get_height() // 2))

    def handle_click(self, pos):
        if self.rect.collidepoint(pos):
            self.on_click()
            return True
        return False


# ----------------------------------------------------------------------
# Main application
# ----------------------------------------------------------------------
class PlayerApp:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Mediastage")

        # The reference design has no native title bar, so we go borderless
        # and draw our own minimize / maximize / close controls + drag-to-move.
        # If the SDL2 Window wrapper isn't available (older pygame), we fall
        # back to a normal OS-framed window so the app still has working
        # window controls either way.
        self._windowed_size = (1040, 760)
        self._maximized = False
        self._win_dragging = False
        self._drag_last_mouse = (0, 0)
        self._sdl_window = None
        self.frameless = _SDLWindow is not None

        flags = pygame.RESIZABLE | (pygame.NOFRAME if self.frameless else 0)
        self.screen = pygame.display.set_mode(self._windowed_size, flags)

        if self.frameless:
            try:
                self._sdl_window = _SDLWindow.from_display_module()
            except Exception:
                # couldn't get a handle to control the borderless window —
                # recreate it with a normal OS frame instead of leaving the
                # person with an unmovable, uncontrollable window.
                self._sdl_window = None
                self.frameless = False
                self.screen = pygame.display.set_mode(self._windowed_size, pygame.RESIZABLE)

        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.SysFont(FONT_CANDIDATES, 20, bold=True)
        self.font_subtitle = pygame.font.SysFont(FONT_CANDIDATES, 13)
        self.font_body = pygame.font.SysFont(FONT_CANDIDATES, 14)
        self.font_small = pygame.font.SysFont(FONT_CANDIDATES, 12)
        self.font_clock = pygame.font.SysFont(FONT_CANDIDATES, 26, bold=True)
        self.font_temp = pygame.font.SysFont(FONT_CANDIDATES, 26, bold=True)
        self.font_temp_unit = pygame.font.SysFont(FONT_CANDIDATES, 13)

        self.playlist = []          # list of file paths
        self.current_index = -1
        self.engine = None
        self.is_playing = False
        self.video_surface_cache = None
        self.sidebar_open = False           # playlist slide-out panel (starts closed)
        self.sidebar_anim = Anim(speed=9)
        self._tk_root = None  # lazily created for native file dialogs

        # equalizer animation state (purely decorative, matches reference art)
        self._eq_bar_count = 44
        self._eq_seeds = [random.uniform(0, 6.28) for _ in range(self._eq_bar_count)]
        self._eq_time = 0.0

        self._build_widgets()

    # ------------------------------------------------------------ setup
    def _build_widgets(self):
        self.play_btn = IconButton((0, 0, 64, 64), draw_play_icon, self.toggle_play, filled=True)
        self.prev_btn = IconButton((0, 0, 42, 42), lambda s, x, y, sz, c: draw_skip_icon(s, x, y, sz, c, False),
                                    self.previous_track)
        self.next_btn = IconButton((0, 0, 42, 42), lambda s, x, y, sz, c: draw_skip_icon(s, x, y, sz, c, True),
                                    self.next_track)
        self.rewind_btn = IconButton((0, 0, 42, 42), lambda s, x, y, sz, c: draw_seek_icon(s, x, y, sz, c, False),
                                      self.seek_back)
        self.forward_btn = IconButton((0, 0, 42, 42), lambda s, x, y, sz, c: draw_seek_icon(s, x, y, sz, c, True),
                                       self.seek_forward)
        self.mute_btn = IconButton((0, 0, 40, 40), self._draw_speaker_for_button, self.toggle_mute, filled=True)

        # left icon rail
        self.rail_gallery_btn = IconButton((0, 0, 44, 44), draw_image_icon, self.open_folder_dialog)
        self.rail_music_btn = IconButton((0, 0, 44, 44), draw_music_note_icon, self.toggle_sidebar, ring=True)
        self.rail_video_btn = IconButton((0, 0, 44, 44), draw_video_icon, self.open_files_dialog)

        # bottom-left decorative / utility icons
        self.sliders_btn = IconButton((0, 0, 34, 34), draw_sliders_icon, self.toggle_sidebar)
        self.chat_btn = IconButton((0, 0, 34, 34), draw_chat_icon, lambda: None)
        self.gear_btn = IconButton((0, 0, 34, 34), draw_gear_icon, lambda: None)

        # bottom-right decorative icons
        self.star_btn = IconButton((0, 0, 34, 34), lambda s, x, y, sz, c: draw_star_icon(s, x, y, sz, c), lambda: None)
        self.repeat_btn = IconButton((0, 0, 34, 34), draw_repeat_icon, lambda: None)
        self.restore_btn = IconButton((0, 0, 34, 34), draw_restore_icon, lambda: None)

        self.open_files_btn_empty = TextButton((0, 0, 170, 44), "Open Files", self.open_files_dialog, draw_folder_icon)

        self.seek_slider = Slider((0, 0, 100, 6), self._get_seek_fraction, self._on_seek,
                                   track_color=GLASS_BORDER, fill_color=TEXT)

        # custom window controls (only shown/active when running borderless)
        self.min_btn = IconButton((0, 0, 24, 24), draw_minimize_icon, self.minimize_window)
        self.maxres_btn = IconButton((0, 0, 24, 24),
                                      lambda s, x, y, sz, c: draw_maximize_icon(s, x, y, sz, c, self._maximized),
                                      self.toggle_maximize)
        self.close_btn = IconButton((0, 0, 24, 24), draw_close_icon, self.close_window, danger=True)

        self.all_icon_buttons = [
            self.play_btn, self.prev_btn, self.next_btn, self.rewind_btn, self.forward_btn, self.mute_btn,
            self.rail_gallery_btn, self.rail_music_btn, self.rail_video_btn,
            self.sliders_btn, self.chat_btn, self.gear_btn,
            self.star_btn, self.repeat_btn, self.restore_btn,
            self.min_btn, self.maxres_btn, self.close_btn,
        ]
        self.all_text_buttons = [self.open_files_btn_empty]
        self.all_sliders = [self.seek_slider]

    def _draw_speaker_for_button(self, surf, cx, cy, size, color):
        muted = self.engine.muted if self.engine else False
        vol = self.engine.volume if self.engine else 1.0
        draw_speaker_icon(surf, cx, cy, size, color, muted=muted, volume=vol)

    # ------------------------------------------------------------ file dialogs
    def _get_tk_root(self):
        if self._tk_root is None:
            self._tk_root = tk.Tk()
            self._tk_root.withdraw()
        return self._tk_root

    def open_files_dialog(self):
        root = self._get_tk_root()
        paths = filedialog.askopenfilenames(
            parent=root, title="Open media",
            filetypes=[("Media files", " ".join("*" + e for e in SUPPORTED_EXTENSIONS)), ("All files", "*.*")]
        )
        if paths:
            self.add_files(list(paths), play_first=(self.current_index == -1))

    def open_folder_dialog(self):
        root = self._get_tk_root()
        folder = filedialog.askdirectory(parent=root, title="Open folder")
        if folder:
            found = []
            for name in sorted(os.listdir(folder)):
                if name.lower().endswith(SUPPORTED_EXTENSIONS):
                    found.append(os.path.join(folder, name))
            if found:
                self.add_files(found, play_first=(self.current_index == -1))

    def add_files(self, paths, play_first=False):
        start = len(self.playlist)
        self.playlist.extend(paths)
        if play_first:
            self.load_track(start)

    # ------------------------------------------------------------ track control
    def load_track(self, index):
        if self.engine:
            self.engine.stop()
            self.engine = None
        if not (0 <= index < len(self.playlist)):
            return
        self.current_index = index
        path = self.playlist[index]
        try:
            self.engine = MediaEngine(path)
        except Exception as e:
            print(f"[open error] {path}: {e}")
            return
        self.engine.start()
        self.engine.play()
        self.is_playing = True
        self.video_surface_cache = None

    def next_track(self):
        if not self.playlist:
            return
        self.load_track((self.current_index + 1) % len(self.playlist))

    def previous_track(self):
        if not self.playlist:
            return
        self.load_track((self.current_index - 1) % len(self.playlist))

    def toggle_play(self):
        if not self.engine:
            if self.playlist:
                self.load_track(0)
            else:
                self.open_files_dialog()
            return
        if self.is_playing:
            self.engine.pause()
            self.is_playing = False
        else:
            self.engine.play()
            self.is_playing = True

    def toggle_mute(self):
        if self.engine:
            self.engine.toggle_mute()

    def toggle_sidebar(self):
        self.sidebar_open = not self.sidebar_open
        self.sidebar_anim.set_target(1.0 if self.sidebar_open else 0.0)

    # ------------------------------------------------------------ window controls
    def minimize_window(self):
        try:
            if self._sdl_window:
                self._sdl_window.minimize()
            else:
                pygame.display.iconify()
        except Exception:
            pass

    def toggle_maximize(self):
        if self._sdl_window:
            try:
                if not self._maximized:
                    self._windowed_size = (self.w, self.h)
                    self._sdl_window.maximize()
                else:
                    self._sdl_window.restore()
                self._maximized = not self._maximized
                return
            except Exception:
                pass
        # fallback for environments without the SDL2 Window wrapper
        info = pygame.display.Info()
        flags = pygame.RESIZABLE | (pygame.NOFRAME if self.frameless else 0)
        if not self._maximized:
            self._windowed_size = (self.w, self.h)
            self.screen = pygame.display.set_mode((info.current_w, info.current_h), flags)
        else:
            self.screen = pygame.display.set_mode(self._windowed_size, flags)
        self._maximized = not self._maximized

    def close_window(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _start_window_drag(self, pos):
        if not self.frameless or self._maximized or not self._sdl_window:
            return
        self._win_dragging = True
        self._drag_last_mouse = pos

    def _drag_window(self, pos):
        if not self._win_dragging or not self._sdl_window:
            return
        dx = pos[0] - self._drag_last_mouse[0]
        dy = pos[1] - self._drag_last_mouse[1]
        if dx or dy:
            try:
                wx, wy = self._sdl_window.position
                self._sdl_window.position = (wx + dx, wy + dy)
            except Exception:
                pass
        self._drag_last_mouse = pos

    def seek_forward(self):
        if self.engine:
            self.engine.seek(self.engine.get_clock() + 10)

    def seek_back(self):
        if self.engine:
            self.engine.seek(self.engine.get_clock() - 10)

    def _get_seek_fraction(self):
        if self.engine and self.engine.duration:
            return self.engine.get_clock() / self.engine.duration
        return 0.0

    def _on_seek(self, frac):
        if self.engine and self.engine.duration:
            self.engine.seek(frac * self.engine.duration)

    # ------------------------------------------------------------ main loop
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self._handle_key(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_mouse_down(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    for s in self.all_sliders:
                        s.handle_mouse_up()
                    self._win_dragging = False
                elif event.type == pygame.MOUSEMOTION:
                    for s in self.all_sliders:
                        s.handle_mouse_move(event.pos)
                    self._drag_window(event.pos)
                elif event.type == pygame.DROPFILE:
                    self._handle_drop(event.file)

            self._auto_advance_if_ended()
            self._layout(self.screen.get_width(), self.screen.get_height())
            self._update(dt, mouse_pos)
            self._draw()
            pygame.display.flip()

        if self.engine:
            self.engine.stop()
        if self._tk_root:
            self._tk_root.destroy()
        pygame.quit()

    def _handle_key(self, key):
        if key == pygame.K_SPACE:
            self.toggle_play()
        elif key == pygame.K_m:
            self.toggle_mute()
        elif key == pygame.K_RIGHT:
            self.seek_forward()
        elif key == pygame.K_LEFT:
            self.seek_back()
        elif key == pygame.K_b:
            self.toggle_sidebar()

    def _handle_drop(self, path):
        if os.path.isdir(path):
            found = [os.path.join(path, n) for n in sorted(os.listdir(path))
                      if n.lower().endswith(SUPPORTED_EXTENSIONS)]
            self.add_files(found, play_first=(self.current_index == -1))
        elif path.lower().endswith(SUPPORTED_EXTENSIONS):
            self.add_files([path], play_first=(self.current_index == -1))

    def _handle_mouse_down(self, pos):
        for b in self.all_icon_buttons:
            if b.handle_click(pos):
                return
        for b in self.all_text_buttons:
            if b.handle_click(pos):
                return
        for s in self.all_sliders:
            if s.handle_mouse_down(pos):
                return
        # playlist row clicks
        if self.sidebar_open:
            for i, row_rect in enumerate(self._playlist_row_rects):
                if row_rect.collidepoint(pos):
                    self.load_track(i)
                    return
        # empty header strip — click-drag to move the (borderless) window
        if self.drag_zone_rect.collidepoint(pos):
            self._start_window_drag(pos)

    def _auto_advance_if_ended(self):
        if self.engine and self.engine.is_finished():
            self.next_track()

    # ------------------------------------------------------------ layout
    def _layout(self, w, h):
        self.w, self.h = w, h
        pad = 22

        self.rail_rect = pygame.Rect(pad, 22, RAIL_W - pad, h - 44)

        playlist_w = int(PLAYLIST_W * self.sidebar_anim.value)
        self.playlist_rect = pygame.Rect(RAIL_W + 6, TOP_H, playlist_w, h - TOP_H - BOTTOM_H - 10)

        stage_x = RAIL_W + 12 + playlist_w
        self.stage_rect = pygame.Rect(stage_x, TOP_H, w - stage_x - pad, h - TOP_H - BOTTOM_H)

        # rail icons, stacked vertically centered
        rail_cx = self.rail_rect.centerx
        rail_cy = self.rail_rect.centery
        self.rail_gallery_btn.rect.center = (rail_cx, rail_cy - 92)
        self.rail_music_btn.rect.center = (rail_cx, rail_cy)
        self.rail_video_btn.rect.center = (rail_cx, rail_cy + 92)

        # custom window controls, top-right corner (borderless window has no OS titlebar)
        ctrl_size, ctrl_gap = 22, 8
        ctrl_y = 14
        self.close_btn.rect.center = (w - pad - ctrl_size // 2, ctrl_y)
        self.maxres_btn.rect.center = (w - pad - ctrl_size - ctrl_gap - ctrl_size // 2, ctrl_y)
        self.min_btn.rect.center = (w - pad - (ctrl_size + ctrl_gap) * 2 - ctrl_size // 2, ctrl_y)
        # whole top strip is draggable to move the window, except over the controls
        self.drag_zone_rect = pygame.Rect(0, 0, w, 30)

        # top-right clock / temperature glass cards
        card_w, card_h = 120, 72
        top_cards_y = 34
        self.clock_card_rect = pygame.Rect(w - pad - card_w, top_cards_y, card_w, card_h)
        self.temp_card_rect = pygame.Rect(w - pad - card_w, top_cards_y + card_h + 10, card_w, card_h)

        # now-playing card, centered
        np_w, np_h = min(420, w - RAIL_W - card_w - pad * 3), 78
        self.now_playing_rect = pygame.Rect(0, 40, np_w, np_h)
        self.now_playing_rect.centerx = RAIL_W + (w - RAIL_W - card_w - pad * 2) // 2

        self.top_divider_y = TOP_H - 8
        self.bottom_divider_y = h - BOTTOM_H + 8

        # seek row
        seek_y = h - BOTTOM_H + 44
        self.mute_btn.rect.center = (w - pad - 26, seek_y)
        self.seek_slider.rect = pygame.Rect(RAIL_W + 6, seek_y - 3, w - RAIL_W - pad - 80, 6)

        # transport row
        controls_y = h - BOTTOM_H + 118
        center_x = w // 2
        self.play_btn.rect.center = (center_x, controls_y)
        self.prev_btn.rect.center = (center_x - 74, controls_y)
        self.next_btn.rect.center = (center_x + 74, controls_y)
        self.rewind_btn.rect.center = (center_x - 132, controls_y)
        self.forward_btn.rect.center = (center_x + 132, controls_y)

        left_group_x = RAIL_W + 40
        self.sliders_btn.rect.center = (left_group_x, controls_y)
        self.chat_btn.rect.center = (left_group_x + 46, controls_y)
        self.gear_btn.rect.center = (left_group_x + 92, controls_y)

        right_group_x = w - pad - 40
        self.star_btn.rect.center = (right_group_x - 92, controls_y)
        self.repeat_btn.rect.center = (right_group_x - 46, controls_y)
        self.restore_btn.rect.center = (right_group_x, controls_y)

        self.open_files_btn_empty.rect.center = (self.stage_rect.centerx, self.stage_rect.centery + 40)

        # playlist rows
        self._playlist_row_rects = []
        row_h = 40
        start_y = self.playlist_rect.y + 10
        for i in range(len(self.playlist)):
            self._playlist_row_rects.append(
                pygame.Rect(self.playlist_rect.x, start_y + i * row_h, self.playlist_rect.width, row_h))

    def _update(self, dt, mouse_pos):
        for b in self.all_icon_buttons:
            b.visible = True
            b.update(dt, mouse_pos)
        self.play_btn.icon_fn = draw_pause_icon if self.is_playing else draw_play_icon
        for b in self.all_text_buttons:
            b.update(dt, mouse_pos)
        for s in self.all_sliders:
            s.update(dt, mouse_pos)
        self.sidebar_anim.update(dt)
        self.rail_music_btn.ring = self.sidebar_open

        # window controls only matter (and should only intercept clicks) in borderless mode
        for b in (self.min_btn, self.maxres_btn, self.close_btn):
            b.visible = self.frameless
            b.enabled = self.frameless

        has_media = self.engine is not None
        self.prev_btn.enabled = has_media and len(self.playlist) > 1
        self.next_btn.enabled = has_media and len(self.playlist) > 1
        self.rewind_btn.enabled = has_media
        self.forward_btn.enabled = has_media
        self.mute_btn.enabled = has_media

        if self.is_playing:
            self._eq_time += dt

    # ------------------------------------------------------------ drawing
    def _draw(self):
        draw_background(self.screen, self.w, self.h)
        self._draw_now_playing_card()
        self._draw_info_card(self.clock_card_rect, datetime.now().strftime("%H:%M"), None)
        self._draw_info_card(self.temp_card_rect, TEMP_DISPLAY, "C")
        self._draw_rail()
        if self.sidebar_anim.value > 0.01:
            self._draw_playlist_panel()
        self._draw_divider(self.top_divider_y)
        self._draw_equalizer()
        self._draw_divider(self.bottom_divider_y)
        self._draw_seek_row()
        self._draw_transport_row()
        if self.frameless:
            self._draw_window_controls()

    def _draw_window_controls(self):
        self.min_btn.draw(self.screen)
        self.maxres_btn.draw(self.screen)
        self.close_btn.draw(self.screen)

    def _draw_divider(self, y):
        pygame.draw.line(self.screen, GLASS_BORDER_SOFT, (24, y), (self.w - 24, y), 1)
        glow_w = int(self.w * 0.32)
        cx = self.w // 2
        glow = pygame.Surface((glow_w, 3), pygame.SRCALPHA)
        for x in range(glow_w):
            t = 1 - abs((x / glow_w) - 0.5) * 2
            pygame.draw.line(glow, (*ACCENT, int(90 * t)), (x, 1), (x, 1))
        self.screen.blit(glow, (cx - glow_w // 2, y - 1))

    def _draw_rail(self):
        rounded_rect_alpha(self.screen, self.rail_rect, GLASS, 150, radius=28)
        rounded_rect(self.screen, self.rail_rect, GLASS_BORDER_SOFT, radius=28, width=1)
        self.rail_gallery_btn.draw(self.screen)
        self.rail_music_btn.draw(self.screen)
        self.rail_video_btn.draw(self.screen)

    def _draw_info_card(self, rect, big_text, unit):
        rounded_rect_alpha(self.screen, rect, GLASS, 150, radius=16)
        rounded_rect(self.screen, rect, GLASS_BORDER_SOFT, radius=16, width=1)
        font = self.font_clock if unit is None else self.font_temp
        text_surf = font.render(big_text, True, TEXT)
        tx = rect.centerx - text_surf.get_width() // 2 - (10 if unit else 0)
        ty = rect.centery - text_surf.get_height() // 2
        self.screen.blit(text_surf, (tx, ty))
        if unit:
            unit_surf = self.font_temp_unit.render(f"°{unit}", True, TEXT_MUTED)
            self.screen.blit(unit_surf, (tx + text_surf.get_width() + 3, ty + text_surf.get_height() - unit_surf.get_height() - 2))

    def _draw_now_playing_card(self):
        rect = self.now_playing_rect
        rounded_rect_alpha(self.screen, rect, GLASS, 165, radius=16)
        rounded_rect(self.screen, rect, GLASS_BORDER_SOFT, radius=16, width=1)

        thumb = pygame.Rect(rect.x + 8, rect.y + 8, rect.height - 16, rect.height - 16)
        rounded_rect(self.screen, thumb, GLASS_LIGHT, radius=10)
        rounded_rect(self.screen, thumb, ACCENT_DIM, radius=10, width=1)
        # simple orbiting-dot "media" glyph inside the thumbnail
        tcx, tcy = thumb.center
        pygame.gfxdraw.aacircle(self.screen, tcx, tcy, int(thumb.width * 0.28), TEXT_MUTED)
        pygame.gfxdraw.filled_circle(self.screen, tcx, tcy, int(thumb.width * 0.1), ACCENT)

        text_x = thumb.right + 14
        if self.engine and self.current_index >= 0:
            title = os.path.splitext(os.path.basename(self.playlist[self.current_index]))[0]
            subtitle = f"Track {self.current_index + 1} of {len(self.playlist)}"
        else:
            title = "The best world"
            subtitle = "Imaginary adventures" if not self.playlist else "Nothing loaded yet"

        title = self._truncate(title, self.font_title, rect.right - text_x - 12)
        title_surf = self.font_title.render(title, True, TEXT)
        self.screen.blit(title_surf, (text_x, rect.y + rect.height // 2 - title_surf.get_height() - 2))
        sub_surf = self.font_subtitle.render(subtitle, True, TEXT_MUTED)
        self.screen.blit(sub_surf, (text_x, rect.y + rect.height // 2 + 4))

    def _draw_playlist_panel(self):
        rect = self.playlist_rect
        if rect.width <= 4:
            return
        rounded_rect_alpha(self.screen, rect, GLASS, 190, radius=14)
        rounded_rect(self.screen, rect, GLASS_BORDER_SOFT, radius=14, width=1)

        prev_clip = self.screen.get_clip()
        self.screen.set_clip(rect)

        label = self.font_small.render(f"PLAYLIST — {len(self.playlist)}", True, TEXT_FAINT)
        self.screen.blit(label, (rect.x + 12, rect.y - 2))

        for i, row_rect in enumerate(self._playlist_row_rects):
            active = (i == self.current_index)
            if active:
                rounded_rect(self.screen, row_rect.inflate(-10, -6), GLASS_LIGHT, radius=8)
                accent_bar = pygame.Rect(row_rect.x + 4, row_rect.y + 6, 3, row_rect.height - 12)
                rounded_rect(self.screen, accent_bar, ACCENT, radius=2)
            name = os.path.basename(self.playlist[i])
            color = ACCENT if active else TEXT_MUTED
            text_surf = self.font_body.render(self._truncate(name, self.font_body, rect.width - 30), True, color)
            self.screen.blit(text_surf, (rect.x + 14, row_rect.centery - text_surf.get_height() // 2))

        if not self.playlist:
            empty = self.font_small.render("No files yet — use the rail icons", True, TEXT_FAINT)
            self.screen.blit(empty, (rect.x + 12, rect.y + 24))

        self.screen.set_clip(prev_clip)

    def _truncate(self, text, font, max_w):
        if max_w <= 0:
            return ""
        if font.size(text)[0] <= max_w:
            return text
        while text and font.size(text + "…")[0] > max_w:
            text = text[:-1]
        return text + "…"

    def _draw_equalizer(self):
        rect = self.stage_rect
        if rect.width <= 4:
            return

        # if a video is actually playing, show its frame instead of the fake EQ
        if self.engine:
            frame_rgb = self.engine.get_next_video_frame()
            if frame_rgb is not None:
                surf = pygame.image.frombuffer(
                    frame_rgb.tobytes(), (frame_rgb.shape[1], frame_rgb.shape[0]), "RGB"
                )
                self.video_surface_cache = surf
            if self.video_surface_cache and self.engine.video_stream is not None:
                sw, sh = self.video_surface_cache.get_size()
                avail_w, avail_h = rect.width - 20, rect.height - 20
                scale = min(avail_w / sw, avail_h / sh)
                new_size = (max(1, int(sw * scale)), max(1, int(sh * scale)))
                scaled = pygame.transform.smoothscale(self.video_surface_cache, new_size)
                x = rect.x + (rect.width - new_size[0]) // 2
                y = rect.y + (rect.height - new_size[1]) // 2
                self.screen.blit(scaled, (x, y))
                return

        if not self.playlist:
            self._draw_empty_state()
            return

        # decorative animated equalizer bars
        n = self._eq_bar_count
        gap = 4
        bar_w = max(3, (rect.width - gap * (n - 1)) / n)
        base_y = rect.bottom - 18
        max_h = rect.height - 30
        mid = n / 2

        for i in range(n):
            seed = self._eq_seeds[i]
            if self.is_playing:
                t = self._eq_time
                h = (0.5 + 0.5 * math.sin(t * 2.4 + seed) * math.sin(t * 0.9 + seed * 1.7)) 
                h = 0.15 + 0.85 * abs(h)
            else:
                h = 0.12 + 0.05 * math.sin(seed)
            bar_h = max(4, h * max_h)
            x = rect.x + i * (bar_w + gap)
            bar_rect = pygame.Rect(int(x), int(base_y - bar_h), int(bar_w), int(bar_h))
            dist = abs(i - mid) / mid
            color = lerp_color(EQ_BAR, EQ_BAR_DIM, dist * 0.5)
            rounded_rect(self.screen, bar_rect, color, radius=int(bar_w / 2))

        # warm glow along the baseline, echoing the reference art
        glow = pygame.Surface((rect.width, 24), pygame.SRCALPHA)
        for x in range(rect.width):
            t = 1 - abs((x / rect.width) - 0.5) * 2
            pygame.draw.line(glow, (*EQ_GLOW, int(70 * max(0, t) ** 2)), (x, 0), (x, 24))
        self.screen.blit(glow, (rect.x, base_y - 2), special_flags=pygame.BLEND_RGBA_ADD)

    def _draw_empty_state(self):
        rect = self.stage_rect
        cx, cy = rect.center
        pygame.gfxdraw.filled_circle(self.screen, cx, cy - 50, 30, GLASS_LIGHT)
        pygame.gfxdraw.aacircle(self.screen, cx, cy - 50, 30, GLASS_BORDER)
        draw_folder_icon(self.screen, cx, cy - 50, 26, ACCENT)

        title = self.font_title.render("Drop a video or audio file", True, TEXT)
        self.screen.blit(title, (cx - title.get_width() // 2, cy - 6))
        sub = self.font_small.render("or use the rail icons on the left", True, TEXT_FAINT)
        self.screen.blit(sub, (cx - sub.get_width() // 2, cy + 20))

        self.open_files_btn_empty.rect.center = (cx, cy + 66)
        self.open_files_btn_empty.draw(self.screen, self.font_body)

    def _draw_seek_row(self):
        self.seek_slider.draw(self.screen)
        if self.engine and self.engine.duration:
            cur = self._format_time(self.engine.get_clock())
            total = self._format_time(self.engine.duration)
            cur_s = self.font_small.render(cur, True, TEXT_FAINT)
            tot_s = self.font_small.render(total, True, TEXT_FAINT)
            self.screen.blit(cur_s, (self.seek_slider.rect.x, self.seek_slider.rect.bottom + 6))
            self.screen.blit(tot_s, (self.seek_slider.rect.right - tot_s.get_width(),
                                      self.seek_slider.rect.bottom + 6))
        self.mute_btn.draw(self.screen)

    def _draw_transport_row(self):
        self.sliders_btn.draw(self.screen)
        self.chat_btn.draw(self.screen)
        self.gear_btn.draw(self.screen)

        self.rewind_btn.draw(self.screen)
        self.prev_btn.draw(self.screen)
        self.play_btn.draw(self.screen)
        self.next_btn.draw(self.screen)
        self.forward_btn.draw(self.screen)

        self.star_btn.draw(self.screen)
        self.repeat_btn.draw(self.screen)
        self.restore_btn.draw(self.screen)

    @staticmethod
    def _format_time(seconds):
        seconds = int(max(0, seconds))
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def main():
    app = PlayerApp()
    app.run()


if __name__ == "__main__":
    main()