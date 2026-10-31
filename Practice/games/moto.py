"""
Moto Stunt - 2D Physics Motorbike Game
-------------------------------------------------
Real rigid-body physics via pymunk: chassis + two wheel bodies connected
with spring suspension (DampedSpring + GrooveJoint) and driven by motors,
so jumps, landings, flips, and crashes all come from actual simulation.

Controls:
  Right Arrow / D  - Throttle (grounded) / rotate clockwise (airborne)
  Left Arrow  / A  - Brake+Reverse (grounded) / rotate counter-clockwise (airborne)
  R                - Restart from last checkpoint
  ESC              - Quit

Install:
  pip install pygame pymunk

Run:
  python moto_stunt.py
"""

import pygame
import pymunk
import math
import random
import sys

# ---------------------- Setup ----------------------
pygame.init()
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moto Stunt")
clock = pygame.time.Clock()
FPS = 60

font = pygame.font.SysFont("consolas", 22)
big_font = pygame.font.SysFont("consolas", 44, bold=True)

# Colors - beach/desert theme, original palette
SKY_TOP = (100, 190, 235)
SKY_BOTTOM = (215, 240, 250)
SUN_COLOR = (255, 240, 180)
OCEAN = (40, 140, 190)
SAND_FAR = (225, 195, 145)
SAND_NEAR = (200, 165, 110)
SAND_DARK = (150, 115, 70)
PALM_TRUNK = (90, 60, 40)
PALM_LEAF = (40, 130, 70)
RED = (220, 60, 60)
YELLOW = (240, 200, 60)
WHITE = (255, 255, 255)
DARK = (20, 20, 25)
FRAME_COLOR = (35, 40, 45)
ACCENT = (80, 220, 120)
TANK_COLOR = (230, 90, 40)
RIDER_SUIT = (40, 60, 150)
RIDER_ACCENT = (230, 200, 40)
HELMET_COLOR = (230, 230, 235)
TIRE_COLOR = (30, 30, 32)
RIM_COLOR = (210, 210, 215)

# ---------------------- Physics space ----------------------
space = pymunk.Space()
space.gravity = (0, 1900)
space.damping = 0.999

COLL_TERRAIN = 1
COLL_CHASSIS = 2
COLL_WHEEL = 3
COLL_HAZARD = 4

# ---------------------- Terrain ----------------------
def make_terrain_profile():
    pts = [(-200, 500)]
    x, y = 0, 500
    pts.append((x, y))

    segments = [
        ("flat", 250, 0),
        ("ramp", 150, -120),
        ("gap", 140, 0),
        ("ramp", 150, 120),
        ("flat", 120, 0),
        ("hill_up", 200, -160),
        ("hill_down", 200, 160),
        ("flat", 100, 0),
        ("ramp", 130, -100),
        ("gap", 120, 0),
        ("ramp", 130, 100),
        ("flat", 150, 0),
        ("hill_up", 180, -140),
        ("dip", 160, 140),
        ("ramp", 140, -110),
        ("gap", 130, 0),
        ("ramp", 140, 110),
        ("flat", 300, 0),
    ]

    gaps = []
    for kind, length, dy in segments:
        if kind == "gap":
            gaps.append((x, x + length))
            x += length
            y += dy
            pts.append((x, y))
        else:
            x += length
            y += dy
            pts.append((x, y))

    pts.append((x + 400, y))
    return pts, gaps


def build_terrain(points, gaps):
    for i in range(len(points) - 1):
        p1, p2 = points[i], points[i + 1]
        in_gap = any(p1[0] >= g[0] - 1 and p2[0] <= g[1] + 1 for g in gaps)
        if in_gap:
            continue
        seg = pymunk.Segment(space.static_body, p1, p2, 5)
        seg.friction = 1.6
        seg.elasticity = 0.03
        seg.collision_type = COLL_TERRAIN
        space.add(seg)


