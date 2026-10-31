import pygame
import math
import sys
import random
import json
import os

# Initialize Pygame & Mixer for sound synthesis
pygame.init()
pygame.font.init()
try:
    pygame.mixer.init(frequency=22050, size=-16, channels=2)
    SOUND_ENABLED = True
except:
    SOUND_ENABLED = False

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
FPS = 60

# Procedural Sound Generators
def play_sound(sound_type):
    if not SOUND_ENABLED:
        return
    try:
        sample_rate = 22050
        if sound_type == "jump":
            duration = 0.15
            n_samples = int(sample_rate * duration)
            buffer = bytearray()
            for i in range(n_samples):
                t = i / sample_rate
                freq = 300 + t * 1000
                val = int(32767 * 0.3 * math.sin(2 * math.pi * freq * t) * (1 - t/duration))
                buffer += val.to_bytes(2, byteorder='little', signed=True)
                buffer += val.to_bytes(2, byteorder='little', signed=True)
            sound = pygame.mixer.Sound(buffer=bytes(buffer))
            sound.play()
        elif sound_type == "crash":
            duration = 0.4
            n_samples = int(sample_rate * duration)
            buffer = bytearray()
            for i in range(n_samples):
                t = i / sample_rate
                val = int(32767 * 0.5 * (random.random() * 2 - 1) * (1 - t/duration))
                buffer += val.to_bytes(2, byteorder='little', signed=True)
                buffer += val.to_bytes(2, byteorder='little', signed=True)
            sound = pygame.mixer.Sound(buffer=bytes(buffer))
            sound.play()
        elif sound_type == "victory":
            duration = 0.6
            n_samples = int(sample_rate * duration)
            buffer = bytearray()
            for i in range(n_samples):
                t = i / sample_rate
                freq = 440 if t < 0.3 else 660
                val = int(32767 * 0.3 * math.sin(2 * math.pi * freq * t) * (1 - t/duration))
                buffer += val.to_bytes(2, byteorder='little', signed=True)
                buffer += val.to_bytes(2, byteorder='little', signed=True)
            sound = pygame.mixer.Sound(buffer=bytes(buffer))
            sound.play()
    except:
        pass

# Colors (Sunset / Tropical Palette)
SKY_TOP = (40, 100, 200)
SKY_MID = (220, 140, 100)
SKY_BOTTOM = (255, 220, 180)
GROUND_GRASS = (70, 160, 70)
GROUND_DIRT = (120, 75, 40)
BLACK = (20, 20, 20)
WHITE = (255, 255, 255)
RED = (230, 40, 40)
YELLOW = (250, 200, 40)
ORANGE = (245, 95, 20)
DARK_ORANGE = (180, 50, 10)
GREEN = (50, 210, 80)
NEON_GREEN = (50, 255, 100)
ELECTRIC_BLUE = (0, 180, 255)
PURPLE = (160, 50, 240)
GRAY = (130, 130, 130)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (190, 190, 190)
CHROME = (220, 230, 240)
TIRE_BLACK = (30, 30, 30)

SAVE_FILE = os.path.join("games", "save_data_pro.json")

def load_save_data():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"unlocked_level": 1, "stars": {}, "score": 0, "bike_color": "ORANGE"}

def save_game_data(data):
    try:
        os.makedirs("games", exist_ok=True)
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f)
    except:
        pass

class FloatingText:
    def __init__(self, text, x, y, color):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.life = 60

    def update(self):
        self.y -= 1.5
        self.life -= 1

class Particle:
    def __init__(self, x, y, vx, vy, color, size, life):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.life = life
        self.max_life = life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.25
        self.life -= 1

    def draw(self, surface, camera_x):
        if self.life > 0:
            s = int(self.size * (self.life / self.max_life))
            if s > 0:
                pygame.draw.circle(surface, self.color, (int(self.x - camera_x), int(self.y)), s)

