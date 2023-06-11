DEBUG = False
DEBUG_START_X = 110
DEBUG_START_Y = 538

SCREEN_HEIGHT = 700
SCREEN_WIDTH = 1000
SCREEN_SIZE = (SCREEN_WIDTH,SCREEN_HEIGHT)

## COLORS ##
#                R    G    B
GRAY         = (100, 100, 100)
WHITE        = (255, 255, 255)
RED          = (255,   0,   0)
GREEN        = (  0, 255,   0)
YELLOW       = (255, 255,   0)
ORANGE       = (255, 128,   0)
BLACK        = (  0,   0,   0)
NEAR_BLACK   = ( 19,  15,  48)

#배율
SIZE_MULTIPLIER = 2.5
TILE_SIZE_MULTIPLIER = 2.69
BACKGROUND_MULTIPLER = 2.679
GROUND_HEIGHT = SCREEN_HEIGHT - 62

GAME_TIME_OUT = 201

#STATES FOR ENTIRE GAME
MAIN_MENU = 'main menu'
LOAD_SCREEN = 'load screen'
TIME_OUT = 'time out'
GAME_OVER = 'game over'
LEVEL = 'level'

#MAIN MENU CURSOR STATES
PLAYER1 = '1 PLAYER GAME'
PLAYER2 = '2 PLAYER GAME'

#GAME INFO DICTIONARY KEYS
TOTAL_COIN = 'coin total'
SCORE = 'score'
TOP_SCORE = 'top score'
ATTENDENCE = 'attendence'
CURRENT_TIME = 'current time'
LEVEL_NUM = 'level num'
PLAYER_NAME = 'player name'
PLAYER_1 = 'player1'
PLAYER_2 = 'player2'

#MAP COMPONENTS
MAP_IMAGE = 'image_name'
MAP_MAPS = 'maps'
SUB_MAP = 'sub_map'
MAP_GROUND = 'ground'
MAP_ELEVATOR = 'elevator'
ELEVATOR_TYPE_NONE = 0
ELEVATOR_TYPE_IN = 1                # 수직형
ELEVATOR_TYPE_HORIZONTAL = 2        # 수평형
MAP_STEP = 'step'
MAP_TILE = 'tile'
TILE_NUM = 'tile_num'
TYPE_NONE = 0
TYPE_COIN = 1
TYPE_STAR = 2
MAP_QR_BRICK = 'QR_brick'
TYPE_COFFEE = 3
TYPE_HOT6 = 4
TYPE_FIREBALL = 5
TYPE_LIFECOFFEE = 6
MAP_ENEMY = 'enemy'
ENEMY_TYPE_BOO = 0
ENEMY_TYPE_PROF = 1
ENEMY_TYPE_FLY_PROF = 2
ENEMY_TYPE_PIRANHA = 3
ENEMY_TYPE_FIRESTICK = 4
ENEMY_TYPE_FIRE_PROF = 5
ENEMY_RANGE = 'range'
MAP_CHECKPOINT = 'checkpoint'
ENEMY_GROUPID = 'enemy_groupid'
MAP_INDEX = 'map_index'
CHECKPOINT_TYPE_ENEMY = 0
CHECKPOINT_TYPE_FLAG = 1
CHECKPOINT_TYPE_END = 2
CHECKPOINT_TYPE_COFFEE = 3
CHECKPOINT_TYPE_ELEVATOR = 4        
CHECKPOINT_TYPE_ELEVATOR_UP = 5     
CHECKPOINT_TYPE_MAP = 6         
CHECKPOINT_TYPE_BOSS = 7     
MAP_FLAGPOLE = 'flagpole'
FLAGPOLE_TYPE_FLAG = 0
FLAGPOLE_TYPE_POLE = 1
FLAGPOLE_TYPE_TOP = 2
MAP_SLIDER = 'slider'
HORIZONTAL = 0
VERTICAL = 1
VELOCITY = 'velocity'
MAP_COIN = 'coin'

#COMPONENT COLOR
COLOR = 'color'
COLOR_TYPE_ORANGE = 0
COLOR_TYPE_GREEN = 1
COLOR_TYPE_RED = 2

#TILE STATES
STAYED = 'stayed'
BUMPED = 'bumped'
OPENED = 'opened'

#COFFEE STATES
REVEAL = 'reveal'
SLIDE = 'slide'

#Player FRAMES
PLAYER_FRAMES = 'image_frames'
RIGHT_SMALL_NORMAL = 'right_small_normal'
RIGHT_BIG_NORMAL = 'right_big_normal'
RIGHT_BIG_FIRE = 'right_big_fire'

#플레이어 상태. auto walking은 깃발 도달 시 사용.
STOPPED = 'stopped'
WALK = 'walk'
JUMP = 'jump'
FALL = 'fall'
FLY = 'fly'
SMALL_TO_BIG = 'small to big'
BIG_TO_FIRE = 'big to fire'
BIG_TO_SMALL = 'big to small'
FLAGPOLE = 'flag pole'
WALK_AUTO = 'walk auto'
END_OF_LEVEL_FALL = 'end of level fall'
GOAL_IN = 'in goal'
DOWN_ELEVATOR = 'down elevator'
UP_ELEVATOR = 'up elevator'

#플레이어 이동. 중력 조절 필요.
PLAYER_SPEED = 'speed'
WALK_ACCEL = 'walk_accel'
RUN_ACCEL = 'run_accel'
JUMP_VEL = 'jump_velocity'
MAX_Y_VEL = 'max_y_velocity'
MAX_RUN_SPEED = 'max_run_speed'
MAX_WALK_SPEED = 'max_walk_speed'
SMALL_TURNAROUND = .35
JUMP_GRAVITY = .31
GRAVITY = 1.01

#LIST of ENEMIES
BOO = 'boo'
PROF = 'prof'
FLY_PROF = 'fly prof'
FIRE_PROF = 'fire prof'
FIRE = 'fire'
PIRANHA = 'piranha'
FIRESTICK = 'firestick'

#boo Stuff
LEFT = 'left'
RIGHT = 'right'
JUMPED_ON = 'jumped on'
DEATH_JUMP = 'death jump'

#PROF STUFF
WORK_SLIDE = 'work slide'

#FLAG STATE
TOP_OF_POLE = 'top of pole'
SLIDE_DOWN = 'slide down'
BOTTOM_OF_POLE = 'bottom of pole'

#사출기
FLYING = 'flying'
BOUNCING = 'bouncing'
EXPLODING = 'exploding'

#IMAGE SHEET
ENEMY_SHEET = 'enemies'
ITEM_SHEET = 'item_images'