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
        self.minigun_last_shot = 0
        self.weapon = REVOLVER
        self.start_time = time.time()
        self.enemies_killed = 0
        self.results_screen = None
        self.weapon_icons = {
            REVOLVER: pg.image.load("textures/revolver_steampunk.png").convert_alpha(),
            SHOTGUN: pg.image.load("textures/shotgun_steampunk.png").convert_alpha(),
            MINIGUN: pg.image.load("textures/minigun_steampunk.png").convert_alpha(),
        }
        for key in self.weapon_icons:
            self.weapon_icons[key] = pg.transform.scale(self.weapon_icons[key], (80, 80))
        self.weapon_frame = pg.image.load("textures/UI_frame_static.png").convert_alpha()
        self.weapon_frame = pg.transform.scale(self.weapon_frame, (300, 100))
        self.shooting = False
        self.shotgun_sound = pg.mixer.Sound("music/shotgun sound effect.mp3")
        pg.mixer.music.load("music/Pixel Pulse.mp3")
        pg.mixer.music.set_volume(0.5)
        pg.mixer.music.play(-1, 0.0)

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
        elif self.state == GAME:
            if self.player.is_dead():
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
        elif self.state == GAME_OVER:
            pass


    def draw_ui(self):
        font = pg.font.SysFont('Arial', 24)
        wave_text = font.render(f"Wave: {self.game.wave}", True, (255, 255, 255))
        self.screen.blit(wave_text, (10, 10))

        enemy_count = len(self.game.enemies)
        enemy_text = font.render(f"Enemies: {enemy_count}", True, (255, 255, 255))
        self.screen.blit(enemy_text, (10, 40))

        self.player.draw_health(self.screen)

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
        icon = pg.transform.scale(icon, (64, 64))
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

    def run(self):
        while True:
            self.check_event()
            self.update()
            self.draw()
            pg.display.flip()

if __name__ == "__main__":
    app = App()
    app.run()