class Obstacle:
    def __init__(self, x, y, type_str):
        self.x = x
        self.y = y
        self.type = type_str  # "barrel", "spike", "saw", "booster"
        self.angle_offset = random.uniform(0, math.pi * 2)

    def draw(self, surface, camera_x, tick):
        ox = int(self.x - camera_x)
        oy = int(self.y)
        if -80 <= ox <= SCREEN_WIDTH + 80:
            if self.type == "barrel":
                pygame.draw.rect(surface, ORANGE, (ox - 14, oy - 26, 28, 34), border_radius=6)
                pygame.draw.rect(surface, BLACK, (ox - 14, oy - 14, 28, 5))
                pygame.draw.rect(surface, BLACK, (ox - 14, oy - 4, 28, 5))
                pygame.draw.circle(surface, YELLOW, (ox, oy - 9), 6)
            elif self.type == "spike":
                for dx in [-12, 0, 12]:
                    pygame.draw.polygon(surface, DARK_GRAY, [(ox + dx, oy), (ox + dx - 6, oy - 24), (ox + dx + 6, oy - 24)])
                    pygame.draw.polygon(surface, WHITE, [(ox + dx, oy - 2), (ox + dx - 3, oy - 20), (ox + dx + 3, oy - 20)])
            elif self.type == "saw":
                rot = tick * 0.15 + self.angle_offset
                pygame.draw.circle(surface, DARK_GRAY, (ox, oy), 20)
                pygame.draw.circle(surface, CHROME, (ox, oy), 16)
                for i in range(6):
                    a = rot + i * (math.pi / 3)
                    sx = ox + int(24 * math.cos(a))
                    sy = oy + int(24 * math.sin(a))
                    pygame.draw.line(surface, BLACK, (ox, oy), (sx, sy), 3)
            elif self.type == "booster":
                pygame.draw.polygon(surface, YELLOW, [(ox - 20, oy), (ox + 20, oy), (ox, oy - 15)])

