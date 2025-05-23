import pygame as pg
import sys
import time
from settings import WIN_RES, MENU, GAME
from mode7 import *
from game import Game
from menu import Menu
from weapons import *
from player import Player
from results import ResultsScreen

class App:
    def __init__(self):
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode(WIN_RES)
        self.clock = pg.time.Clock()
        self.mode7 = Mode7(self)
        self.player = Player()
        self.game = Game(self.mode7, self.player, self)
        self.menu = Menu(self)
        self.state = MENU
        self.speed_multiplier = 1.0
        self.speed_timer = 0
        self.minigun_last_shot = 0
        self.weapon = REVOLVER
        self.weapon_timer = 0
        self.powerup_icon = pg.image.load("textures/Steampunk_valve_and_pipe.png").convert_alpha()
        self.powerup_icon = pg.transform.scale(self.powerup_icon, (128, 128))
        self.powerup_sound = pg.mixer.Sound("music/Timer.mp3")




        self.start_time = time.time()
        self.enemies_killed = 0
        self.results_screen = None
        self.weapon_icons = {
            REVOLVER: pg.image.load("textures/revolver_steampunk.png").convert_alpha(),
            SHOTGUN: pg.image.load("textures/shotgun_steampunk.png").convert_alpha(),
            MINIGUN: pg.image.load("textures/minigun_steampunk.png").convert_alpha(),
        }

        self.progression_box = pg.image.load("textures/progression_blank.png").convert_alpha()
        self.progression_box = pg.transform.scale(self.progression_box, (200, 200))  # prilagodi veličinu

        original_full = pg.image.load("textures/steampunk_bar_full.png").convert_alpha()
        scale_factor = 0.2
        self.bar_full = pg.transform.scale(original_full, (
        int(original_full.get_width() * scale_factor), int(original_full.get_height() * scale_factor)))

        original_speed = pg.image.load("textures/powerup_bar.png").convert_alpha()
        scale_factor = 0.1
        scaled_speed = pg.transform.scale(original_speed, (
            int(original_speed.get_width() * scale_factor),
            int(original_speed.get_height() * scale_factor)
        ))

        self.bar_speed = pg.transform.rotate(scaled_speed, 90)  # rotiraj za 90° udesno

        for key in self.weapon_icons:
            self.weapon_icons[key] = pg.transform.scale(self.weapon_icons[key], (80, 80))
        self.weapon_frame = pg.image.load("textures/UI_frame_static.png").convert_alpha()
        self.weapon_frame = pg.transform.scale(self.weapon_frame, (300, 200))
        self.shooting = False
        self.shotgun_sound = pg.mixer.Sound("music/shotgun sound effect.mp3")
        self.health_sound = pg.mixer.Sound("music/HP UP.mp3")
        pg.mixer.music.load("music/Pixel Pulse.mp3")
        pg.mixer.music.set_volume(0.5)
        pg.mixer.music.play(-1, 0.0)
        
    def apply_speed_boost(self, multiplier, duration=5):
        self.speed_multiplier = multiplier
        self.speed_timer = time.time() + duration
        print(f"[SPEED] Boost applied: x{multiplier} fo r {duration}s")



    def show_results_screen(self):
        time_survived = int(time.time() - self.start_time)
        enemies_killed = self.enemies_killed
        waves_survived = self.game.wave

        results_screen = ResultsScreen(self.screen, time_survived, enemies_killed, waves_survived)
        results_screen.update()
        results_screen.draw()


#    def game_over_screen(self):
#        time_survived = int(time.time() - self.start_time)
#        enemies_killed = self.enemies_killed
#        waves_survived = self.game.wave

