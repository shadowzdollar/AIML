"""
Breakout - Arduino joystick edition

Hardware:
    Flash joystick_bridge.ino onto your Arduino first (see that file for
    wiring). This script talks to it over USB serial.

Setup:
    pip install pygame pyserial
    Edit SERIAL_PORT below to match your Arduino's COM port (Windows:
    check Device Manager -> Ports (COM & LPT); it'll be something like
    "COM3", "COM5", etc.) If you leave it as "AUTO", the script will try
    to auto-detect an Arduino-like device and tell you what it found (or
    didn't) when it starts.

Controls:
    Joystick left/right  - move paddle (proportional: the further you
                            push, the faster the paddle moves)
    Joystick button      - launch the ball when it's stuck to the paddle
    Keyboard (fallback, always active even with the joystick connected):
        Left/Right arrows or A/D - move paddle
        Space                     - launch ball
        R                         - restart after game over / win

Design notes:
    - Serial reads happen on a background thread so a slow/missing
      joystick never stalls the game loop; the main loop just reads
      whatever the latest known state is.
    - The joystick's electrical center is rarely exactly at the raw
      midpoint (1023/2), so on startup the script samples the joystick
      for about a second and uses the average as "center", then treats
      deflection from THAT as the real signal. A small deadzone around
      center absorbs sensor noise so the paddle doesn't drift.
    - If no Arduino is found (or pyserial isn't installed), the game
      still runs fine on keyboard alone - it just prints a note and
      keeps going, rather than crashing.
"""

import pygame
import random
import sys
import math
import threading
import time

# ---------------------------------------------------------- Serial config
SERIAL_PORT = "AUTO"   # e.g. "COM5" on Windows, "/dev/ttyUSB0" on Linux/Mac,
                        # or leave as "AUTO" to try auto-detecting
BAUD_RATE = 115200
JOYSTICK_DEADZONE = 0.12         # ignore small drift around center
CALIBRATION_SAMPLES = 40         # ~ first 0.6s of data, used to find center

try:
    import serial
    import serial.tools.list_ports
    PYSERIAL_AVAILABLE = True
except ImportError:
    PYSERIAL_AVAILABLE = False


# ---------------------------------------------------------------- Config --
WIDTH, HEIGHT = 800, 700
FPS = 60

PADDLE_WIDTH = 110
PADDLE_HEIGHT = 16
PADDLE_Y = HEIGHT - 40
PADDLE_SPEED = 9          # max paddle speed, reached at full joystick deflection

BALL_RADIUS = 8
BALL_BASE_SPEED = 6.0
BALL_MAX_SPEED = 11.0
BALL_SPEED_RAMP = 0.02

BRICK_ROWS_AREA_TOP = 70
BRICK_HEIGHT = 26
BRICK_GAP = 4
BRICK_COLS = 12

STARTING_LIVES = 3

WHITE = (240, 240, 245)
BLACK = (15, 15, 20)
GRAY = (90, 90, 100)
PADDLE_COLOR = (80, 200, 160)
BALL_COLOR = (250, 220, 90)

BRICK_COLORS = {
    "R": (220, 70, 70), "O": (230, 140, 60), "Y": (230, 210, 70),
    "G": (90, 190, 100), "B": (80, 140, 220), "P": (170, 100, 210),
}
BRICK_HP = {"R": 1, "O": 1, "Y": 1, "G": 1, "B": 2, "P": 3}

LEVELS = [
    [
        "RRRRRRRRRRRR", "OOOOOOOOOOOO", "YYYYYYYYYYYY", "............",
        "GGGGGGGGGGGG", "............", "BB..BBBB..BB",
    ],
    [
        "P..P..P..P..", "PPPPPPPPPPPP", ".B.B.B.B.B.B", "GGGGGGGGGGGG",
        ".O.O.O.O.O.O", "RRRRRRRRRRRR", "Y.Y.Y.Y.Y.Y.",
    ],
]

