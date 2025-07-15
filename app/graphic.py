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
        # Use a cooler font with fallback
        try:
            self.title_font = pygame.font.Font('./assets/fonts/GroovyLiquor.ttf', 85)
        except:
            self.title_font = pygame.font.Font(None, 80)  # System default as fallback
        self.subtitle_font = pygame.font.Font(FONT_GRINCHED, 24)
        self.status_font = pygame.font.Font(FONT_GRINCHED, 24)
        self.all_sprites = pygame.sprite.Group()

        self.state = MAP
        self.map_i = 1
        self.mouse = None
        self.bg = pygame.image.load('./assets/images/win.png').convert()
        self.bg = pygame.transform.scale(self.bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.direct = 3
        self.anim_time = 0
        self.pulse_time = 0
        # Load Wumpus image for animation with better scaling
        self.wumpus_img = pygame.image.load('./assets/images/wumpus1.png').convert_alpha()
        self.wumpus_img = pygame.transform.smoothscale(self.wumpus_img, (140, 140))
        
        # Create particles for background effect
        self.particles = []
        for _ in range(30):
            self.particles.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'speed': random.uniform(0.5, 2.0),
                'size': random.randint(1, 3)
            })

    def draw_modern_ui_panel(self, x, y, width, height, color, border_color=None, alpha=200, glow=False):
        """Draw a modern UI panel with rounded corners, transparency, and optional glow"""
        # Glow effect
        if glow:
            glow_surface = pygame.Surface((width + 20, height + 20), pygame.SRCALPHA)
            for i in range(10):
                glow_alpha = max(0, alpha // 4 - i * 5)
                pygame.draw.rect(glow_surface, (*border_color, glow_alpha), 
                               (10-i, 10-i, width + i*2, height + i*2), border_radius=20)
            self.screen.blit(glow_surface, (x-10, y-10))
        
        # Main panel
        panel = pygame.Surface((width, height), pygame.SRCALPHA)
        panel.fill((*color, alpha))
        pygame.draw.rect(panel, (*color, alpha), (0, 0, width, height), border_radius=15)
        if border_color:
            pygame.draw.rect(panel, border_color, (0, 0, width, height), 3, border_radius=15)
        self.screen.blit(panel, (x, y))

    def draw_game_grid_background(self):
        """Draw a futuristic grid background with enhanced visuals"""
        # Main grid
        grid_color = (40, 60, 80, 120)
        game_area_width = 800
        game_area_height = 800
        
        for x in range(100, game_area_width, 70):
            pygame.draw.line(self.screen, grid_color, (x, 100), (x, game_area_height), 1)
        for y in range(100, game_area_height, 70):
            pygame.draw.line(self.screen, grid_color, (100, y), (game_area_width, y), 1)
        
        # Highlight grid borders
        pygame.draw.rect(self.screen, (60, 100, 140), (100, 100, game_area_width-100, game_area_height-100), 2)

    def draw_health_bar(self, x, y, current, maximum, width=200, height=20):
        """Draw a gaming-style health/progress bar"""
        # Background
        pygame.draw.rect(self.screen, (40, 40, 40), (x, y, width, height), border_radius=10)
        # Fill
        fill_width = int((current / maximum) * width) if maximum > 0 else 0
        color = (100, 255, 100) if current > maximum * 0.5 else (255, 200, 100) if current > maximum * 0.25 else (255, 100, 100)
        if fill_width > 0:
            pygame.draw.rect(self.screen, color, (x, y, fill_width, height), border_radius=10)
        # Border
        pygame.draw.rect(self.screen, (200, 200, 200), (x, y, width, height), 2, border_radius=10)

    def draw_minimap(self, x, y, size=200):
        """Draw a minimap showing explored areas"""
        # Minimap background
        self.draw_modern_ui_panel(x, y, size, size, (10, 20, 30), (60, 100, 140), glow=True)
        
        # Minimap title
        try:
            mini_font = pygame.font.Font('./assets/fonts/GroovyLiquor.ttf', 18)
        except:
            mini_font = pygame.font.Font(None, 18)
        
        title = mini_font.render("RADAR", True, (100, 200, 255))
        self.screen.blit(title, (x + 10, y + 10))
        
        # Draw minimap grid (simplified)
        cell_size = (size - 40) // 10
        start_x, start_y = x + 20, y + 40
        
        if hasattr(self, 'map') and self.map:
            discovered = self.map.discovered()
            agent_pos = self.agent.get_pos()
            
            for i in range(10):
                for j in range(10):
                    cell_x = start_x + j * cell_size
                    cell_y = start_y + i * cell_size
                    
                    if discovered[i][j]:
                        # Discovered area
                        pygame.draw.rect(self.screen, (100, 150, 100), 
                                       (cell_x, cell_y, cell_size-1, cell_size-1))
                    else:
                        # Unknown area
                        pygame.draw.rect(self.screen, (50, 50, 50), 
                                       (cell_x, cell_y, cell_size-1, cell_size-1))
                    
                    # Agent position
                    if agent_pos[0] == i and agent_pos[1] == j:
                        pygame.draw.circle(self.screen, (255, 255, 100), 
                                         (cell_x + cell_size//2, cell_y + cell_size//2), 3)

    def running_draw(self):
        # Enhanced dark futuristic background with depth
        gradient = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        draw_vertical_gradient(gradient, (10, 15, 25), (20, 30, 45))
        self.screen.blit(gradient, (0, 0))
        
        # Add dynamic animated particles for atmosphere
        for i in range(40):
            x = (self.anim_time * 0.3 + i * 40) % SCREEN_WIDTH
            y = (self.anim_time * 0.2 + i * 30) % SCREEN_HEIGHT
            alpha = int(30 + 20 * math.sin(self.anim_time * 0.01 + i))
            size = 1 + int(2 * math.sin(self.anim_time * 0.015 + i))
            pygame.gfxdraw.filled_circle(self.screen, int(x), int(y), size, (80, 120, 180, alpha))

        # Enhanced game area with better positioning
        game_area_x, game_area_y = 50, 100
        game_area_size = 800
        
        # Game area background with glow
        self.draw_modern_ui_panel(game_area_x-10, game_area_y-10, game_area_size+20, game_area_size+20, 
                                 (5, 10, 20), (40, 80, 120), glow=True)
        
        # Draw enhanced grid
        self.draw_game_grid_background()
        
        # Draw the game map
        self.map.draw(self.screen)
        
        # Get current game stats
        score = self.agent.get_score()
        agent_pos = self.agent.get_pos()
        
        # === TOP HUD BAR ===
        self.draw_modern_ui_panel(0, 0, SCREEN_WIDTH, 90, (15, 25, 40), (60, 100, 140), glow=True)
        
        # Enhanced score display
        score_color = (100, 255, 100) if score >= 0 else (255, 100, 100)
        try:
            score_font = pygame.font.Font('./assets/fonts/GroovyLiquor.ttf', 36)
            hud_font = pygame.font.Font('./assets/fonts/GroovyLiquor.ttf', 24)
        except:
            score_font = pygame.font.Font(None, 36)
            hud_font = pygame.font.Font(None, 24)
        
        # Score with background panel
        score_panel_width = 250
        self.draw_modern_ui_panel(20, 15, score_panel_width, 60, (25, 35, 55), (80, 120, 160))
        score_text = score_font.render(f"💎 {score}", True, score_color)
        self.screen.blit(score_text, (40, 30))
        score_label = self.noti.render("SCORE", True, (150, 170, 200))
        self.screen.blit(score_label, (40, 15))
        
        # Agent position with panel
        pos_panel_width = 200
        self.draw_modern_ui_panel(300, 15, pos_panel_width, 60, (25, 35, 55), (80, 120, 160))
        pos_text = hud_font.render(f"({agent_pos[0]}, {agent_pos[1]})", True, (200, 220, 255))
        self.screen.blit(pos_text, (320, 35))
        pos_label = self.noti.render("POSITION", True, (150, 170, 200))
        self.screen.blit(pos_label, (320, 20))
        
        # AI Status with animated indicator
        ai_panel_width = 180
        self.draw_modern_ui_panel(530, 15, ai_panel_width, 60, (25, 35, 55), (100, 255, 150))
        ai_pulse = int(50 + 50 * math.sin(self.anim_time * 0.1))
        ai_color = (100, 255, 150, ai_pulse)
        ai_text = hud_font.render("AI ACTIVE", True, (100, 255, 150))
        self.screen.blit(ai_text, (550, 35))
        ai_label = self.noti.render("STATUS", True, (150, 170, 200))
        self.screen.blit(ai_label, (550, 20))
        
        # === RIGHT SIDE PANELS ===
        panel_x = 900
        panel_width = SCREEN_WIDTH - panel_x - 30
        
        # Mission Control Panel
        self.draw_modern_ui_panel(panel_x, 100, panel_width, 350, (15, 25, 40), (60, 100, 140), glow=True)
        
        try:
            panel_font = pygame.font.Font('./assets/fonts/GroovyLiquor.ttf', 32)
            section_font = pygame.font.Font('./assets/fonts/GroovyLiquor.ttf', 20)
        except:
            panel_font = pygame.font.Font(None, 32)
            section_font = pygame.font.Font(None, 20)
        
        # Panel header with glow
        title_text = panel_font.render("MISSION CONTROL", True, (150, 200, 255))
        self.screen.blit(title_text, (panel_x + 20, 120))
        
        # Mission objectives with better spacing
        objectives = [
            "🎯 Collect all gold treasures",
            "⚔️  Eliminate or avoid Wumpus", 
            "🕳️  Navigate around deadly pits",
            "🧠 Apply logical reasoning",
            "🏠 Return to starting position"
        ]
        
        obj_y_start = 170
        for i, objective in enumerate(objectives):
            # Objective background
            obj_bg_width = panel_width - 40
            self.draw_modern_ui_panel(panel_x + 20, obj_y_start + i * 35 - 5, obj_bg_width, 30, (20, 30, 50), None, alpha=100)
            obj_text = section_font.render(objective, True, (180, 200, 220))
            self.screen.blit(obj_text, (panel_x + 30, obj_y_start + i * 35))
        
        # Minimap/Radar
        self.draw_minimap(panel_x, 480, 250)
        
        # Stats Panel
        stats_y = 750
        self.draw_modern_ui_panel(panel_x, stats_y, panel_width, 120, (15, 25, 40), (60, 100, 140), glow=True)
        
        stats_title = section_font.render("STATISTICS", True, (150, 200, 255))
        self.screen.blit(stats_title, (panel_x + 20, stats_y + 15))
        
        # Calculate some stats
        total_cells = 100
        discovered_cells = sum(sum(row) for row in self.map.discovered()) if hasattr(self.map, 'discovered') else 0
        exploration_percent = int((discovered_cells / total_cells) * 100)
        
        # Progress bar for exploration
        self.draw_health_bar(panel_x + 20, stats_y + 50, discovered_cells, total_cells, panel_width - 40, 15)
        progress_text = self.noti.render(f"Cave Explored: {exploration_percent}%", True, (180, 200, 220))
        self.screen.blit(progress_text, (panel_x + 25, stats_y + 75))
        
        # === BOTTOM STATUS BAR ===
        bottom_height = 80
        self.draw_modern_ui_panel(0, SCREEN_HEIGHT - bottom_height, SCREEN_WIDTH, bottom_height, 
                                 (15, 25, 40), (60, 100, 140), glow=True)
        
        # Action status with animated elements
        action_bg_width = 300
        self.draw_modern_ui_panel(30, SCREEN_HEIGHT - bottom_height + 15, action_bg_width, 50, (25, 35, 55), (100, 255, 150))
        action_text = hud_font.render("🤖 AI AGENT EXPLORING", True, (100, 255, 150))
        self.screen.blit(action_text, (50, SCREEN_HEIGHT - bottom_height + 30))
        
        # Thinking indicator with animated dots
        thinking_x = 400
        progress_dots = "●" * ((int(self.anim_time / 15) % 4) + 1)
        progress_text = hud_font.render(f"PROCESSING{progress_dots}", True, (255, 200, 100))
        self.screen.blit(progress_text, (thinking_x, SCREEN_HEIGHT - bottom_height + 30))
        
        # Neural network visualization (animated)
        nn_x = 700
        for i in range(5):
            for j in range(3):
                x = nn_x + i * 15
                y = SCREEN_HEIGHT - 50 + j * 10
                alpha = int(100 + 100 * math.sin(self.anim_time * 0.05 + i + j))
                pygame.gfxdraw.filled_circle(self.screen, x, y, 2, (100, 200, 255, alpha))
                if i < 4:
                    pygame.draw.line(self.screen, (100, 200, 255, 50), (x, y), (x + 15, y), 1)
        
        # Version info with style
        version_bg_width = 200
        self.draw_modern_ui_panel(SCREEN_WIDTH - version_bg_width - 20, SCREEN_HEIGHT - bottom_height + 15, 
                                 version_bg_width, 50, (25, 35, 55), (60, 100, 140))
        version_text = self.noti.render("WUMPUS WORLD AI", True, (150, 170, 200))
        self.screen.blit(version_text, (SCREEN_WIDTH - version_bg_width, SCREEN_HEIGHT - bottom_height + 20))
        version_num = self.noti.render("v2.0 NEURAL EDITION", True, (100, 120, 150))
        self.screen.blit(version_num, (SCREEN_WIDTH - version_bg_width, SCREEN_HEIGHT - bottom_height + 40))

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

    def draw_particles(self):
        """Draw animated background particles"""
        for particle in self.particles:
            # Update particle position
            particle['y'] += particle['speed']
            if particle['y'] > SCREEN_HEIGHT:
                particle['y'] = -10
                particle['x'] = random.randint(0, SCREEN_WIDTH)
            
            # Draw particle with slight transparency
            alpha = int(100 + 50 * math.sin(self.anim_time * 0.05 + particle['x'] * 0.01))
            color = (255, 255, 255, alpha)
            pygame.gfxdraw.filled_circle(self.screen, int(particle['x']), int(particle['y']), particle['size'], (255, 255, 255))

    def home_draw(self):
        # Enhanced gradient background with more depth
        gradient = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        draw_vertical_gradient(gradient, (45, 100, 180), (120, 180, 240))
        self.screen.blit(gradient, (0, 0))
        
        # Draw animated particles
        self.draw_particles()
        
        # Title with glow effect
        title_text = "Wumpus World AI"
        # Create glow effect by drawing multiple times with different colors
        for offset in range(5, 0, -1):
            glow_color = (100 + offset * 20, 150 + offset * 20, 255)
            glow_surf = self.title_font.render(title_text, True, glow_color)
            glow_rect = glow_surf.get_rect(center=(SCREEN_WIDTH // 2 + offset//2, 100 + offset//2))
            self.screen.blit(glow_surf, glow_rect)
        
        # Main title
        title_surf = self.title_font.render(title_text, True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_surf, title_rect)
        
        # Subtitle
        subtitle_text = "Intelligent Agent Navigation"
        subtitle_surf = self.subtitle_font.render(subtitle_text, True, (200, 220, 255))
        subtitle_rect = subtitle_surf.get_rect(center=(SCREEN_WIDTH // 2, 140))
        self.screen.blit(subtitle_surf, subtitle_rect)
        
        # Enhanced Wumpus animation with rotation and scaling
        wumpus_x = SCREEN_WIDTH // 2
        base_y = 240
        bob_offset = int(25 * math.sin(self.anim_time * 0.08))
        wumpus_y = base_y + bob_offset
        
        # Add slight rotation
        rotation_angle = 5 * math.sin(self.anim_time * 0.05)
        
        # Add pulsing scale effect
        scale_factor = 1.0 + 0.1 * math.sin(self.anim_time * 0.1)
        scaled_size = int(140 * scale_factor)
        
        # Apply transformations
        rotated_wumpus = pygame.transform.rotate(self.wumpus_img, rotation_angle)
        scaled_wumpus = pygame.transform.smoothscale(rotated_wumpus, (scaled_size, scaled_size))
        
        # Draw the wumpus (removed shadow effect)
        wumpus_rect = scaled_wumpus.get_rect(center=(wumpus_x, wumpus_y))
        self.screen.blit(scaled_wumpus, wumpus_rect)
        
        # Enhanced Start button with better styling
        button_width, button_height = 380, 70
        button_x = (SCREEN_WIDTH - button_width) // 2
        button_y = wumpus_rect.bottom + 60
        start_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        self.mouse = pygame.mouse.get_pos()
        hover = start_rect.collidepoint(self.mouse)
        
        # Button glow effect when hovering
        if hover:
            glow_rect = start_rect.inflate(10, 10)
            pygame.draw.rect(self.screen, (100, 200, 120, 100), glow_rect, border_radius=20)
        
        self.draw_button(self.screen, start_rect, (60, 150, 80), (255, 255, 255), "🚀 Start Adventure", shadow=True, hover=hover)
        self.start_button_rect = start_rect
        
        # Add instruction text
        instruction_text = "Navigate the dangerous cave using AI logic!"
        instruction_surf = self.subtitle_font.render(instruction_text, True, (180, 200, 240))
        instruction_rect = instruction_surf.get_rect(center=(SCREEN_WIDTH // 2, start_rect.bottom + 40))
        self.screen.blit(instruction_surf, instruction_rect)
        
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