#        results_screen = ResultsScreen(self.screen, time_survived, enemies_killed, waves_survived)
#        
#        while not results_screen.is_done():
#            results_screen.update()
#            results_screen.draw()
#            pg.time.Clock().tick(60)
#        self.wait_for_input_after_game_over()

    def wait_for_input_after_game_over(self):
        waiting_for_input = True
        while waiting_for_input:
            for event in pg.event.get():
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                    pg.quit()
                    sys.exit()
                elif event.type == pg.KEYDOWN and event.key == pg.K_r:
                    self.__init__()
                    self.state = MENU
                    waiting_for_input = False
                elif event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                    self.state = MENU
                    waiting_for_input = False

    def update(self):
        if self.state == MENU:
            self.menu.update()
        # Reset weapon after timer
        if self.weapon != REVOLVER and time.time() > self.weapon_timer:
            self.weapon = REVOLVER
            print("[TIMER] Power-up expired")
        elif self.state == GAME:
            if self.player.is_dead():
                self.powerup_sound.stop()
                self.state = GAME_OVER
                self.results_screen = ResultsScreen(
                    self.screen,
                    int(time.time() - self.start_time),
                    self.enemies_killed,
                    self.game.wave
                )
                return
            player_pos = self.mode7.pos
            self.mode7.update()
            self.game.update(player_pos)
            if hasattr(self, 'weapon_timer') and time.time() > self.weapon_timer:
                self.weapon = REVOLVER
                del self.weapon_timer
            if self.weapon == MINIGUN and self.shooting:
                now = time.time()
                if now - self.minigun_last_shot > 0.1:
                    self.shotgun_sound.play()
                    self.game.shoot_minigun(self.mode7.pos, self.mode7.angle)
                    self.minigun_last_shot = now
            self.clock.tick()
            pg.display.set_caption(f'{self.clock.get_fps():.1f}')
            if self.speed_multiplier != 1.0 and time.time() > self.speed_timer:
                self.speed_multiplier = 1.0
                print("[SPEED] Boost expired")


        elif self.state == GAME_OVER:
            pass



    def draw_ui(self):
        # Lokacija i prikaz okvira
        box_x, box_y = 20, 20
        self.screen.blit(self.progression_box, (box_x, box_y))

        # Font i boja
        font = pg.font.Font("fonts/steampunk-mainmenu.ttf", 20)
        color = (255, 220, 180)

        # Tekstovi
        wave_text = font.render(f"Wave: {self.game.wave}", True, color)
        enemy_label = font.render("Enemies:", True, color)
        enemy_number = font.render(str(len(self.game.enemies)), True, color)

        # Pozicije
        text_x = box_x + 70
        wave_y = box_y + 65
        enemy_y = box_y + 100
        enemy_number_y = enemy_y + 25  # ispod "Enemies:"

        # Crtanje
        self.screen.blit(wave_text, (text_x, wave_y))
        self.screen.blit(enemy_label, (text_x, enemy_y))
        self.screen.blit(enemy_number, (text_x + 25, enemy_number_y))  # lagani pomak desno

        self.player.draw_health(self.screen)
        # Show icon if powerup is active

        #if self.weapon != REVOLVER and time.time() < self.weapon_timer:
         #   self.screen.blit(self.powerup_icon, (1115, 200))  # pozicija ikone

        if self.weapon != REVOLVER and time.time() < self.weapon_timer:
            x, y = 85, 600
            total = 10  # trajanje
            remaining = self.weapon_timer - time.time()
            percent = max(0, min(1, remaining / total))

            full_width = int(self.bar_full.get_width() * percent)
            if full_width > 0:
                bar_clip = self.bar_full.subsurface(
                    (0, 0, full_width, self.bar_full.get_height())
                )
                self.screen.blit(bar_clip, (x, y))

        if self.speed_multiplier > 1.0 and time.time() < self.speed_timer:
            x2, y2 = 1440, 180  # Lokacija gdje želiš prikazati bar
            total = 5.4
            remaining = self.speed_timer - time.time()
            percent = max(0, min(1, remaining / total))

            full_height = int(self.bar_speed.get_height() * percent)
            if full_height > 0:

                bar_clip = self.bar_speed.subsurface(
                    (0, self.bar_speed.get_height() - full_height, self.bar_speed.get_width(), full_height)
                )
                rotated_clip = pg.transform.rotate(bar_clip, 0)
                self.screen.blit(rotated_clip, (x2, y2 + (self.bar_speed.get_height() - full_height)))

    def draw_weapon_ui(self):
        padding = 20
        frame_width, frame_height = self.weapon_frame.get_size()
        x = padding
        y = self.screen.get_height() - frame_height - padding
        if x + frame_width > self.screen.get_width():
            x = self.screen.get_width() - frame_width
        if y + frame_height > self.screen.get_height():
            y = self.screen.get_height() - frame_height
        frame_rect = self.weapon_frame.get_rect()
        frame_rect.topleft = (x, y)
        self.screen.blit(self.weapon_frame, frame_rect)
        icon = self.weapon_icons[self.weapon]
        icon = pg.transform.scale(icon, (128, 128))
        icon_x = frame_rect.x + (frame_rect.width - icon.get_width()) // 2
        icon_y = frame_rect.y + (frame_rect.height - icon.get_height()) // 2
        self.screen.blit(icon, (icon_x, icon_y))

    def draw(self):
        if self.state == MENU:
            self.menu.draw()
        elif self.state == GAME:
            self.mode7.draw()
            self.game.draw(self.screen)
            self.draw_ui()
            self.draw_weapon_ui()
            pg.display.flip()
        elif self.state == GAME_OVER:
            if self.results_screen:
                self.results_screen.update()
                self.results_screen.draw()

    def check_event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            if self.state == MENU and event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                self.__init__()
                self.state = GAME
                self.switch_to_game()
            elif self.state == GAME_OVER:
                if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                    self.__init__()
                    self.state = MENU
                    self.results_screen = None
            elif self.state == GAME and self.player.is_dead() and event.type == pg.KEYDOWN and event.key == pg.K_r:
                self.__init__()
#            elif event.type == pg.KEYDOWN and event.key == pg.K_j:
#                self.weapon = REVOLVER
#            elif event.type == pg.KEYDOWN and event.key == pg.K_k:
#                self.weapon = SHOTGUN
#            elif event.type == pg.KEYDOWN and event.key == pg.K_l:
#                self.weapon = MINIGUN
            elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                self.shooting = True
                direction = np.array([np.cos(self.mode7.angle), np.sin(self.mode7.angle)])
                if self.weapon == REVOLVER:
                    self.shotgun_sound.play()
                    self.game.shoot_revolver(self.mode7.pos, self.mode7.angle)
                elif self.weapon == SHOTGUN:
                    self.shotgun_sound.play()
                    self.game.shoot_shotgun(self.mode7.pos, self.mode7.angle)
                elif self.weapon == MINIGUN:
                    self.shotgun_sound.play()
                    self.game.shoot_minigun(self.mode7.pos, self.mode7.angle)
            elif event.type == pg.KEYUP and event.key == pg.K_SPACE:
                self.shooting = False

    def switch_to_game(self):
        pg.mixer.music.stop()
        pg.mixer.music.load("music/Pixel Forge.mp3")
        pg.mixer.music.set_volume(0.5)
        pg.mixer.music.play(-1, 0.0)

    def apply_powerup(self, weapon_type):
        print(f"[POWERUP] Weapon set to {weapon_type}")
        self.weapon = weapon_type
        self.weapon_timer = time.time() + 10
        self.powerup_sound.stop()
        self.powerup_sound.play()

    def run(self):
        while True:
            self.check_event()
            self.update()
            self.draw()
            pg.display.flip()

if __name__ == "__main__":
    app = App()
    app.run()