POWERUP_TYPES = ["life", "wide", "narrow", "multi", "slow"]
POWERUP_WEIGHTS = [8, 20, 10, 15, 15]
POWERUP_COLORS = {
    "life": (250, 90, 90), "wide": (100, 220, 140), "narrow": (220, 100, 100),
    "multi": (250, 220, 90), "slow": (120, 180, 250),
}
POWERUP_FALL_SPEED = 3
POWERUP_DURATION_FRAMES = 8 * FPS


# ------------------------------------------------------------- Joystick IO
class JoystickReader:
    """Reads CSV lines ('x,y,button') from the Arduino on a background
    thread and exposes the latest calibrated axis value + button edge."""

    def __init__(self, port, baud):
        self.axis = 0.0             # -1.0 (full left) .. 1.0 (full right)
        self.button_down = False
        self.button_pressed_event = False  # true for one read if just pressed
        self._prev_button = False
        self.connected = False
        self._stop = False
        self._center = 512.0
        self._calibrated = False
        self._samples = []

        self._ser = None
        if not PYSERIAL_AVAILABLE:
            print("[joystick] pyserial not installed - run: pip install pyserial")
            print("[joystick] Falling back to keyboard-only control.")
            return

        resolved_port = port
        if port == "AUTO":
            resolved_port = self._autodetect_port()
            if resolved_port is None:
                print("[joystick] Could not auto-detect an Arduino. "
                      "Set SERIAL_PORT manually at the top of the file.")
                self._list_ports()
                return

        try:
            self._ser = serial.Serial(resolved_port, baud, timeout=0.2)
            time.sleep(2)  # let the Arduino reset after the port opens
            self.connected = True
            print(f"[joystick] Connected on {resolved_port} at {baud} baud.")
            self._thread = threading.Thread(target=self._read_loop, daemon=True)
            self._thread.start()
        except Exception as e:
            print(f"[joystick] Could not open {resolved_port}: {e}")
            print("[joystick] Falling back to keyboard-only control.")
            self._list_ports()

    def _autodetect_port(self):
        for p in serial.tools.list_ports.comports():
            desc = (p.description or "").lower()
            if "arduino" in desc or "ch340" in desc or "usb serial" in desc or "usb-serial" in desc:
                return p.device
        ports = list(serial.tools.list_ports.comports())
        if len(ports) == 1:
            return ports[0].device
        return None

    def _list_ports(self):
        ports = list(serial.tools.list_ports.comports())
        if not ports:
            print("[joystick] No serial ports detected at all.")
        else:
            print("[joystick] Available ports:")
            for p in ports:
                print(f"    {p.device}  -  {p.description}")

    def _read_loop(self):
        while not self._stop:
            try:
                line = self._ser.readline().decode("utf-8", errors="ignore").strip()
                if not line:
                    continue
                parts = line.split(",")
                if len(parts) != 3:
                    continue
                x_raw, _y_raw, btn = (float(parts[0]), float(parts[1]), int(parts[2]))

                if not self._calibrated:
                    self._samples.append(x_raw)
                    if len(self._samples) >= CALIBRATION_SAMPLES:
                        self._center = sum(self._samples) / len(self._samples)
                        self._calibrated = True
                        print(f"[joystick] Calibrated center = {self._center:.0f}")
                    continue

                normalized = (x_raw - self._center) / self._center
                normalized = max(-1.0, min(1.0, normalized))
                if abs(normalized) < JOYSTICK_DEADZONE:
                    normalized = 0.0
                self.axis = normalized

                pressed_now = (btn == 1)
                if pressed_now and not self._prev_button:
                    self.button_pressed_event = True
                self.button_down = pressed_now
                self._prev_button = pressed_now

            except Exception:
                # transient read hiccup - just skip this line
                continue

    def consume_button_press(self):
        """Returns True once per physical press, then clears the flag."""
        if self.button_pressed_event:
            self.button_pressed_event = False
            return True
        return False

    def close(self):
        self._stop = True
        if self._ser:
            try:
                self._ser.close()
            except Exception:
                pass