class Bike:
    def __init__(self, x, y, color_theme="ORANGE"):
        self.color_theme = color_theme
        self.reset(x, y)

    def reset(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.angle = 0.0
        self.omega = 0.0
        self.wheel_base = 76
        self.radius = 18
        self.crashed = False
        self.finished = False
        self.air_time = 0
        self.total_rotation = 0.0
        self.last_angle = 0.0
        self.flips = 0
        self.on_ground = False
        self.boost_timer = 0

    def get_theme_colors(self):
        if self.color_theme == "GREEN":
            return NEON_GREEN, DARK_GRAY
        elif self.color_theme == "BLUE":
            return ELECTRIC_BLUE, DARK_GRAY
        elif self.color_theme == "PURPLE":
            return PURPLE, DARK_GRAY
        else:
            return ORANGE, DARK_ORANGE

    def update(self, keys, terrain):
        if self.crashed or self.finished:
            return

        if self.boost_timer > 0:
            self.boost_timer -= 1
            boost_mult = 1.6
        else:
            boost_mult = 1.0

        throttle = 0
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            throttle = 0.62 * boost_mult
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            throttle = -0.45

        tilt = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            tilt = -0.065
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            tilt = 0.065

        if self.on_ground:
            forward_x = math.cos(self.angle)
            forward_y = math.sin(self.angle)
            
            self.vx += forward_x * throttle
            self.vy += forward_y * throttle

            self.vx *= 0.97
            self.vy *= 0.97

            ground_y = terrain.get_height(self.x)
            target_y = ground_y - 25
            self.y += (target_y - self.y) * 0.7

            h1 = terrain.get_height(self.x - 28)
            h2 = terrain.get_height(self.x + 28)
            slope_angle = math.atan2(h2 - h1, 56)
            
            angle_diff = (slope_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
            self.angle += angle_diff * 0.5
            self.omega = 0

            self.angle += tilt * 0.85
            self.air_time = 0
        else:
            self.vy += 0.52
            self.vx *= 0.995
            self.vy *= 0.995

            self.omega += tilt * 0.22
            self.omega *= 0.96
            self.angle += self.omega

            self.air_time += 1

        self.x += self.vx
        self.y += self.vy

        angle_delta = self.angle - self.last_angle
        angle_delta = (angle_delta + math.pi) % (2 * math.pi) - math.pi
        self.total_rotation += angle_delta
        self.last_angle = self.angle

        if abs(self.total_rotation) >= math.pi * 1.85:
            self.flips += 1
            self.total_rotation = 0

        ground_y = terrain.get_height(self.x)
        if self.y >= ground_y - 24:
            if not self.on_ground:
                h1 = terrain.get_height(self.x - 28)
                h2 = terrain.get_height(self.x + 28)
                slope_angle = math.atan2(h2 - h1, 56)
                
                diff = abs((self.angle - slope_angle + math.pi) % (2 * math.pi) - math.pi)
                if diff > 1.25 or self.vy > 9.5:
                    self.crashed = True
                    play_sound("crash")
            self.on_ground = True
            self.y = ground_y - 24
        else:
            self.on_ground = False

        if self.on_ground and (math.cos(self.angle) < -0.35 and abs(self.vx) > 2.5):
            self.crashed = True
            play_sound("crash")

    def draw(self, surface, camera_x):
        bx = int(self.x - camera_x)
        by = int(self.y)

        cos_a = math.cos(self.angle)
        sin_a = math.sin(self.angle)

        w1_x = bx - int(self.wheel_base/2 * cos_a - 15 * sin_a)
        w1_y = by - int(self.wheel_base/2 * sin_a + 15 * cos_a)
        w2_x = bx + int(self.wheel_base/2 * cos_a + 15 * sin_a)
        w2_y = by + int(self.wheel_base/2 * sin_a - 15 * cos_a)

        primary_color, secondary_color = self.get_theme_colors()

        body_cx = bx
        body_cy = by - 16

        # Swingarm & Suspension
        pygame.draw.line(surface, DARK_GRAY, (w1_x, w1_y), (body_cx - 15, body_cy + 5), 8)
        pygame.draw.line(surface, CHROME, (body_cx - 10, body_cy), (body_cx - 20, body_cy - 10), 5)

        # Engine Block
        engine_pts = [
            (body_cx - int(16 * cos_a - 12 * sin_a), body_cy - int(16 * sin_a + 12 * cos_a)),
            (body_cx + int(16 * cos_a - 12 * sin_a), body_cy + int(16 * sin_a + 12 * cos_a)),
            (body_cx + int(12 * cos_a + 14 * sin_a), body_cy + int(12 * sin_a - 14 * cos_a)),
            (body_cx - int(12 * cos_a + 14 * sin_a), body_cy - int(12 * sin_a - 14 * cos_a))
        ]
        pygame.draw.polygon(surface, DARK_GRAY, engine_pts)
        pygame.draw.polygon(surface, BLACK, engine_pts, 2)
        for i in range(-6, 8, 4):
            fx1 = body_cx + int(i * cos_a - 10 * sin_a)
            fy1 = body_cy + int(i * sin_a + 10 * cos_a)
            fx2 = body_cx + int(i * cos_a + 10 * sin_a)
            fy2 = body_cy + int(i * sin_a - 10 * cos_a)
            pygame.draw.line(surface, LIGHT_GRAY, (fx1, fy1), (fx2, fy2), 2)

        # Chrome Exhaust Pipe
        ex_start_x = body_cx - int(5 * cos_a)
        ex_start_y = body_cy - int(5 * sin_a)
        ex_mid_x = body_cx - int(30 * cos_a - 8 * sin_a)
        ex_mid_y = body_cy - int(30 * sin_a + 8 * cos_a)
        ex_end_x = w1_x - int(10 * cos_a)
        ex_end_y = w1_y - int(10 * sin_a)
        pygame.draw.line(surface, CHROME, (ex_start_x, ex_start_y), (ex_mid_x, ex_mid_y), 5)
        pygame.draw.line(surface, CHROME, (ex_mid_x, ex_mid_y), (ex_end_x, ex_end_y), 4)

        # Steel Frame
        pygame.draw.line(surface, DARK_GRAY, (body_cx - 20, body_cy - 5), (body_cx + 15, body_cy - 12), 6)
        pygame.draw.line(surface, DARK_GRAY, (body_cx + 15, body_cy - 12), (w2_x, w2_y), 6)

        # Plastics & Bodywork
        tank_pts = [
            (body_cx - int(24 * cos_a - 14 * sin_a), body_cy - int(24 * sin_a + 14 * cos_a)),
            (body_cx + int(18 * cos_a - 18 * sin_a), body_cy + int(18 * sin_a + 18 * cos_a)),
            (body_cx + int(28 * cos_a - 6 * sin_a), body_cy + int(28 * sin_a - 6 * cos_a)),
            (body_cx - int(8 * cos_a - 22 * sin_a), body_cy - int(8 * sin_a + 22 * cos_a))
        ]
        pygame.draw.polygon(surface, primary_color, tank_pts)
        pygame.draw.polygon(surface, BLACK, tank_pts, 2)

        fender_tip_x = w2_x + int(35 * cos_a)
        fender_tip_y = w2_y + int(35 * sin_a) - 10
        pygame.draw.line(surface, primary_color, (body_cx + 20, body_cy - 10), (fender_tip_x, fender_tip_y), 7)
        
        rear_fender_x = w1_x - int(35 * cos_a)
        rear_fender_y = w1_y - int(35 * sin_a) - 15
        pygame.draw.line(surface, primary_color, (body_cx - 25, body_cy - 15), (rear_fender_x, rear_fender_y), 6)

        # Seat
        seat_p1 = (body_cx - int(30 * cos_a - 18 * sin_a), body_cy - int(30 * sin_a + 18 * cos_a))
        seat_p2 = (body_cx - int(5 * cos_a - 18 * sin_a), body_cy - int(5 * sin_a + 18 * cos_a))
        pygame.draw.line(surface, BLACK, seat_p1, seat_p2, 8)

        # Forks & Handlebars
        fork_top_x = body_cx + int(25 * cos_a)
        fork_top_y = body_cy + int(25 * sin_a) - 5
        pygame.draw.line(surface, CHROME, (w2_x, w2_y), (fork_top_x, fork_top_y), 6)
        pygame.draw.line(surface, primary_color, (w2_x, w2_y), (w2_x + int(15 * cos_a), w2_y + int(15 * sin_a)), 7)

        hb_x = fork_top_x + int(10 * sin_a)
        hb_y = fork_top_y - int(10 * cos_a) - 14
        pygame.draw.line(surface, BLACK, (fork_top_x, fork_top_y), (hb_x, hb_y), 6)
        pygame.draw.line(surface, RED, (hb_x - 8, hb_y), (hb_x + 8, hb_y), 7)

        # Rider
        r_hip_x = body_cx - int(14 * cos_a)
        r_hip_y = body_cy - int(14 * sin_a) - 6
        
        r_shoulder_x = body_cx - int(18 * cos_a)
        r_shoulder_y = body_cy - int(18 * sin_a) - 30
        
        r_head_x = r_shoulder_x - int(10 * cos_a)
        r_head_y = r_shoulder_y - 14

        foot_x = body_cx + int(4 * cos_a)
        foot_y = body_cy + int(4 * sin_a) + 8
        pygame.draw.line(surface, GREEN, (r_hip_x, r_hip_y), (foot_x, foot_y), 9)
        pygame.draw.circle(surface, DARK_GRAY, (foot_x, foot_y), 6)

        pygame.draw.line(surface, primary_color, (r_hip_x, r_hip_y), (r_shoulder_x, r_shoulder_y), 13)
        pygame.draw.line(surface, WHITE, (r_hip_x - int(4*sin_a), r_hip_y + int(4*cos_a)), (r_shoulder_x - int(4*sin_a), r_shoulder_y + int(4*cos_a)), 4)

        elbow_x = (r_shoulder_x + hb_x) // 2 - int(6 * sin_a)
        elbow_y = (r_shoulder_y + hb_y) // 2 + int(6 * cos_a)
        pygame.draw.line(surface, primary_color, (r_shoulder_x, r_shoulder_y), (elbow_x, elbow_y), 7)
        pygame.draw.line(surface, primary_color, (elbow_x, elbow_y), (hb_x, hb_y), 6)
        pygame.draw.circle(surface, BLACK, (hb_x, hb_y), 5)

        # Helmet
        pygame.draw.circle(surface, primary_color, (r_head_x, r_head_y), 13)
        visor_tip_x = r_head_x + int(14 * cos_a)
        visor_tip_y = r_head_y + int(14 * sin_a) - 6
        pygame.draw.line(surface, primary_color, (r_head_x, r_head_y - 4), (visor_tip_x, visor_tip_y), 5)
        pygame.draw.circle(surface, GREEN, (r_head_x - 3, r_head_y - 4), 11, 3)
        pygame.draw.rect(surface, BLACK, (r_head_x + int(5*cos_a) - 3, r_head_y - 5, 10, 7), border_radius=2)
        pygame.draw.rect(surface, CHROME, (r_head_x + int(5*cos_a) - 1, r_head_y - 4, 6, 4))

        # Wheels
        for wx, wy in [(w1_x, w1_y), (w2_x, w2_y)]:
            pygame.draw.circle(surface, TIRE_BLACK, (wx, wy), self.radius)
            for i in range(12):
                ta = self.angle * 1.5 + i * (math.pi / 6)
                tx1 = wx + int((self.radius - 3) * math.cos(ta))
                ty1 = wy + int((self.radius - 3) * math.sin(ta))
                tx2 = wx + int((self.radius + 1) * math.cos(ta))
                ty2 = wy + int((self.radius + 1) * math.sin(ta))
                pygame.draw.line(surface, BLACK, (tx1, ty1), (tx2, ty2), 3)
            pygame.draw.circle(surface, CHROME, (wx, wy), self.radius - 5)
            pygame.draw.circle(surface, LIGHT_GRAY, (wx, wy), self.radius - 8, 2)
            pygame.draw.circle(surface, DARK_GRAY, (wx, wy), 6)
            for i in range(6):
                sa = self.angle * 2 + i * (math.pi / 3)
                sx = wx + int((self.radius - 6) * math.cos(sa))
                sy = wy + int((self.radius - 6) * math.sin(sa))
                pygame.draw.line(surface, BLACK, (wx, wy), (sx, sy), 1)

class Terrain:
    def __init__(self, level=1):
        self.points = []
        self.obstacles = []
        self.generate_level(level)

    def generate_level(self, level):
        self.points = []
        self.obstacles = []
        length = 7000 + level * 2200
        dx = 35
        x = 0
        y = 480
        
        self.points.append((x, y))
        x += 250
        self.points.append((x, y))

        while x < length - 400:
            x += dx
            if level == 1:
                variation = math.sin(x * 0.005) * 95 + math.cos(x * 0.015) * 45
            elif level == 2:
                variation = math.sin(x * 0.007) * 130 + math.sin(x * 0.025) * 60 + math.cos(x * 0.04) * 25
            elif level == 3:
                variation = math.sin(x * 0.006) * 160 + math.cos(x * 0.02) * 85 + math.sin(x * 0.05) * 40
            elif level == 4:
                variation = math.sin(x * 0.008) * 180 + math.sin(x * 0.03) * 75 + math.cos(x * 0.06) * 45
            else: # Level 5
                variation = math.sin(x * 0.007) * 200 + math.cos(x * 0.022) * 110 + math.sin(x * 0.05) * 55

            target_y = 480 - variation
            y = y * 0.35 + target_y * 0.65
            y = max(160, min(620, y))
            self.points.append((x, y))

            if level >= 2 and random.random() < (0.07 + level * 0.02) and x > 700 and x < length - 700:
                obs_types = ["barrel", "spike"]
                if level >= 3:
                    obs_types.append("booster")
                if level >= 4:
                    obs_types.append("saw")
                obs_type = random.choice(obs_types)
                self.obstacles.append(Obstacle(x, y, obs_type))

        x += 350
        self.points.append((x, y))
        self.finish_x = x

    def get_height(self, x):
        if x <= self.points[0][0]:
            return self.points[0][1]
        if x >= self.points[-1][0]:
            return self.points[-1][1]

        for i in range(len(self.points) - 1):
            p1 = self.points[i]
            p2 = self.points[i+1]
            if p1[0] <= x <= p2[0]:
                t = (x - p1[0]) / (p2[0] - p1[0])
                return p1[1] + t * (p2[1] - p1[1])
        return 480

    def draw(self, surface, camera_x, tick):
        surface.fill(SKY_BOTTOM)
        pygame.draw.rect(surface, SKY_MID, (0, 0, SCREEN_WIDTH, 180))
        pygame.draw.rect(surface, SKY_TOP, (0, 0, SCREEN_WIDTH, 90))

        screen_points = [(-100, SCREEN_HEIGHT + 100)]
        for p in self.points:
            if p[0] >= camera_x - 200 and p[0] <= camera_x + SCREEN_WIDTH + 200:
                screen_points.append((p[0] - camera_x, p[1]))
                
        if screen_points:
            screen_points.append((SCREEN_WIDTH + 100, SCREEN_HEIGHT + 100))
            pygame.draw.polygon(surface, GROUND_DIRT, screen_points)
            
            line_points = [(p[0] - camera_x, p[1]) for p in self.points if p[0] >= camera_x - 200 and p[0] <= camera_x + SCREEN_WIDTH + 200]
            if len(line_points) > 1:
                pygame.draw.lines(surface, GROUND_GRASS, False, line_points, 14)

        for obs in self.obstacles:
            obs.draw(surface, camera_x, tick)

        fx = self.finish_x - camera_x
        if -100 <= fx <= SCREEN_WIDTH + 100:
            fy = self.get_height(self.finish_x)
            pygame.draw.rect(surface, BLACK, (fx - 6, fy - 140, 12, 140))
            pygame.draw.rect(surface, WHITE, (fx, fy - 140, 70, 45))
            for i in range(3):
                for j in range(2):
                    if (i + j) % 2 == 0:
                        pygame.draw.rect(surface, BLACK, (fx + i * 23 + 2, fy - 140 + j * 22 + 2, 21, 21))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Moto X3M Ultimate Pro Edition")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 26, bold=True)
        self.big_font = pygame.font.SysFont("Arial", 52, bold=True)
        self.med_font = pygame.font.SysFont("Arial", 36, bold=True)
        
        self.save_data = load_save_data()
        self.current_level = 1
        self.max_levels = 5
        self.terrain = Terrain(self.current_level)
        self.bike = Bike(120, self.terrain.get_height(120) - 24, self.save_data.get("bike_color", "ORANGE"))
        
        self.camera_x = 0
        self.start_ticks = pygame.time.get_ticks()
        self.elapsed_time = 0
        self.particles = []
        self.floating_texts = []
        self.tick_count = 0
        self.state = "MENU"

    def run(self):
        while True:
            self.tick_count += 1
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state in ("PLAYING", "LEVEL_SELECT", "SHOP"):
                        self.state = "MENU"
                    else:
                        pygame.quit()
                        sys.exit()

                if self.state == "MENU":
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.state = "LEVEL_SELECT"
                    elif event.key == pygame.K_s:
                        self.state = "SHOP"
                elif self.state == "SHOP":
                    if event.key == pygame.K_m:
                        self.state = "MENU"
                    elif event.key == pygame.K_1:
                        self.save_data["bike_color"] = "ORANGE"
                        save_game_data(self.save_data)
                        self.bike.color_theme = "ORANGE"
                    elif event.key == pygame.K_2:
                        self.save_data["bike_color"] = "GREEN"
                        save_game_data(self.save_data)
                        self.bike.color_theme = "GREEN"
                    elif event.key == pygame.K_3:
                        self.save_data["bike_color"] = "BLUE"
                        save_game_data(self.save_data)
                        self.bike.color_theme = "BLUE"
                    elif event.key == pygame.K_4:
                        self.save_data["bike_color"] = "PURPLE"
                        save_game_data(self.save_data)
                        self.bike.color_theme = "PURPLE"
                elif self.state == "LEVEL_SELECT":
                    if pygame.K_1 <= event.key <= pygame.K_5:
                        lvl = event.key - pygame.K_0
                        if lvl <= self.save_data.get("unlocked_level", 1):
                            self.start_level(lvl)
                    elif event.key == pygame.K_m:
                        self.state = "MENU"
                elif self.state == "PLAYING":
                    if event.key == pygame.K_r:
                        self.restart_level()
                elif self.state in ("GAMEOVER", "VICTORY"):
                    if event.key == pygame.K_r or event.key == pygame.K_RETURN:
                        if self.state == "VICTORY":
                            if self.current_level < self.max_levels:
                                self.current_level += 1
                                self.start_level(self.current_level)
                            else:
                                self.state = "LEVEL_SELECT"
                        else:
                            self.start_level(self.current_level)
                    elif event.key == pygame.K_m:
                        self.state = "MENU"
            elif event.type == pygame.MOUSEBUTTONDOWN and self.state == "LEVEL_SELECT":
                mx, my = event.pos
                for i in range(self.max_levels):
                    bx = SCREEN_WIDTH // 2 - 250 + i * 110
                    by = 300
                    if bx <= mx <= bx + 90 and by <= my <= by + 90:
                        lvl = i + 1
                        if lvl <= self.save_data.get("unlocked_level", 1):
                            self.start_level(lvl)

    def start_level(self, level):
        self.current_level = level
        self.terrain = Terrain(level)
        self.bike = Bike(120, self.terrain.get_height(120) - 24, self.save_data.get("bike_color", "ORANGE"))
        self.camera_x = 0
        self.start_ticks = pygame.time.get_ticks()
        self.elapsed_time = 0
        self.particles = []
        self.floating_texts = []
        self.state = "PLAYING"

    def restart_level(self):
        self.start_level(self.current_level)

    def update(self):
        if self.state == "PLAYING":
            keys = pygame.key.get_pressed()
            
            prev_flips = self.bike.flips
            self.bike.update(keys, self.terrain)
            if self.bike.flips > prev_flips:
                play_sound("jump")
                self.floating_texts.append(FloatingText("FLIP! +500 PTS", self.bike.x, self.bike.y - 40, YELLOW))

            target_camera_x = self.bike.x - 320
            self.camera_x += (target_camera_x - self.camera_x) * 0.12
            self.camera_x = max(0, self.camera_x)

            self.elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000.0

            if self.bike.on_ground and abs(self.bike.vx) > 1.5:
                if random.random() < 0.5:
                    px = self.bike.x - 25
                    py = self.terrain.get_height(px)
                    self.particles.append(Particle(px, py, -self.bike.vx * 0.4 + (random.random()-0.5)*2, -random.random()*2.5, GRAY, random.randint(3, 6), 25))

            for obs in self.terrain.obstacles:
                dist = math.hypot(self.bike.x - obs.x, self.bike.y - obs.y)
                if obs.type == "booster":
                    if dist < 35:
                        self.bike.boost_timer = 90
                        play_sound("jump")
                        self.floating_texts.append(FloatingText("BOOST!", self.bike.x, self.bike.y - 40, NEON_GREEN))
                else:
                    if dist < 24:
                        self.bike.crashed = True

            if self.bike.crashed:
                for _ in range(50):
                    angle = random.uniform(0, math.pi * 2)
                    speed = random.uniform(2, 10)
                    self.particles.append(Particle(self.bike.x, self.bike.y, math.cos(angle)*speed, math.sin(angle)*speed, ORANGE, random.randint(4, 9), 50))
                self.state = "GAMEOVER"

            if self.bike.x >= self.terrain.finish_x:
                self.state = "VICTORY"
                play_sound("victory")
                stars = 3 if self.elapsed_time < 28 else (2 if self.elapsed_time < 45 else 1)
                lvl_str = str(self.current_level)
                curr_stars = self.save_data["stars"].get(lvl_str, 0)
                if stars > curr_stars:
                    self.save_data["stars"][lvl_str] = stars

                if self.current_level >= self.save_data.get("unlocked_level", 1) and self.current_level < self.max_levels:
                    self.save_data["unlocked_level"] = self.current_level + 1
                save_game_data(self.save_data)

        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)

        for ft in self.floating_texts[:]:
            ft.update()
            if ft.life <= 0:
                self.floating_texts.remove(ft)

    def draw(self):
        self.terrain.draw(self.screen, self.camera_x, self.tick_count)

        for p in self.particles:
            p.draw(self.screen, self.camera_x)

        if self.state != "GAMEOVER" or self.bike.air_time < 120:
            self.bike.draw(self.screen, self.camera_x)

        for ft in self.floating_texts:
            ft_surf = self.font.render(ft.text, True, ft.color)
            self.screen.blit(ft_surf, (int(ft.x - self.camera_x - ft_surf.get_width()//2), int(ft.y)))

        if self.state == "PLAYING":
            time_surf = self.font.render(f"Time: {self.elapsed_time:.1f}s", True, BLACK)
            level_surf = self.font.render(f"Level: {self.current_level}/{self.max_levels}", True, BLACK)
            flips_surf = self.font.render(f"Flips: {self.bike.flips}", True, BLACK)
            
            self.screen.blit(time_surf, (20, 20))
            self.screen.blit(level_surf, (20, 55))
            self.screen.blit(flips_surf, (20, 90))
            
            controls_surf = self.font.render("W/UP: Throttle | A/D or LEFT/RIGHT: Stunt/Flips | R: Restart", True, DARK_GRAY)
            self.screen.blit(controls_surf, (20, SCREEN_HEIGHT - 40))

        elif self.state == "MENU":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            title = self.big_font.render("MOTO X3M ULTIMATE", True, YELLOW)
            subtitle = self.med_font.render("Press ENTER or SPACE to Play", True, WHITE)
            shop_txt = self.font.render("Press S for Garage / Bike Customization", True, NEON_GREEN)
            controls = self.font.render("Controls: W/S or UP/DOWN to Drive, A/D or LEFT/RIGHT to Stunt & Flips", True, LIGHT_GRAY)

            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 160))
            self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 260))
            self.screen.blit(shop_txt, (SCREEN_WIDTH//2 - shop_txt.get_width()//2, 330))
            self.screen.blit(controls, (SCREEN_WIDTH//2 - controls.get_width()//2, 410))

        elif self.state == "SHOP":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 190))
            self.screen.blit(overlay, (0, 0))

            title = self.big_font.render("GARAGE / BIKE COLOR", True, YELLOW)
            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 140))

            colors = [("1. Racing Orange", ORANGE), ("2. Neon Green", NEON_GREEN), ("3. Electric Blue", ELECTRIC_BLUE), ("4. Royal Purple", PURPLE)]
            for i, (c_name, c_val) in enumerate(colors):
                bx = SCREEN_WIDTH // 2 - 260 + i * 135
                by = 280
                pygame.draw.rect(self.screen, c_val, (bx, by, 115, 115), border_radius=14)
                pygame.draw.rect(self.screen, WHITE, (bx, by, 115, 115), 3, border_radius=14)
                
                name_surf = self.font.render(c_name.split()[1], True, WHITE)
                self.screen.blit(name_surf, (bx + 57 - name_surf.get_width()//2, by + 45))

            curr_col = self.save_data.get("bike_color", "ORANGE")
            sel_txt = self.med_font.render(f"Current Bike Theme: {curr_col}", True, YELLOW)
            self.screen.blit(sel_txt, (SCREEN_WIDTH//2 - sel_txt.get_width()//2, 430))

            back_txt = self.font.render("Press 1-4 to Select | Press M for Main Menu", True, WHITE)
            self.screen.blit(back_txt, (SCREEN_WIDTH//2 - back_txt.get_width()//2, 510))

        elif self.state == "LEVEL_SELECT":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 190))
            self.screen.blit(overlay, (0, 0))

            title = self.big_font.render("SELECT LEVEL", True, YELLOW)
            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 120))

            unlocked = self.save_data.get("unlocked_level", 1)
            for i in range(self.max_levels):
                lvl = i + 1
                bx = SCREEN_WIDTH // 2 - 275 + i * 115
                by = 280
                
                is_unlocked = lvl <= unlocked
                box_color = ORANGE if is_unlocked else DARK_GRAY
                pygame.draw.rect(self.screen, box_color, (bx, by, 95, 95), border_radius=12)
                pygame.draw.rect(self.screen, WHITE, (bx, by, 95, 95), 3, border_radius=12)

                lvl_txt = self.med_font.render(str(lvl), True, WHITE if is_unlocked else GRAY)
                self.screen.blit(lvl_txt, (bx + 47 - lvl_txt.get_width()//2, by + 25))

                if is_unlocked:
                    stars = self.save_data.get("stars", {}).get(str(lvl), 0)
                    star_str = "★" * stars + "☆" * (3 - stars)
                    star_surf = self.font.render(star_str, True, YELLOW)
                    self.screen.blit(star_surf, (bx + 47 - star_surf.get_width()//2, by + 62))

            back_txt = self.font.render("Press M for Main Menu", True, WHITE)
            self.screen.blit(back_txt, (SCREEN_WIDTH//2 - back_txt.get_width()//2, 480))

        elif self.state == "GAMEOVER":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((140, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            title = self.big_font.render("WIPED OUT!", True, WHITE)
            subtitle = self.med_font.render("Press R to Restart | M for Menu", True, YELLOW)
            
            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 240))
            self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 330))

        elif self.state == "VICTORY":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 130, 0, 180))
            self.screen.blit(overlay, (0, 0))

            title = self.big_font.render("LEVEL COMPLETED!", True, YELLOW)
            
            stars = self.save_data.get("stars", {}).get(str(self.current_level), 3)
            star_str = "★" * stars + "☆" * (3 - stars)
            star_surf = self.big_font.render(star_str, True, YELLOW)

            time_text = self.font.render(f"Time: {self.elapsed_time:.2f}s | Flips: {self.bike.flips}", True, WHITE)
            
            if self.current_level < self.max_levels:
                subtitle = self.med_font.render("Press ENTER for Next Level | M for Menu", True, WHITE)
            else:
                subtitle = self.med_font.render("ALL LEVELS BEATEN! Press M for Level Select", True, WHITE)

            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 180))
            self.screen.blit(star_surf, (SCREEN_WIDTH//2 - star_surf.get_width()//2, 255))
            self.screen.blit(time_text, (SCREEN_WIDTH//2 - time_text.get_width()//2, 330))
            self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 400))

        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()
