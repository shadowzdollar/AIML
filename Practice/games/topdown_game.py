"""
Top-Down 2D Shooter - Pygame Starter
--------------------------------------
Controls:
  WASD or Arrow Keys - Move
  Mouse - Aim
  Left Click - Shoot
  ESC - Quit

Run with: python topdown_game.py
Requires: pip install pygame
"""

import pygame
import math
import random
import sys

# ---------------------- Setup ----------------------
pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 900, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Top-Down Shooter")
clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
RED = (220, 60, 60)
GREEN = (60, 200, 100)
YELLOW = (240, 220, 80)
GRAY = (60, 60, 60)

font = pygame.font.SysFont("consolas", 24)


# ---------------------- Player ----------------------
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 18
        self.speed = 4
        self.color = GREEN
        self.health = 100
        self.max_health = 100

    def handle_input(self, keys):
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1

        # Normalize diagonal movement so it isn't faster
        if dx != 0 or dy != 0:
            length = math.hypot(dx, dy)
            dx, dy = dx / length, dy / length

        self.x += dx * self.speed
        self.y += dy * self.speed

        # Keep player on screen
        self.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(SCREEN_HEIGHT - self.radius, self.y))

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        # Direction indicator toward mouse
        mx, my = pygame.mouse.get_pos()
        angle = math.atan2(my - self.y, mx - self.x)
        end_x = self.x + math.cos(angle) * (self.radius + 10)
        end_y = self.y + math.sin(angle) * (self.radius + 10)
        pygame.draw.line(surface, WHITE, (self.x, self.y), (end_x, end_y), 3)

    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0


# ---------------------- Bullet ----------------------
class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.speed = 10
        self.radius = 5
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed

    def update(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self, surface):
        pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), self.radius)

    def off_screen(self):
        return (
            self.x < 0 or self.x > SCREEN_WIDTH or
            self.y < 0 or self.y > SCREEN_HEIGHT
        )


# ---------------------- Enemy ----------------------
class Enemy:
    def __init__(self):
        # Spawn just outside the screen edges
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":
            self.x, self.y = random.randint(0, SCREEN_WIDTH), -30
        elif side == "bottom":
            self.x, self.y = random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + 30
        elif side == "left":
            self.x, self.y = -30, random.randint(0, SCREEN_HEIGHT)
        else:
            self.x, self.y = SCREEN_WIDTH + 30, random.randint(0, SCREEN_HEIGHT)

        self.radius = 16
        self.speed = random.uniform(1.2, 2.2)
        self.health = 30

    def update(self, target_x, target_y):
        angle = math.atan2(target_y - self.y, target_x - self.x)
        self.x += math.cos(angle) * self.speed
        self.y += math.sin(angle) * self.speed

    def draw(self, surface):
        pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), self.radius)

    def collides_with(self, x, y, radius):
        dist = math.hypot(self.x - x, self.y - y)
        return dist < self.radius + radius


# ---------------------- Game State ----------------------
def reset_game():
    return {
        "player": Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
        "bullets": [],
        "enemies": [],
        "score": 0,
        "spawn_timer": 0,
        "game_over": False,
    }


state = reset_game()

SHOOT_COOLDOWN = 15  # frames between shots
shoot_timer = 0

# ---------------------- Main Loop ----------------------
running = True
while running:
    dt = clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_r and state["game_over"]:
                state = reset_game()

    keys = pygame.key.get_pressed()
    mouse_buttons = pygame.mouse.get_pressed()

    if not state["game_over"]:
        player = state["player"]
        player.handle_input(keys)

        # Shooting
        shoot_timer = max(0, shoot_timer - 1)
        if mouse_buttons[0] and shoot_timer == 0:
            mx, my = pygame.mouse.get_pos()
            angle = math.atan2(my - player.y, mx - player.x)
            state["bullets"].append(Bullet(player.x, player.y, angle))
            shoot_timer = SHOOT_COOLDOWN

        # Update bullets
        for bullet in state["bullets"][:]:
            bullet.update()
            if bullet.off_screen():
                state["bullets"].remove(bullet)

        # Spawn enemies over time
        state["spawn_timer"] += 1
        spawn_rate = max(20, 60 - state["score"] // 5)  # gets harder over time
        if state["spawn_timer"] >= spawn_rate:
            state["spawn_timer"] = 0
            state["enemies"].append(Enemy())

        # Update enemies
        for enemy in state["enemies"][:]:
            enemy.update(player.x, player.y)

            # Enemy hits player
            if enemy.collides_with(player.x, player.y, player.radius):
                state["enemies"].remove(enemy)
                if player.take_damage(15):
                    state["game_over"] = True

            # Bullet hits enemy
            for bullet in state["bullets"][:]:
                if enemy.collides_with(bullet.x, bullet.y, bullet.radius):
                    if bullet in state["bullets"]:
                        state["bullets"].remove(bullet)
                    if enemy in state["enemies"]:
                        state["enemies"].remove(enemy)
                    state["score"] += 10
                    break

    # ---------------------- Draw ----------------------
    screen.fill(BLACK)

    # Simple grid background for depth
    for x in range(0, SCREEN_WIDTH, 40):
        pygame.draw.line(screen, GRAY, (x, 0), (x, SCREEN_HEIGHT), 1)
    for y in range(0, SCREEN_HEIGHT, 40):
        pygame.draw.line(screen, GRAY, (0, y), (SCREEN_WIDTH, y), 1)

    if not state["game_over"]:
        for bullet in state["bullets"]:
            bullet.draw(screen)
        for enemy in state["enemies"]:
            enemy.draw(screen)
        state["player"].draw(screen)

        # HUD
        score_text = font.render(f"Score: {state['score']}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Health bar
        hp = state["player"].health
        pygame.draw.rect(screen, GRAY, (10, 45, 200, 20))
        pygame.draw.rect(screen, RED, (10, 45, 200 * max(hp, 0) / state["player"].max_health, 20))
        hp_text = font.render(f"HP: {max(hp, 0)}", True, WHITE)
        screen.blit(hp_text, (220, 45))
    else:
        over_text = font.render(f"GAME OVER - Score: {state['score']}", True, WHITE)
        retry_text = font.render("Press R to restart, ESC to quit", True, WHITE)
        screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
        screen.blit(retry_text, (SCREEN_WIDTH // 2 - retry_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))

    pygame.display.flip()

pygame.quit()
sys.exit()
