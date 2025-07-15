import sys
from map import *
from agent import *
from objects import *
import algorithms
import pygame.gfxdraw
import math
import random

def draw_vertical_gradient(surface, color_top, color_bottom):
    """Draw a vertical gradient from color_top to color_bottom on the given surface."""
    height = surface.get_height()
    for y in range(height):
        ratio = y / height
        r = int(color_top[0] * (1 - ratio) + color_bottom[0] * ratio)
        g = int(color_top[1] * (1 - ratio) + color_bottom[1] * ratio)
        b = int(color_top[2] * (1 - ratio) + color_bottom[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (surface.get_width(), y))

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
        self.title_font = pygame.font.Font(FONT_GRINCHED, 60)
        self.status_font = pygame.font.Font(FONT_GRINCHED, 24)
        self.all_sprites = pygame.sprite.Group()

        self.state = MAP
        self.map_i = 1
        self.mouse = None
        self.bg = pygame.image.load('./assets/images/win.png').convert()
        self.bg = pygame.transform.scale(self.bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.direct = 3
        self.anim_time = 0
        # Load Wumpus image for animation
        self.wumpus_img = pygame.image.load('./assets/images/wumpus1.png').convert_alpha()
        self.wumpus_img = pygame.transform.smoothscale(self.wumpus_img, (120, 120))

    def running_draw(self):
        # Gradient background for gameplay
        gradient = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        draw_vertical_gradient(gradient, (230, 240, 255), (180, 200, 220))
        self.screen.blit(gradient, (0, 0))
        self.map.draw(self.screen)
        score = self.agent.get_score()
        # Modern status bar
        pygame.draw.rect(self.screen, (30, 30, 60), (0, 0, SCREEN_WIDTH, 50), border_radius=0)
        text = self.status_font.render(f'Points: {score}', True, (255, 255, 255))
        self.screen.blit(text, (30, 10))
        # Add more status info if needed

    def draw_button(self, surf, rect, button_color, text_color, text, shadow=True, hover=False):
        # Draw shadow
        if shadow:
            shadow_rect = rect.move(4, 4)
            pygame.draw.rect(surf, (60, 60, 60, 80), shadow_rect, border_radius=15)
        # Draw button
        color = button_color
        if hover:
            color = tuple(min(255, c + 30) for c in button_color)
        pygame.draw.rect(surf, color, rect, border_radius=15)
        # Draw border
        pygame.draw.rect(surf, (0, 0, 0), rect, 2, border_radius=15)
        # Draw text
        text_surf = self.font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=rect.center)
        surf.blit(text_surf, text_rect)

    def home_draw(self):
        # Gradient background
        gradient = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        draw_vertical_gradient(gradient, (60, 120, 200), (200, 220, 255))
        self.screen.blit(gradient, (0, 0))
        # Title
        title_surf = self.title_font.render("Wumpus World AI", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_surf, title_rect)
        # Animated Wumpus (bobbing)
        wumpus_x = SCREEN_WIDTH // 2
        wumpus_y = 220 + int(20 * math.sin(self.anim_time * 0.07))
        wumpus_rect = self.wumpus_img.get_rect(center=(wumpus_x, wumpus_y))
        self.screen.blit(self.wumpus_img, wumpus_rect)
        # Centered Start button
        button_width, button_height = 350, 60
        button_x = (SCREEN_WIDTH - button_width) // 2
        button_y = wumpus_rect.bottom + 40
        start_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        self.mouse = pygame.mouse.get_pos()
        hover = start_rect.collidepoint(self.mouse)
        self.draw_button(self.screen, start_rect, (70, 170, 90), (255, 255, 255), "Start", shadow=True, hover=hover)
        self.start_button_rect = start_rect  # Save for event handling
        pygame.display.update()

    def home_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if hasattr(self, 'start_button_rect') and self.start_button_rect.collidepoint(event.pos):
                    self.state = RUNNING
                    self.map_i = 1

    def win_draw(self):
        # Gradient background
        gradient = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        draw_vertical_gradient(gradient, (255, 220, 120), (255, 255, 255))
        self.screen.blit(gradient, (0, 0))
        self.screen.blit(self.bg, (0, 0))
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))
        # Win message
        if self.state == WIN:
            text = self.victory.render('VICTORY!!!', True, (255, 255, 0))
        elif self.state == TRYBEST:
            text = self.victory.render('TRY BEST!!!', True, (255, 255, 0))
        textRect = text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(text, textRect)
        score = self.agent.get_score()
        score_text = self.victory.render('Scored: ' + str(score), True, (255, 255, 255))
        scoreRect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(score_text, scoreRect)

    def win_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()
        pygame.time.delay(200)
        self.state = MAP

    def run(self):
        while True:
            self.anim_time += 1  # For animation
            if self.state == MAP:
                self.home_draw()
                self.home_event()

            elif self.state == RUNNING:
                self.state = TRYBEST

                action_list, cave_cell, cell_matrix = algorithms.AgentBrain(MAP_LIST[self.map_i - 1], OUTPUT_LIST[self.map_i - 1]).solve_wumpus_world()
                map_pos = cave_cell.map_pos

                self.map = Map((len(cell_matrix) - map_pos[1] + 1, map_pos[0]))
                self.arrow = Arrow()
                self.gold = Gold()
                self.agent = Agent(len(cell_matrix) - map_pos[1] + 1, map_pos[0])
                self.agent.load_image()
                self.all_sprites = pygame.sprite.Group()
                self.all_sprites.add(self.agent)

                x = []
                y = []
                for ir in range(len(cell_matrix)):
                    for ic in range(len(cell_matrix)):
                        if cell_matrix[ir][ic].exist_pit():
                            x.append(ir)
                            y.append(ic)
                self.pit = Pit(x, y)
                self.pit.pit_notification()

                x = []
                y = []
                for ir in range(len(cell_matrix)):
                    for ic in range(len(cell_matrix)):
                        if cell_matrix[ir][ic].exist_wumpus():
                            x.append(ir)
                            y.append(ic)
                self.wumpus = Wumpus(x, y)
                self.wumpus.wumpus_notification()

                self.running_draw()

                for action in action_list:
                    pygame.time.delay(SPEED)
                    self.display_action(action)
                    # print(action)

                    if action == algorithms.Action.KILL_ALL_WUMPUS_AND_GRAB_ALL_FOOD:
                        self.state = WIN

                    if action == algorithms.Action.FALL_INTO_PIT or action == algorithms.Action.BE_EATEN_BY_WUMPUS:
                        self.state = GAMEOVER
                        break

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()

            elif self.state == WIN or self.state == TRYBEST:
                self.win_draw()
                self.win_event()

            self.clock.tick(60)


    def display_action(self, action: algorithms.Action):
        if action == algorithms.Action.TURN_LEFT:
            self.direct = self.agent.turn_left()
            self.all_sprites.update()
            self.running_draw()
            self.all_sprites.draw(self.screen)
            temp = self.map.discovered()
            self.wumpus.update(self.screen, self.noti, temp)
            self.pit.update(self.screen, self.noti, temp)
            pygame.display.update()
        elif action == algorithms.Action.TURN_RIGHT:
            self.direct = self.agent.turn_right()
            self.all_sprites.update()
            self.running_draw()
            self.all_sprites.draw(self.screen)
            temp = self.map.discovered()
            self.wumpus.update(self.screen, self.noti, temp)
            self.pit.update(self.screen, self.noti, temp)
            pygame.display.update()
        elif action == algorithms.Action.TURN_UP:
            self.direct = self.agent.turn_up()
            self.all_sprites.update()
            self.running_draw()
            self.all_sprites.draw(self.screen)
            temp = self.map.discovered()
            self.wumpus.update(self.screen, self.noti, temp)
            self.pit.update(self.screen, self.noti, temp)
            pygame.display.update()
        elif action == algorithms.Action.TURN_DOWN:
            self.direct = self.agent.turn_down()
            self.all_sprites.update()
            self.running_draw()
            self.all_sprites.draw(self.screen)
            temp = self.map.discovered()
            self.wumpus.update(self.screen, self.noti, temp)
            self.pit.update(self.screen, self.noti, temp)
            pygame.display.update()
        elif action == algorithms.Action.MOVE_FORWARD:
            self.agent.move_forward(self.direct)
            i, j = self.agent.get_pos()
            self.map.discover_cell_i_j(i, j)
            self.all_sprites.update()
            self.running_draw()
            self.all_sprites.draw(self.screen)
            temp = self.map.discovered()
            self.wumpus.update(self.screen, self.noti, temp)
            self.pit.update(self.screen, self.noti, temp)
            pygame.display.update()
        elif action == algorithms.Action.GRAB_GOLD:
            self.agent.grab_gold()
            self.all_sprites.update()
            self.running_draw()
            self.all_sprites.draw(self.screen)
            self.gold.grab_gold(self.screen, self.font)
            temp = self.map.discovered()
            self.wumpus.update(self.screen, self.noti, temp)
            self.pit.update(self.screen, self.noti, temp)
            pygame.display.update()
            pygame.time.delay(500)
        elif action == algorithms.Action.PERCEIVE_BREEZE:
            pass
        elif action == algorithms.Action.PERCEIVE_STENCH:
            pass
        elif action == algorithms.Action.SHOOT:
            self.agent.shoot()
            self.all_sprites.update()
            self.running_draw()
            self.all_sprites.draw(self.screen)
            i, j = self.agent.get_pos()
            self.arrow.shoot(self.direct, self.screen, i, j)
            temp = self.map.discovered()
            self.wumpus.update(self.screen, self.noti, temp)
            self.pit.update(self.screen, self.noti, temp)
            pygame.display.update()
            pygame.time.delay(500)
        elif action == algorithms.Action.KILL_WUMPUS:

            i, j = self.agent.get_pos()
            if self.direct == 0:
                i -= 1
            elif self.direct == 1:
                i += 1
            elif self.direct == 2:
                j -= 1
            elif self.direct == 3:
                j += 1
            self.wumpus.wumpus_killed(i, j)
            self.wumpus.wumpus_notification()
            i, j = self.agent.get_pos()
            if not self.wumpus.stench_i_j(i, j):
                self.wumpus.wumpus_kill(self.screen, self.font)
            temp = self.map.discovered()
            self.wumpus.update(self.screen, self.noti, temp)
            self.pit.update(self.screen, self.noti, temp)
            pygame.display.update()
            pygame.time.delay(500)
            pass
        elif action == algorithms.Action.KILL_NO_WUMPUS:
            pass
        elif action == algorithms.Action.BE_EATEN_BY_WUMPUS:
            self.agent.wumpus_or_pit_collision()
            self.all_sprites.update()
            self.running_draw()
            self.all_sprites.draw(self.screen)
            pygame.display.update()
            self.state = GAMEOVER
        elif action == algorithms.Action.FALL_INTO_PIT:
            self.agent.wumpus_or_pit_collision()
            self.all_sprites.update()
            self.running_draw()
            self.all_sprites.draw(self.screen)
            pygame.display.update()
            self.state = GAMEOVER
        elif action == algorithms.Action.KILL_ALL_WUMPUS_AND_GRAB_ALL_FOOD:
            #
            self.state = WIN
            pass
        elif action == algorithms.Action.CLIMB_OUT_OF_THE_CAVE:
            self.agent.climb()
            self.all_sprites.update()
            self.running_draw()
            self.all_sprites.draw(self.screen)
            self.map.agent_climb(self.screen, self.font)
            pygame.display.update()
            pygame.time.delay(2000)
        elif action == algorithms.Action.DECTECT_PIT:
            i, j = self.agent.get_pos()
            if self.direct == 0:
                i -= 1
            elif self.direct == 1:
                i += 1
            elif self.direct == 2:
                j -= 1
            elif self.direct == 3:
                j += 1
            self.map.pit_detect(i, j)
            self.all_sprites.update()
            self.running_draw()
            self.all_sprites.draw(self.screen)
            pygame.time.delay(1000)
        elif action == algorithms.Action.DETECT_WUMPUS:
            pass
        elif action == algorithms.Action.DETECT_NO_PIT:
            pass
        elif action == algorithms.Action.DETECT_NO_WUMPUS:
            pass
        elif action == algorithms.Action.INFER_PIT:
            pass
        elif action == algorithms.Action.INFER_NOT_PIT:
            pass
        elif action == algorithms.Action.INFER_WUMPUS:
            pass
        elif action == algorithms.Action.INFER_NOT_WUMPUS:
            pass
        elif action == algorithms.Action.DETECT_SAFE:
            pass
        elif action == algorithms.Action.INFER_SAFE:
            pass
        else:
            raise TypeError("Error: " + self.display_action.__name__)
