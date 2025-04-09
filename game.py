import pygame as pg
import numpy as np
import random
from enemies import *; 

class Projectile:
    def __init__(self, player_pos, player_angle, speed=0.5, max_distance=20):
        # Convert angle to radians if necessary
        player_angle = np.radians(player_angle) if player_angle > np.pi * 2 else player_angle
        
        # Compute direction relative to player rotation (correcting for 90-degree offset)
        direction_x = np.cos(player_angle - np.pi/2)
        direction_y = -np.sin(player_angle - np.pi/2)
        self.direction = np.array([direction_x, direction_y], dtype=np.float32)
        
        # Offset projectile position relative to player orientation
        offset_distance = 2.0
        rotated_offset_x = offset_distance * direction_x
        rotated_offset_y = offset_distance * direction_y
        
        self.pos = np.array(player_pos, dtype=np.float32) + np.array([rotated_offset_x, rotated_offset_y])
        self.speed = speed
        self.max_distance = max_distance
        self.start_pos = np.array(self.pos, dtype=np.float32)
        self.active = True

    def update(self):
        self.pos += self.direction * self.speed

        if np.linalg.norm(self.pos - self.start_pos) > self.max_distance:
            self.active = False

    
    def draw(self, screen, mode7):
        screen_x, screen_y, scale = mode7.project(self.pos)
        
        # Calculate projectile size based on distance traveled (larger at spawn, smaller as it moves)
        distance_traveled = np.linalg.norm(self.pos - self.start_pos)
        initial_size = 9  # Size at spawn
        min_size = 1  # Smallest size when far away
        size = max(min_size, initial_size - int(distance_traveled / self.max_distance * initial_size))
        
        pg.draw.circle(screen, (0, 0, 0), (int(screen_x), int(screen_y)), size)  # Blue projectile for better visibility


class Game:
    def __init__(self, mode7):
        self.mode7 = mode7
        self.enemies = [Enemy((5, 5)), Enemy((-5, 2)), Enemy((5, -5)), Enemy((-5, -2))]  # Example enemies
        self.projectiles = []
    
    def update(self, player_pos):
        for enemy in self.enemies:
            enemy.update(player_pos)
        for projectile in self.projectiles:
            projectile.update()
        
        # Check collisions and remove hit enemies
        for projectile in self.projectiles:
            for enemy in self.enemies:
                if enemy.check_collision(projectile):
                    self.enemies.remove(enemy)
                    projectile.active = False
                    break
        
        self.projectiles = [p for p in self.projectiles if p.active]  # Remove inactive projectiles
    
    def draw(self, screen):
        for enemy in self.enemies:
            enemy.draw(screen, self.mode7)
        for projectile in self.projectiles:
            projectile.draw(screen, self.mode7)
    
    def shoot_revolver(self, player_pos, player_angle):
        self.projectiles.append(Projectile(player_pos, player_angle))

    #Evenly distributed shotgun pellets
    #def shoot_shotgun(self, player_pos, player_angle, num_pellets=5, spread_degrees=30):
    #    spread_rad = np.radians(spread_degrees)
     #   base_angle = player_angle
     #   for i in range(num_pellets):
     #       t = i / (num_pellets - 1) if num_pellets > 1 else 0.5
     #       offset = spread_rad * (t - 0.5)
     #       pellet_angle = base_angle + offset
     #       proj = Projectile(player_pos, pellet_angle)
     #       self.projectiles.append(proj)
            
    def shoot_minigun(self, player_pos, player_angle):
        num_projectiles = 1
        spread = 3
        for i in range(num_projectiles):
            angle_offset = np.radians(np.random.uniform(-spread, spread))
            projectile_angle = player_angle + angle_offset
            proja = Projectile(player_pos, projectile_angle)
            self.projectiles.append(proja)

    def shoot_shotgun(self, player_pos, player_angle, num_pellets=5, spread_degrees=30):
        spread_rad = np.radians(spread_degrees)
        base_angle = player_angle
        for _ in range(num_pellets):
            offset = random.uniform(-spread_rad / 2, spread_rad / 2)
            pellet_angle = base_angle + offset
            proj = Projectile(player_pos, pellet_angle)
            self.projectiles.append(proj)

