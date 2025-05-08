import pygame as pg
import sys
from settings import WIN_RES, MENU, GAME

class Menu:
    def __init__(self, app):
        self.app = app
        
        self.font = pg.font.Font('fonts/steampunk-mainmenu.ttf', 74)
        self.background = pg.image.load('textures/BG_notext.png').convert()
        print("Background loaded.")

        button_width, button_height = 300, 60
        screen_width, screen_height = WIN_RES
        button_x = (screen_width - button_width) // 2
        button_y_start = (screen_height - 2 * button_height) // 2.5

        self.buttons = [
            {'text': 'Start game', 'rect': pg.Rect(button_x, button_y_start, button_width, button_height), 'action': self.start_game},
            {'text': 'Settings', 'rect': pg.Rect(button_x, button_y_start + (button_height + 50), button_width, button_height), 'action': self.exit_game},
            {'text': 'Exit', 'rect': pg.Rect(button_x, button_y_start + (button_height + 50)*2, button_width, button_height), 'action': self.exit_game}
        ]

    def start_game(self):
        print("Starting game.")
        self.app.state = GAME
        self.app.switch_to_game()

    def exit_game(self):
        pg.quit()
        sys.exit()

    def update(self):
        mouse_pos = pg.mouse.get_pos()
        for button in self.buttons:
            if button['rect'].collidepoint(mouse_pos):
                if pg.mouse.get_pressed()[0]:
                    button['action']()

    def draw(self):
        print("Drawing menu.")
        self.app.screen.blit(self.background, (0, 0))
        for button in self.buttons:
            text = self.font.render(button['text'], True, (255, 255, 255))
            text_rect = text.get_rect(center=button['rect'].center)
            self.app.screen.blit(text, text_rect)