TERRAIN_POINTS, GAPS = make_terrain_profile()
build_terrain(TERRAIN_POINTS, GAPS)

SPIKES = [520, 1350, 2050]


def ground_y_at(x):
    for i in range(len(TERRAIN_POINTS) - 1):
        if TERRAIN_POINTS[i][0] <= x <= TERRAIN_POINTS[i + 1][0]:
            t = (x - TERRAIN_POINTS[i][0]) / max(1, (TERRAIN_POINTS[i + 1][0] - TERRAIN_POINTS[i][0]))
            return TERRAIN_POINTS[i][1] + t * (TERRAIN_POINTS[i + 1][1] - TERRAIN_POINTS[i][1])
    return 500


for sx in SPIKES:
    gy = ground_y_at(sx)
    tri = [(sx - 14, gy), (sx + 14, gy), (sx, gy - 30)]
    shape = pymunk.Poly(space.static_body, tri)
    shape.collision_type = COLL_HAZARD
    shape.sensor = True
    space.add(shape)

FINISH_X = TERRAIN_POINTS[-1][0] - 150
CHECKPOINT_XS = [0, 700, 1400, 2100]


# ---------------------- Bike ----------------------
class Bike:
    def __init__(self, spawn_x):
        self.wheel_radius = 18
        self.wheelbase = 50
        self.susp_travel = 16
        self.rest_len = 22
        self.stiffness = 26000
        self.damping = 900
        self.build(spawn_x)
        self.grounded_wheels = 0
        self.crashed = False
        self.finished = False
        self.air_time = 0.0
        self.last_landing_impact = 0.0

    def build(self, spawn_x):
        spawn_y = ground_y_at(spawn_x) - 70

        chassis_pts = [(-32, -12), (26, -14), (36, 0), (30, 8), (-36, 8)]
        chassis_mass = 7
        moment = pymunk.moment_for_poly(chassis_mass, chassis_pts)
        self.chassis_body = pymunk.Body(chassis_mass, moment)
        self.chassis_body.position = (spawn_x, spawn_y)
        self.chassis_shape = pymunk.Poly(self.chassis_body, chassis_pts)
        self.chassis_shape.friction = 0.6
        self.chassis_shape.collision_type = COLL_CHASSIS
        space.add(self.chassis_body, self.chassis_shape)

        wheel_mass = 1.4
        wmoment = pymunk.moment_for_circle(wheel_mass, 0, self.wheel_radius)

        rear_anchor = (-self.wheelbase / 2, 6)
        front_anchor = (self.wheelbase / 2, 4)

        self.rear_body = pymunk.Body(wheel_mass, wmoment)
        self.rear_body.position = (spawn_x + rear_anchor[0], spawn_y + rear_anchor[1] + self.rest_len)
        self.rear_shape = pymunk.Circle(self.rear_body, self.wheel_radius)
        self.rear_shape.friction = 2.3
        self.rear_shape.collision_type = COLL_WHEEL
        space.add(self.rear_body, self.rear_shape)

        self.front_body = pymunk.Body(wheel_mass, wmoment)
        self.front_body.position = (spawn_x + front_anchor[0], spawn_y + front_anchor[1] + self.rest_len)
        self.front_shape = pymunk.Circle(self.front_body, self.wheel_radius)
        self.front_shape.friction = 2.3
        self.front_shape.collision_type = COLL_WHEEL
        space.add(self.front_body, self.front_shape)

        self.rear_anchor_local = rear_anchor
        self.front_anchor_local = front_anchor

        # Suspension: groove constrains wheel to slide vertically under the anchor,
        # damped spring provides the springy force, motor drives rotation.
        groove_len = self.susp_travel
        rear_groove_a = (rear_anchor[0], rear_anchor[1] - 2)
        rear_groove_b = (rear_anchor[0], rear_anchor[1] + groove_len + self.rest_len)
        self.rear_groove = pymunk.GrooveJoint(self.chassis_body, self.rear_body, rear_groove_a, rear_groove_b, (0, 0))
        self.rear_groove.collide_bodies = False
        space.add(self.rear_groove)

        front_groove_a = (front_anchor[0], front_anchor[1] - 2)
        front_groove_b = (front_anchor[0], front_anchor[1] + groove_len + self.rest_len)
        self.front_groove = pymunk.GrooveJoint(self.chassis_body, self.front_body, front_groove_a, front_groove_b, (0, 0))
        self.front_groove.collide_bodies = False
        space.add(self.front_groove)

        self.rear_spring = pymunk.DampedSpring(
            self.chassis_body, self.rear_body, rear_anchor, (0, 0), self.rest_len, self.stiffness, self.damping
        )
        space.add(self.rear_spring)

        self.front_spring = pymunk.DampedSpring(
            self.chassis_body, self.front_body, front_anchor, (0, 0), self.rest_len, self.stiffness * 0.85, self.damping
        )
        space.add(self.front_spring)

        # Keep wheels from swinging sideways relative to chassis (simple rotation-limit
        # is handled implicitly by the groove being fixed in the chassis frame).
        self.rear_motor = pymunk.SimpleMotor(self.chassis_body, self.rear_body, 0)
        self.front_motor = pymunk.SimpleMotor(self.chassis_body, self.front_body, 0)
        space.add(self.rear_motor, self.front_motor)

    def destroy(self):
        objs = [self.chassis_body, self.chassis_shape, self.rear_body, self.rear_shape,
                self.front_body, self.front_shape, self.rear_groove, self.front_groove,
                self.rear_spring, self.front_spring, self.rear_motor, self.front_motor]
        for obj in objs:
            try:
                space.remove(obj)
            except Exception:
                pass

    def respawn(self, x):
        self.destroy()
        self.build(x)
        self.crashed = False
        self.finished = False
        self.air_time = 0.0

    def update_controls(self, keys, dt):
        if self.crashed or self.finished:
            self.rear_motor.rate = 0
            self.front_motor.rate = 0
            return

        airborne = self.grounded_wheels == 0
        if airborne:
            self.air_time += dt
        else:
            self.air_time = 0.0

        throttle = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        brake = keys[pygame.K_LEFT] or keys[pygame.K_a]

        if not airborne:
            if throttle:
                self.rear_motor.rate = -24
                self.front_motor.rate = -24
            elif brake:
                self.rear_motor.rate = 15
                self.front_motor.rate = 15
            else:
                self.rear_motor.rate = 0
                self.front_motor.rate = 0
        else:
            self.rear_motor.rate = -10 if throttle else (10 if brake else 0)
            self.front_motor.rate = self.rear_motor.rate
            if throttle:
                self.chassis_body.angular_velocity += 0.13
            if brake:
                self.chassis_body.angular_velocity -= 0.13

    def is_bad_angle(self):
        angle = self.chassis_body.angle % (2 * math.pi)
        diff = min(angle, abs(2 * math.pi - angle))
        return diff > 1.1

    def wheel_compression(self, which):
        """0 = fully extended, 1 = fully compressed (for visual suspension travel)."""
        body, anchor = (self.rear_body, self.rear_anchor_local) if which == "rear" else (self.front_body, self.front_anchor_local)
        world_anchor = self.chassis_body.local_to_world(anchor)
        dist = (pymunk.Vec2d(*body.position) - world_anchor).length
        t = (dist - self.rest_len) / max(1, self.susp_travel)
        return max(0.0, min(1.0, t))

    def draw(self, surface, cam_x, cam_y):
        angle = self.chassis_body.angle
        cx, cy = self.chassis_body.position
        cx -= cam_x
        cy -= cam_y
        ca, sa = math.cos(angle), math.sin(angle)

        def rot(px, py):
            return (cx + px * ca - py * sa, cy + px * sa + py * ca)

        rear_w = self.rear_body.position
        front_w = self.front_body.position
        rwx, rwy = rear_w.x - cam_x, rear_w.y - cam_y
        fwx, fwy = front_w.x - cam_x, front_w.y - cam_y

        # --- Suspension struts (drawn from chassis anchor to wheel center) ---
        rear_anchor_world = rot(*self.rear_anchor_local)
        front_anchor_world = rot(*self.front_anchor_local)
        pygame.draw.line(surface, (90, 95, 100), rear_anchor_world, (rwx, rwy), 5)
        pygame.draw.line(surface, (90, 95, 100), front_anchor_world, (fwx, fwy), 5)
        pygame.draw.line(surface, ACCENT, front_anchor_world, (fwx, fwy), 2)

        # --- Swingarm from under-seat pivot to rear wheel (visual only) ---
        swing_pivot = rot(-6, 4)
        pygame.draw.line(surface, FRAME_COLOR, swing_pivot, (rwx, rwy), 7)

        # --- Main frame ---
        frame_pts = [rot(-32, -12), rot(26, -14), rot(36, 0), rot(30, 8), rot(-36, 8)]
        pygame.draw.polygon(surface, FRAME_COLOR, frame_pts)
        pygame.draw.polygon(surface, (10, 10, 12), frame_pts, 2)

        # --- Fuel tank ---
        tank_pts = [rot(-20, -18), rot(2, -20), rot(8, -8), rot(-22, -8)]
        pygame.draw.polygon(surface, TANK_COLOR, tank_pts)
        pygame.draw.polygon(surface, (20, 20, 20), tank_pts, 1)
        pygame.draw.line(surface, ACCENT, rot(-18, -14), rot(-2, -15), 2)

        # --- Seat ---
        seat_pts = [rot(-34, -6), rot(-6, -8), rot(-4, -1), rot(-34, 1)]
        pygame.draw.polygon(surface, (25, 25, 28), seat_pts)

        # --- Front fork ---
        pygame.draw.line(surface, (60, 65, 70), rot(28, -10), (fwx, fwy), 4)
        # Handlebar
        pygame.draw.line(surface, FRAME_COLOR, rot(22, -18), rot(34, -20), 3)

        # --- Exhaust pipe ---
        pygame.draw.line(surface, (150, 150, 155), rot(-10, 4), rot(-38, 6), 6)

        # --- Rider ---
        # Torso leans with bike; slight independent lean opposite to rotation for style
        hip = rot(-16, -14)
        shoulder = rot(-4, -34)
        head_c = rot(2, -44)
        hand = rot(30, -20)
        foot = rot(6, 2)

        pygame.draw.line(surface, RIDER_SUIT, hip, shoulder, 10)
        pygame.draw.line(surface, RIDER_SUIT, hip, foot, 9)
        pygame.draw.line(surface, RIDER_SUIT, shoulder, hand, 8)
        pygame.draw.line(surface, RIDER_ACCENT, hip, shoulder, 3)

        pygame.draw.circle(surface, HELMET_COLOR, (int(head_c[0]), int(head_c[1])), 11)
        pygame.draw.circle(surface, DARK, (int(head_c[0]), int(head_c[1])), 11, 2)
        visor = rot(8, -44)
        pygame.draw.circle(surface, (40, 40, 45), (int(visor[0]), int(visor[1])), 5)

        # --- Wheels ---
        for body, shape in [(self.rear_body, self.rear_shape), (self.front_body, self.front_shape)]:
            wx, wy = body.position.x - cam_x, body.position.y - cam_y
            r = shape.radius
            pygame.draw.circle(surface, TIRE_COLOR, (int(wx), int(wy)), int(r))
            # tread marks
            for i in range(10):
                ta = body.angle + i * (2 * math.pi / 10)
                x1 = wx + math.cos(ta) * (r - 2)
                y1 = wy + math.sin(ta) * (r - 2)
                x2 = wx + math.cos(ta) * r
                y2 = wy + math.sin(ta) * r
                pygame.draw.line(surface, (10, 10, 10), (x1, y1), (x2, y2), 2)
            pygame.draw.circle(surface, RIM_COLOR, (int(wx), int(wy)), int(r * 0.45))
            pygame.draw.circle(surface, (140, 140, 145), (int(wx), int(wy)), int(r * 0.45), 2)
            for i in range(5):
                sa2 = body.angle + i * (2 * math.pi / 5)
                ex = wx + math.cos(sa2) * r * 0.42
                ey = wy + math.sin(sa2) * r * 0.42
                pygame.draw.line(surface, (120, 120, 125), (wx, wy), (ex, ey), 2)