# ------------------------------------------------------------------ Paddle
class Paddle:
    def __init__(self):
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.x = WIDTH / 2 - self.width / 2
        self.y = PADDLE_Y
        self.wide_timer = 0
        self.narrow_timer = 0

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), int(self.width), self.height)

    def update(self, keys, joystick_axis):
        move = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move -= 1.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move += 1.0
        if joystick_axis:
            move = joystick_axis  # joystick overrides/combines naturally since it's analog

        self.x += move * PADDLE_SPEED
        self.x = max(0, min(WIDTH - self.width, self.x))

        if self.wide_timer > 0:
            self.wide_timer -= 1
            if self.wide_timer == 0:
                self.width = PADDLE_WIDTH
        if self.narrow_timer > 0:
            self.narrow_timer -= 1
            if self.narrow_timer == 0:
                self.width = PADDLE_WIDTH

    def apply_wide(self):
        self.width = PADDLE_WIDTH * 1.6
        self.wide_timer = POWERUP_DURATION_FRAMES
        self.narrow_timer = 0

    def apply_narrow(self):
        self.width = PADDLE_WIDTH * 0.6
        self.narrow_timer = POWERUP_DURATION_FRAMES
        self.wide_timer = 0

    def draw(self, screen):
        pygame.draw.rect(screen, PADDLE_COLOR, self.rect(), border_radius=6)


# -------------------------------------------------------------------- Ball
class Ball:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.stuck = False

    def rect(self):
        return pygame.Rect(int(self.x - BALL_RADIUS), int(self.y - BALL_RADIUS),
                            BALL_RADIUS * 2, BALL_RADIUS * 2)

    def speed(self):
        return math.hypot(self.vx, self.vy)

    def set_speed(self, new_speed):
        s = self.speed()
        if s == 0:
            return
        scale = new_speed / s
        self.vx *= scale
        self.vy *= scale

    def update(self):
        if self.stuck:
            return
        self.x += self.vx
        self.y += self.vy

        if self.x - BALL_RADIUS <= 0:
            self.x = BALL_RADIUS
            self.vx *= -1
        elif self.x + BALL_RADIUS >= WIDTH:
            self.x = WIDTH - BALL_RADIUS
            self.vx *= -1
        if self.y - BALL_RADIUS <= 0:
            self.y = BALL_RADIUS
            self.vy *= -1

    def draw(self, screen):
        pygame.draw.circle(screen, BALL_COLOR, (int(self.x), int(self.y)), BALL_RADIUS)


# ------------------------------------------------------------------- Brick
class Brick:
    def __init__(self, x, y, w, h, color_key):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_key = color_key
        self.hp = BRICK_HP[color_key]
        self.max_hp = self.hp

    def hit(self):
        self.hp -= 1
        return self.hp <= 0

    def draw(self, screen):
        base = BRICK_COLORS[self.color_key]
        fade = self.hp / self.max_hp
        color = tuple(int(c * (0.5 + 0.5 * fade)) for c in base)
        pygame.draw.rect(screen, color, self.rect, border_radius=3)
        pygame.draw.rect(screen, BLACK, self.rect, width=1, border_radius=3)


# ----------------------------------------------------------------- PowerUp
class PowerUp:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.size = 18

    def rect(self):
        return pygame.Rect(int(self.x - self.size / 2), int(self.y - self.size / 2),
                            self.size, self.size)

    def update(self):
        self.y += POWERUP_FALL_SPEED

    def draw(self, screen, font):
        color = POWERUP_COLORS[self.kind]
        pygame.draw.rect(screen, color, self.rect(), border_radius=4)
        label = {"life": "+1", "wide": "W", "narrow": "N", "multi": "M", "slow": "S"}[self.kind]
        text = font.render(label, True, BLACK)
        screen.blit(text, (self.x - text.get_width() / 2, self.y - text.get_height() / 2))


