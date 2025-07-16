import pygame

# Speed
SPEED = 50          # Change the speed of the game here.

# Window
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 710
CAPTION = 'Wumpus World'

# Cell
IMG_INITIAL_CELL = './assets/images/initial_cell.png'
IMG_DISCOVERED_CELL = './assets/images/discovered_cell.png'

# Object
IMG_PIT = './assets/images/pit.png'
IMG_WUMPUS = './assets/images/wumpus1.png'
IMG_GOLD = './assets/images/gold.png'

# Hunter
IMG_HUNTER_RIGHT = './assets/images/hunter_right.png'
IMG_HUNTER_LEFT = './assets/images/hunter_left.png'
IMG_HUNTER_UP = './assets/images/hunter_up.png'
IMG_HUNTER_DOWN = './assets/images/hunter_down.png'

IMG_ARROW_RIGHT = './assets/images/arrow_right.png'
IMG_ARROW_LEFT = './assets/images/arrow_left.png'
IMG_ARROW_UP = './assets/images/arrow_up.png'
IMG_ARROW_DOWN = './assets/images/arrow_down.png'

# Map
MAP_LIST = ['./assets/input/map_1.txt']
MAP_NUM = len(MAP_LIST)

# Output
OUTPUT_LIST = ['./assets/output/result_1.txt']

# Fonts
FONT_GRINCHED = './assets/fonts/Grinched.ttf'

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GREY = (170, 170, 170)
DARK_GREY = (75, 75, 75)
RED = (255, 0, 0)
GREEN = (60,179,113)

# state
RUNNING = 'running'
GAMEOVER = 'gameover'
WIN = 'win'
TRYBEST = 'trybest'
MAP = 'map'

LEVEL_1_POS = pygame.Rect(235, 120, 500, 50)
LEVEL_2_POS = pygame.Rect(235, 200, 500, 50)
LEVEL_3_POS = pygame.Rect(235, 280, 500, 50)
LEVEL_4_POS = pygame.Rect(235, 360, 500, 50)
LEVEL_5_POS = pygame.Rect(235, 440, 500, 50)
EXIT_POS = pygame.Rect(235, 520, 500, 50)