# ---------------------- Collision handling ----------------------
contact_state = {"grounded": 0, "crash": False, "hazard": False, "impact_speed": 0.0}


def wheel_terrain_begin(arbiter, space, data):
    contact_state["grounded"] += 1
    try:
        contact_state["impact_speed"] = max(contact_state["impact_speed"], arbiter.total_ke ** 0.5)
    except Exception:
        pass


def wheel_terrain_separate(arbiter, space, data):
    contact_state["grounded"] = max(0, contact_state["grounded"] - 1)


def chassis_terrain_begin(arbiter, space, data):
    contact_state["crash"] = True


def hazard_begin(arbiter, space, data):
    contact_state["hazard"] = True


if hasattr(space, "on_collision"):
    space.on_collision(COLL_WHEEL, COLL_TERRAIN, begin=wheel_terrain_begin, separate=wheel_terrain_separate)
    space.on_collision(COLL_CHASSIS, COLL_TERRAIN, begin=chassis_terrain_begin)
    space.on_collision(COLL_WHEEL, COLL_HAZARD, begin=hazard_begin)
    space.on_collision(COLL_CHASSIS, COLL_HAZARD, begin=hazard_begin)
else:
    def _wrap(fn):
        def inner(a, s, d):
            fn(a, s, d)
            return True
        return inner

    h1 = space.add_collision_handler(COLL_WHEEL, COLL_TERRAIN)
    h1.begin = _wrap(wheel_terrain_begin)
    h1.separate = wheel_terrain_separate

    h2 = space.add_collision_handler(COLL_CHASSIS, COLL_TERRAIN)
    h2.begin = _wrap(chassis_terrain_begin)

    h3 = space.add_collision_handler(COLL_WHEEL, COLL_HAZARD)
    h3.begin = _wrap(hazard_begin)

    h4 = space.add_collision_handler(COLL_CHASSIS, COLL_HAZARD)
    h4.begin = _wrap(hazard_begin)

