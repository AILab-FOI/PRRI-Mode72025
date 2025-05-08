import pygame as pg
import numpy as np
import random

class Projectile:
    def __init__(self, pos, direction, speed=0.08, max_distance=15):
        self.pos = np.array(pos, dtype=np.float32)
        self.direction = np.array(direction, dtype=np.float32)
        self.speed = speed
        self.start_pos = np.array(pos, dtype=np.float32)
        self.max_distance = max_distance
        self.active = True

    def update(self):
        self.pos += self.direction * self.speed
        if np.linalg.norm(self.pos - self.start_pos) > self.max_distance:
            self.active = False

    def draw(self, screen, mode7):
        screen_x, screen_y, scale = mode7.project(self.pos)
        if scale > 0:
            radius = max(2, scale // 20)
            pg.draw.circle(screen, (255, 0, 0), (int(screen_x), int(screen_y)), radius)

class Enemy:
    def __init__(self, pos, speed=0.02, min_distance=2.0):
        self.pos = np.array(pos, dtype=np.float32)
        self.speed = speed
        self.alive = True
        self.min_distance = min_distance
        self.texture = pg.image.load('textures/airship_1.png').convert_alpha()
        self.bullets = []
        self.hit_timer = 0
        self.hp = 100
        self.shoot_delay = 350
        self.shoot_timer = random.randint(0, self.shoot_delay)

    def update(self, player_pos):
        direction = player_pos - self.pos
        distance = np.linalg.norm(direction)

        if distance < self.min_distance:
            direction /= distance
            self.pos -= direction * self.speed
        else:
            direction /= distance
            self.pos += direction * self.speed

        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            self.shoot(player_pos)
            self.shoot_timer = self.shoot_delay

        for bullet in self.bullets:
            bullet.update()
        self.bullets = [b for b in self.bullets if b.active]

    def shoot(self, player_pos):
        direction = player_pos - self.pos
        norm = np.linalg.norm(direction)
        if norm == 0:
            return
        direction = direction / norm
        bullet = Projectile(self.pos.copy(), direction, speed=0.08)
        self.bullets.append(bullet)

    def draw(self, screen, mode7):
        screen_x, screen_y, scale = mode7.project(self.pos)

        if scale > 0:
            scaled_texture = pg.transform.scale(self.texture, (scale, scale))
            screen.blit(scaled_texture, (int(screen_x) - scale // 2, int(screen_y) - scale // 2))

            hp_bar_width = scale
            hp_bar_rect = pg.Rect(int(screen_x - hp_bar_width / 2), int(screen_y - scale // 2 - 10),
                                  int(hp_bar_width), 5)
            pg.draw.rect(screen, (100, 0, 0), hp_bar_rect)
            hp_ratio = self.hp / 100
            green_bar_width = int(hp_bar_rect.width * hp_ratio)
            green_rect = pg.Rect(hp_bar_rect.x, hp_bar_rect.y, green_bar_width, hp_bar_rect.height)
            pg.draw.rect(screen, (0, 255, 0), green_rect)

        for bullet in self.bullets:
            bullet.draw(screen, mode7)

    def check_collision(self, projectile):
        if np.linalg.norm(self.pos - projectile.pos) < 0.6:
            self.hit_timer = 10
            self.hp -= 50
            if self.hp <= 0:
                self.alive = False
            return True
        return False