# -------------------------------------------------------------------- Game
class Game:
    def __init__(self):
        self.level_index = 0
        self.reset(full=True)

    def reset(self, full=False):
        if full:
            self.score = 0
            self.lives = STARTING_LIVES
            self.level_index = 0
        self.paddle = Paddle()
        self.balls = [self._new_ball_on_paddle()]
        self.bricks = self._build_level(self.level_index)
        self.powerups = []
        self.ball_speed = BALL_BASE_SPEED
        self.game_over = False
        self.won = False

    def _new_ball_on_paddle(self):
        b = Ball(self.paddle_center_x() if hasattr(self, "paddle") else WIDTH / 2,
                  PADDLE_Y - BALL_RADIUS - 2, 0, 0)
        b.stuck = True
        return b

    def paddle_center_x(self):
        return self.paddle.x + self.paddle.width / 2

    def _build_level(self, index):
        layout = LEVELS[index % len(LEVELS)]
        bricks = []
        brick_w = (WIDTH - BRICK_GAP * (BRICK_COLS + 1)) / BRICK_COLS
        for row, row_str in enumerate(layout):
            for col, ch in enumerate(row_str):
                if ch == "." or ch not in BRICK_COLORS:
                    continue
                x = BRICK_GAP + col * (brick_w + BRICK_GAP)
                y = BRICK_ROWS_AREA_TOP + row * (BRICK_HEIGHT + BRICK_GAP)
                bricks.append(Brick(int(x), int(y), int(brick_w), BRICK_HEIGHT, ch))
        return bricks

    def launch(self):
        for b in self.balls:
            if b.stuck:
                b.stuck = False
                angle = random.uniform(-35, 35)
                rad = math.radians(angle)
                b.vx = math.sin(rad) * self.ball_speed
                b.vy = -math.cos(rad) * self.ball_speed

    def update(self, keys, joystick_axis):
        if self.game_over or self.won:
            return

        self.paddle.update(keys, joystick_axis)

        for b in self.balls:
            if b.stuck:
                b.x = self.paddle_center_x()
            b.update()

        self._handle_paddle_collisions()
        self._handle_brick_collisions()
        self._handle_powerups()

        self.balls = [b for b in self.balls if b.y - BALL_RADIUS < HEIGHT]

        if not self.balls:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                self.balls = [self._new_ball_on_paddle()]

        if not self.bricks:
            self.level_index += 1
            if self.level_index >= len(LEVELS):
                self.won = True
            else:
                self.bricks = self._build_level(self.level_index)
                self.balls = [self._new_ball_on_paddle()]
                self.powerups = []

    def _handle_paddle_collisions(self):
        prect = self.paddle.rect()
        for b in self.balls:
            if b.stuck or b.vy <= 0:
                continue
            if b.rect().colliderect(prect):
                offset = (b.x - (prect.x + prect.width / 2)) / (prect.width / 2)
                offset = max(-1, min(1, offset))
                angle = offset * 60
                rad = math.radians(angle)
                speed = b.speed()
                b.vx = math.sin(rad) * speed
                b.vy = -abs(math.cos(rad) * speed)
                b.y = prect.y - BALL_RADIUS

    def _handle_brick_collisions(self):
        for b in self.balls:
            if b.stuck:
                continue
            brect = b.rect()
            hit_index = None
            for i, brick in enumerate(self.bricks):
                if brick.rect.colliderect(brect):
                    hit_index = i
                    break
            if hit_index is None:
                continue

            brick = self.bricks[hit_index]
            overlap_left = brect.right - brick.rect.left
            overlap_right = brick.rect.right - brect.left
            overlap_top = brect.bottom - brick.rect.top
            overlap_bottom = brick.rect.bottom - brect.top
            smallest = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
            if smallest in (overlap_left, overlap_right):
                b.vx *= -1
            else:
                b.vy *= -1

            destroyed = brick.hit()
            if destroyed:
                self.score += 10 * brick.max_hp
                self._maybe_drop_powerup(brick.rect.centerx, brick.rect.centery)
                del self.bricks[hit_index]
                self.ball_speed = min(BALL_MAX_SPEED, self.ball_speed + BALL_SPEED_RAMP)
                for ball in self.balls:
                    if not ball.stuck:
                        ball.set_speed(self.ball_speed)

    def _maybe_drop_powerup(self, x, y):
        if random.random() < 0.18:
            kind = random.choices(POWERUP_TYPES, weights=POWERUP_WEIGHTS, k=1)[0]
            self.powerups.append(PowerUp(x, y, kind))

    def _handle_powerups(self):
        prect = self.paddle.rect()
        still_falling = []
        for p in self.powerups:
            p.update()
            if p.rect().colliderect(prect):
                self._apply_powerup(p.kind)
            elif p.y - p.size < HEIGHT:
                still_falling.append(p)
        self.powerups = still_falling

    def _apply_powerup(self, kind):
        if kind == "life":
            self.lives += 1
        elif kind == "wide":
            self.paddle.apply_wide()
        elif kind == "narrow":
            self.paddle.apply_narrow()
        elif kind == "slow":
            self.ball_speed = max(3.0, self.ball_speed - 1.5)
            for b in self.balls:
                if not b.stuck:
                    b.set_speed(self.ball_speed)
        elif kind == "multi":
            new_balls = []
            for b in list(self.balls):
                if b.stuck:
                    continue
                for spread in (-18, 18):
                    rad = math.radians(spread)
                    speed = b.speed()
                    nb = Ball(b.x, b.y,
                              b.vx * math.cos(rad) - b.vy * math.sin(rad),
                              b.vx * math.sin(rad) + b.vy * math.cos(rad))
                    nb.set_speed(speed)
                    new_balls.append(nb)
            self.balls.extend(new_balls)

    def draw(self, screen, font, big_font, joystick_status):
        screen.fill(BLACK)

        self.paddle.draw(screen)
        for b in self.balls:
            b.draw(screen)
        for brick in self.bricks:
            brick.draw(screen)
        for p in self.powerups:
            p.draw(screen, font)

        hud = font.render(
            f"Score: {self.score}   Lives: {self.lives}   Level: {self.level_index + 1}/{len(LEVELS)}",
            True, WHITE)
        screen.blit(hud, (10, 10))

        status_color = (100, 220, 140) if joystick_status == "connected" else (200, 90, 90)
        status_text = f"Joystick: {joystick_status}"
        st = font.render(status_text, True, status_color)
        screen.blit(st, (WIDTH - st.get_width() - 10, 10))

        any_stuck = any(b.stuck for b in self.balls)
        if any_stuck and not self.game_over and not self.won:
            hint = font.render("Press SPACE or joystick button to launch", True, GRAY)
            screen.blit(hint, (WIDTH / 2 - hint.get_width() / 2, HEIGHT / 2 + 60))

        if self.game_over:
            self._draw_center_message(screen, big_font, font, "GAME OVER",
                                       f"Final Score: {self.score}  -  Press R to restart")
        elif self.won:
            self._draw_center_message(screen, big_font, font, "YOU WIN!",
                                       f"Final Score: {self.score}  -  Press R to play again")

        pygame.display.flip()

    def _draw_center_message(self, screen, big_font, font, title, subtitle):
        t = big_font.render(title, True, WHITE)
        screen.blit(t, (WIDTH / 2 - t.get_width() / 2, HEIGHT / 2 - 50))
        s = font.render(subtitle, True, WHITE)
        screen.blit(s, (WIDTH / 2 - s.get_width() / 2, HEIGHT / 2 + 10))


# ------------------------------------------------------------------- Main
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Breakout - Joystick Edition")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 22)
    big_font = pygame.font.SysFont("Arial", 46, bold=True)

    joystick = JoystickReader(SERIAL_PORT, BAUD_RATE)
    game = Game()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                joystick.close()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game.launch()
                if event.key == pygame.K_r and (game.game_over or game.won):
                    game.reset(full=True)

        if joystick.consume_button_press():
            game.launch()

        keys = pygame.key.get_pressed()
        game.update(keys, joystick.axis)

        status = "connected" if joystick.connected else "not found (keyboard only)"
        game.draw(screen, font, big_font, status)
        clock.tick(FPS)


if __name__ == "__main__":
    main()