# ---------------------- Particles ----------------------
particles = []


def spawn_dust(x, y, n=2):
    for _ in range(n):
        particles.append([x, y, random.uniform(-50, 50), random.uniform(-70, -10), 0.5, SAND_DARK, 4])


def spawn_explosion(x, y):
    for _ in range(34):
        ang = random.uniform(0, math.pi * 2)
        spd = random.uniform(90, 340)
        particles.append([x, y, math.cos(ang) * spd, math.sin(ang) * spd, random.uniform(0.4, 0.95),
                           random.choice([RED, TANK_COLOR, YELLOW]), 5])


def update_particles(dt):
    for p in particles[:]:
        p[0] += p[2] * dt
        p[1] += p[3] * dt
        p[3] += 520 * dt
        p[4] -= dt
        if p[4] <= 0:
            particles.remove(p)


def draw_particles(surface, cam_x, cam_y):
    for p in particles:
        size = max(1, int(p[4] * p[6]))
        pygame.draw.circle(surface, p[5], (int(p[0] - cam_x), int(p[1] - cam_y)), size)


# ---------------------- Game state ----------------------
bike = Bike(0)
last_checkpoint_x = 0
cam_x, cam_y = 0.0, 0.0
cam_shake = 0.0
elapsed = 0.0
timer_running = True
crash_timer = 0.0
slowmo_timer = 0.0
prev_grounded = False

