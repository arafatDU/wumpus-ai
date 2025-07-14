import sys
from map import *


class Graphic:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.caption = pygame.display.set_caption(CAPTION)
        self.clock = pygame.time.Clock()
        self.map = None
        self.agent = None
        self.gold = None
        self.wumpus = None
        self.pit = None
        self.arrow = None
        self.font = pygame.font.Font(FONT_GRINCHED, 30)
        self.noti = pygame.font.Font(FONT_GRINCHED, 15)
        self.victory = pygame.font.Font(FONT_GRINCHED, 50)
        self.all_sprites = pygame.sprite.Group()

        self.state = MAP
        self.map_i = 1
        self.mouse = None
        self.bg = pygame.image.load('./Assets/Images/win.png').convert()
        self.bg = pygame.transform.scale(self.bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.direct = 3

    def running_draw(self):
        self.screen.fill(WHITE)
        self.map.draw(self.screen)
        score = self.agent.get_score()
        text = self.font.render('Points : ' + str(score), True, BLACK)
        textRect = text.get_rect()
        textRect.center = (920, 25)
        self.screen.blit(text, textRect)

    def draw_button(self, surf, rect, button_color, text_color, text):
        pygame.draw.rect(surf, button_color, rect)
        text_surf = self.font.render(text, True, text_color)
        text_rect = text_surf.get_rect()
        text_rect.center = rect.center
        self.screen.blit(text_surf, text_rect)

    def home_draw(self):
        self.screen.fill(WHITE)

    def home_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if 235 <= self.mouse[0] <= 735 and 120 <= self.mouse[1] <= 170:
                    self.state = RUNNING
                    self.map_i = 1
                # elif 235 <= self.mouse[0] <= 735 and 200 <= self.mouse[1] <= 250:
                #     self.state = RUNNING
                #     self.map_i = 2
                # elif 235 <= self.mouse[0] <= 735 and 280 <= self.mouse[1] <= 330:
                #     self.state = RUNNING
                #     self.map_i = 3
                # elif 235 <= self.mouse[0] <= 735 and 360 <= self.mouse[1] <= 410:
                #     self.state = RUNNING
                #     self.map_i = 4
                # elif 235 <= self.mouse[0] <= 735 and 440 <= self.mouse[1] <= 490:
                #     self.state = RUNNING
                #     self.map_i = 5
                elif 235 <= self.mouse[0] <= 735 and 520 <= self.mouse[1] <= 570:
                    pygame.quit()
                    sys.exit()

            self.mouse = pygame.mouse.get_pos()
            if 235 <= self.mouse[0] <= 735 and 120 <= self.mouse[1] <= 170:
                self.draw_button(self.screen, LEVEL_1_POS, DARK_GREY, GREEN, "Start")
            else:
                self.draw_button(self.screen, LEVEL_1_POS, LIGHT_GREY, BLACK, "Start")
            # if 235 <= self.mouse[0] <= 735 and 200 <= self.mouse[1] <= 250:
            #     self.draw_button(self.screen, LEVEL_2_POS, DARK_GREY, RED, "MAP 2")
            # else:
            #     self.draw_button(self.screen, LEVEL_2_POS, LIGHT_GREY, BLACK, "MAP 2")
            # if 235 <= self.mouse[0] <= 735 and 280 <= self.mouse[1] <= 330:
            #     self.draw_button(self.screen, LEVEL_3_POS, DARK_GREY, RED, "MAP 3")
            # else:
            #     self.draw_button(self.screen, LEVEL_3_POS, LIGHT_GREY, BLACK, "MAP 3")
            # if 235 <= self.mouse[0] <= 735 and 360 <= self.mouse[1] <= 410:
            #     self.draw_button(self.screen, LEVEL_4_POS, DARK_GREY, RED, "MAP 4")
            # else:
            #     self.draw_button(self.screen, LEVEL_4_POS, LIGHT_GREY, BLACK, "MAP 4")
            # if 235 <= self.mouse[0] <= 735 and 440 <= self.mouse[1] <= 490:
            #     self.draw_button(self.screen, LEVEL_5_POS, DARK_GREY, RED, "MAP 5")
            # else:
            #     self.draw_button(self.screen, LEVEL_5_POS, LIGHT_GREY, BLACK, "MAP 5")
            # if 235 <= self.mouse[0] <= 735 and 520 <= self.mouse[1] <= 570:
            #     self.draw_button(self.screen, EXIT_POS, DARK_GREY, RED, "EXIT")
            # else:
            #     self.draw_button(self.screen, EXIT_POS, LIGHT_GREY, BLACK, "EXIT")
            pygame.display.update()

    def win_draw(self):
        self.screen.fill(WHITE)
        self.screen.blit(self.bg, (0, 0))

        if self.state == WIN:
            text = self.victory.render('VICTORY!!!', True, BLACK)
        elif self.state == TRYBEST:
            text = self.victory.render('TRY BEST!!!', True, BLACK)

        textRect = text.get_rect()
        textRect.center = (600, 50)
        self.screen.blit(text, textRect)
        score = self.agent.get_score()
        text = self.victory.render('Scored: ' + str(score), True, BLACK)
        textRect.center = (500, 100)
        self.screen.blit(text, textRect)

    def win_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()
        pygame.time.delay(200)
        self.state = MAP