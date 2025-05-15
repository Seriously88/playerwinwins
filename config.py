# Game window settings
WIDTH = 800
HEIGHT = 600

# Physics constants
GRAVITY = 0.5
JUMP_STRENGTH = -10
SHUTTLE_GRAVITY = 0.4
SHUTTLE_INITIAL_VELOCITY = -8

# Player movement
SPRINT_SPEED = 8
WALK_SPEED = 4

# Game states
SERVE_STATE = 0
PLAY_STATE = 1

# Badminton rules
POINTS_TO_WIN = 15
MAX_SCORE = 30
MIN_POINT_DIFFERENCE = 2
GAMES_TO_WIN_MATCH = 2

# Court dimensions
COURT_GROUND_Y = 500
NET_X = WIDTH // 2
COURT_LEFT = 20
COURT_RIGHT = WIDTH - 20

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 100, 255)
RED = (255, 50, 50)
GREEN = (50, 200, 50)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
PURPLE = (150, 50, 200)
ORANGE = (255, 165, 0)
GRAY = (200, 200, 200)

# Shot settings
NORMAL_SHOT_SPEED = 8
SMASH_SHOT_SPEED = 12
DROP_SHOT_SPEED = 4
SHOT_COOLDOWN = 30

# Asset paths
COURT_IMAGE = "assests/Badminton court.png"
PLAYER_IMAGE = "assests/player.jpg"
SHUTTLE_IMAGE = "assests/shuttlecock.jpg"
NPC_IMAGE = "assests/npc.png"
HIT_SOUND = "assests/BADMINTON SOUND EFFECT IN HIGH QUALITY.mp4"
BACKGROUND_MUSIC = "assests/Davit Barqaia Tell My Why Remix by Awesome Free Sound Effects (online-audio-converter.com).wav"
GAME_OVER_SOUND = "assests/Game Over _ 01 - ASMR - Free Sound Effects (online-audio-converter.com).wav"
VICTORY_SOUND = "assests/Victory Sound Effect.wav"

# Sound settings
MUSIC_VOLUME = 0.3  # Background music volume (0.0 to 1.0)
SFX_VOLUME = 0.7    # Sound effects volume (0.0 to 1.0)