# ---------------------- Main loop ----------------------
running = True
while running:
    real_dt = clock.tick(FPS) / 1000.0
    real_dt = min(real_dt, 1 / 30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_r:
                bike.respawn(last_checkpoint_x)
                contact_state.update(crash=False, hazard=False, grounded=0, impact_speed=0.0)
                crash_timer = 0.0
                slowmo_timer = 0.0

    keys = pygame.key.get_pressed()

    # Slow-motion time scale on crash impact
    dt = real_dt
    if slowmo_timer > 0:
        dt = real_dt * 0.25
        slowmo_timer -= real_dt

    if not bike.crashed and not bike.finished:
        bike.grounded_wheels = contact_state["grounded"]
        bike.update_controls(keys, dt)

        if timer_running:
            elapsed += dt

        bx = bike.chassis_body.position.x
        for cx_pt in CHECKPOINT_XS:
            if bx >= cx_pt > last_checkpoint_x:
                last_checkpoint_x = cx_pt

        now_grounded = contact_state["grounded"] > 0
        if now_grounded and abs(bike.chassis_body.velocity.x) > 40:
            spawn_dust(bike.rear_body.position.x, bike.rear_body.position.y + 10)

        # Landing impact -> dust burst + camera shake
        if now_grounded and not prev_grounded:
            impact = contact_state["impact_speed"]
            if impact > 300:
                spawn_dust(bike.rear_body.position.x, bike.rear_body.position.y + 10, n=10)
                spawn_dust(bike.front_body.position.x, bike.front_body.position.y + 10, n=6)
                cam_shake = min(14, impact / 120)
        prev_grounded = now_grounded
        contact_state["impact_speed"] = 0.0

        hard_hit = contact_state["crash"] and bike.is_bad_angle()
        fell_in_gap = bike.chassis_body.position.y > 900
        if hard_hit or contact_state["hazard"] or fell_in_gap:
            bike.crashed = True
            spawn_explosion(bike.chassis_body.position.x, bike.chassis_body.position.y)
            crash_timer = 1.1
            slowmo_timer = 0.35
            cam_shake = 18

        if bx >= FINISH_X:
            bike.finished = True
            timer_running = False

        space.step(dt)
        contact_state["crash"] = False
        contact_state["hazard"] = False
    else:
        crash_timer -= real_dt
        if crash_timer <= 0 and bike.crashed:
            bike.respawn(last_checkpoint_x)
            contact_state["grounded"] = 0
            prev_grounded = False

    update_particles(dt)
    cam_shake = max(0.0, cam_shake - 40 * real_dt)

    target_cam_x = bike.chassis_body.position.x - WIDTH * 0.35
    target_cam_y = bike.chassis_body.position.y - HEIGHT * 0.55
    cam_x += (target_cam_x - cam_x) * min(1, 6 * real_dt)
    cam_y += (target_cam_y - cam_y) * min(1, 6 * real_dt)
    cam_y = max(-150, min(150, cam_y))

    shake_x = random.uniform(-cam_shake, cam_shake)
    shake_y = random.uniform(-cam_shake, cam_shake)
    draw_cam_x = cam_x + shake_x
    draw_cam_y = cam_y + shake_y

    # ---------------------- Draw ----------------------
    for i in range(HEIGHT):
        t = i / HEIGHT
        col = tuple(int(SKY_TOP[c] + (SKY_BOTTOM[c] - SKY_TOP[c]) * t) for c in range(3))
        pygame.draw.line(screen, col, (0, i), (WIDTH, i))

    pygame.draw.circle(screen, SUN_COLOR, (int(760 - draw_cam_x * 0.05), 90), 46)

    # Ocean band + distant palm trees (parallax)
    ocean_y = 430
    pygame.draw.rect(screen, OCEAN, (0, ocean_y - draw_cam_y * 0.3, WIDTH, 200))
    for hx in range(-200, 3000, 260):
        sx = hx - draw_cam_x * 0.35
        base_y = ocean_y - draw_cam_y * 0.35
        pygame.draw.rect(screen, PALM_TRUNK, (sx - 3, base_y - 60, 6, 60))
        for a in range(5):
            ang = a * (math.pi * 2 / 5) - math.pi / 2
            lx = sx + math.cos(ang) * 26
            ly = base_y - 60 + math.sin(ang) * 14
            pygame.draw.line(screen, PALM_LEAF, (sx, base_y - 60), (lx, ly), 6)

    # Sand ground fill
    ground_poly = [(p[0] - draw_cam_x, p[1] - draw_cam_y) for p in TERRAIN_POINTS]
    filled = ground_poly + [(ground_poly[-1][0], HEIGHT + 50), (ground_poly[0][0], HEIGHT + 50)]
    if len(filled) >= 3:
        pygame.draw.polygon(screen, SAND_NEAR, filled)
    for i in range(len(TERRAIN_POINTS) - 1):
        p1, p2 = TERRAIN_POINTS[i], TERRAIN_POINTS[i + 1]
        in_gap = any(p1[0] >= g[0] - 1 and p2[0] <= g[1] + 1 for g in GAPS)
        if in_gap:
            continue
        a = (p1[0] - draw_cam_x, p1[1] - draw_cam_y)
        b = (p2[0] - draw_cam_x, p2[1] - draw_cam_y)
        pygame.draw.line(screen, SAND_DARK, a, b, 8)
        pygame.draw.line(screen, SAND_FAR, a, b, 3)

    for sx in SPIKES:
        gy = ground_y_at(sx)
        tri = [(sx - 14 - draw_cam_x, gy - draw_cam_y), (sx + 14 - draw_cam_x, gy - draw_cam_y),
               (sx - draw_cam_x, gy - 30 - draw_cam_y)]
        pygame.draw.polygon(screen, RED, tri)
        pygame.draw.polygon(screen, (120, 20, 20), tri, 2)

    for cx_pt in CHECKPOINT_XS:
        gy = ground_y_at(cx_pt)
        pole = (cx_pt - draw_cam_x, gy - draw_cam_y)
        pygame.draw.line(screen, DARK, pole, (pole[0], pole[1] - 60), 3)
        color = ACCENT if cx_pt <= last_checkpoint_x else WHITE
        pygame.draw.polygon(screen, color, [(pole[0], pole[1] - 60), (pole[0] + 22, pole[1] - 50), (pole[0], pole[1] - 40)])

    fy = ground_y_at(FINISH_X)
    fx = FINISH_X - draw_cam_x
    for i in range(6):
        col = WHITE if i % 2 == 0 else DARK
        pygame.draw.rect(screen, col, (fx - 3, fy - draw_cam_y - (i + 1) * 15, 6, 15))

    draw_particles(screen, draw_cam_x, draw_cam_y)
    bike.draw(screen, draw_cam_x, draw_cam_y)

    t_text = font.render(f"Time: {elapsed:0.2f}s", True, DARK)
    screen.blit(t_text, (12, 10))
    hint = font.render("R = restart from checkpoint", True, DARK)
    screen.blit(hint, (12, 36))

    if bike.crashed:
        msg = big_font.render("CRASHED!", True, RED)
        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 60))
    if bike.finished:
        msg = big_font.render(f"FINISHED! {elapsed:0.2f}s", True, ACCENT)
        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 60))
        sub = font.render("Press R to race again", True, DARK)
        screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 - 10))

    pygame.display.flip()

pygame.quit()
sys.exit()