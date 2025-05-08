import pygame as pg
import numpy as np
import time 
from weapons import SHOTGUN, MINIGUN

class Drop:
    def __init__(self, pos):
        self.pos = np.array(pos, dtype=np.float32)
        self.collected = False
        self.texture = pg.Surface((20, 20))  # Placeholder, can replace with textures

    def update(self, player_pos):
        if np.linalg.norm(self.pos - player_pos) < 0.6:
            self.on_pickup()
            self.collected = True

    def draw(self, screen, mode7):
        screen_x, screen_y, scale = mode7.project(self.pos)
        if scale > 0:
            scaled_texture = pg.transform.scale(self.texture, (scale, scale))
            screen.blit(scaled_texture, (int(screen_x) - scale // 2, int(screen_y) - scale // 2))

    def on_pickup(self):
        pass


class HealthDrop(Drop):
    def __init__(self, pos, player):
        super().__init__(pos)
        self.texture.fill((0, 255, 0))  # Green box for now
        self.player = player

    def on_pickup(self):
        print("[DROP] Picked up health drop!")
        if self.player.health < self.player.max_health:
            self.player.health += 1


class ShotgunDrop(Drop):
    def __init__(self, pos, app):
        super().__init__(pos)
        self.texture = pg.image.load("textures/shotgun_steampunk.png").convert_alpha()
        self.app = app

    def on_pickup(self):
        print("[DROP] Picked up shotgun drop!")
        self.app.weapon = SHOTGUN
        self.app.weapon_timer = time.time() + 5




class MinigunDrop(Drop):
    def __init__(self, pos, app):
        super().__init__(pos)
        self.texture = pg.image.load("textures/minigun_steampunk.png").convert_alpha()
        self.app = app

    def on_pickup(self):
        print("[DROP] Picked up minigun drop!")
        self.app.weapon = MINIGUN
        self.app.weapon_timer = time.time() + 5


