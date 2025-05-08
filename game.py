import pygame as pg
import numpy as np
import random
from drops import HealthDrop, ShotgunDrop, MinigunDrop
from enemies import Enemy

class Projectile:
    def __init__(self, player_pos, player_angle, speed=0.5, max_distance=20):
        player_angle = np.radians(player_angle) if player_angle > np.pi * 2 else player_angle

        direction_x = np.cos(player_angle - np.pi/2)
        direction_y = -np.sin(player_angle - np.pi/2)
        self.direction = np.array([direction_x, direction_y], dtype=np.float32)

        offset_distance = 2.0
        rotated_offset_x = offset_distance * direction_x
        rotated_offset_y = offset_distance * direction_y

        self.pos = np.array(player_pos, dtype=np.float32) + np.array([rotated_offset_x, rotated_offset_y])
        self.speed = speed
        self.max_distance = max_distance
        self.start_pos = np.array(self.pos, dtype=np.float32)
        self.active = True
        #self.app = app

    def update(self):
        self.pos += self.direction * self.speed
        if np.linalg.norm(self.pos - self.start_pos) > self.max_distance:
            self.active = False

    def draw(self, screen, mode7):
        screen_x, screen_y, scale = mode7.project(self.pos)
        if scale > 0:
            radius = max(2, scale // 15)
            pg.draw.circle(screen, (0, 0, 0), (int(screen_x), int(screen_y)), radius)

class Game:
    def __init__(self, mode7, player, app):
        self.mode7 = mode7
        self.player = player
        self.app = app
        self.projectiles = []
        self.enemies = []
        self.drops = []
        self.wave = 1
        self.wave_sound = pg.mixer.Sound("music/Level up.mp3")
        self.spawn_wave(self.wave)


    def spawn_wave(self, wave_num):
        self.enemies.clear()
        for _ in range(5 + wave_num * 2):
            x, y = random.uniform(-10, 10), random.uniform(-10, 10)
            self.enemies.append(Enemy((x, y)))
        if wave_num == 5:
            self.mode7.set_textures('textures/sky_cloudyday_lowres.png', 'textures/ground_sand_lowres.png')
        elif wave_num == 10:
            self.mode7.set_textures('textures/polluted_sky_lowres.png', 'textures/groubd_volcan_lowres.png')

        match wave_num:
            case 3:
                self.mode7.set_textures('textures/sky_cloudyday_lowres.png', 'textures/ground_sand_lowres.png')
            case 6:
                self.mode7.set_textures('textures/polluted_sky_lowres.png', 'textures/groubd_volcan_lowres.png')
            case 9:
                self.mode7.set_textures('textures/sky_cloudynight_lowres.png', 'textures/ground_snow_lowres.png')
            case 12:
                self.mode7.set_textures('textures/sky_lowres.png', 'textures/ground_grass_lowres.png')
            case 15:
                self.mode7.set_textures('textures/sky_cloudyday_lowres.png', 'textures/ground_frozenice_lowres.png')
            case 18:
                self.mode7.set_textures('textures/sky_cloudyday_lowres.png', 'textures/ground_swamp_lowres.png')
            case 21:
                self.mode7.set_textures('textures/sky_night_lowres.png', 'textures/ground_factoryfloor_lowres.png')
            case 24:
                self.mode7.set_textures('textures/sky_cloudynight_lowres.png', 'textures/ground_town_lowres.png')
            case 27:
                self.mode7.set_textures('textures/polluted_sky_lowres.png', 'textures/ground_gravel_lowres.png')
            case 30:
                self.mode7.set_textures('textures/sky_lowres.png', 'textures/ground_rail_lowres.png')
            case 33:
                self.mode7.set_textures('textures/sky_cloudyday_lowres.png', 'textures/ground_graveldirt_lowres.png')
            case 36:
                self.mode7.set_textures('textures/sky_night_lowres.png', 'textures/ground_halfsnow_lowres.png')
            case 39:
                self.mode7.set_textures('textures/sky_lowres.png', 'textures/ground_sea_lowres.png')
            case 42:
                self.mode7.set_textures('textures/sky_cloudyday_lowres.png', 'textures/ground_dirt_lowres.png')
            case _:
                pass

    def update(self, player_pos):
        for proj in self.projectiles:
            proj.update()

        for proj in self.projectiles:
            for enemy in self.enemies:
                if enemy.check_collision(proj):
                    proj.active = False
                    if not enemy.alive:
                        self.app.enemies_killed += 1
                        if random.random() < 0.3:
                            drop_type = random.choice([HealthDrop, ShotgunDrop, MinigunDrop])
                            pos = enemy.pos.copy()
                            if drop_type == HealthDrop:
                                self.drops.append(HealthDrop(pos, self.player, self.app))
                            else:
                                self.drops.append(drop_type(pos, self.app))

        self.projectiles = [p for p in self.projectiles if p.active]

        for enemy in self.enemies:
            enemy.update(player_pos)
            for bullet in enemy.bullets:
                if np.linalg.norm(np.array(player_pos) - bullet.pos) < 0.5:
                    self.player.take_damage(1)
                    bullet.active = False

        self.enemies = [e for e in self.enemies if e.alive]

        for drop in self.drops:
            drop.update(player_pos)

        self.drops = [d for d in self.drops if not d.collected]

        if len(self.enemies) == 0:
            self.wave += 1
            self.spawn_wave(self.wave)

    def draw(self, screen):
        for proj in self.projectiles:
            proj.draw(screen, self.mode7)
        for enemy in self.enemies:
            enemy.draw(screen, self.mode7)
        for drop in self.drops:
            drop.draw(screen, self.mode7)


    def shoot_revolver(self, pos, angle):
        self.projectiles.append(Projectile(pos, angle, speed=0.6))

    def shoot_shotgun(self, pos, angle):
        for spread in [-0.2, 0, 0.2]:
            self.projectiles.append(Projectile(pos, angle + spread, speed=0.5))

    def shoot_minigun(self, pos, angle):
        self.projectiles.append(Projectile(pos, angle, speed=0.5))