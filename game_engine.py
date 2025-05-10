import pygame
import random
from config import *
from player import Player, NPC
from shuttle import Shuttlecock
from utils import draw_court, display_message, check_win_condition

class BadmintonGame:
    def __init__(self):
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Badminton Smash Game")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.game_state = SERVE_STATE
        self.running = True
        self.games_played = 0
        self.match_over = False
        
        # Create players
        self.player = Player(100, 400, BLUE)
        self.npc = NPC(600, 400, RED)
        
        # Create shuttlecock
        self.shuttle = Shuttlecock(self.player.rect.centerx, self.player.rect.top - 20)
        
        # Score
        self.player_score = 0
        self.npc_score = 0
        self.player_games = 0
        self.npc_games = 0
        self.font = pygame.font.SysFont(None, 36)
        
        # Determine who serves first (random)
        self.player_serves = random.choice([True, False])
        self.serving = True
        
        # Shot feedback
        self.feedback_message = ""
        self.feedback_timer = 0
        self.feedback_color = BLACK
        
        # Load court image
        try:
            self.court_img = pygame.image.load(COURT_IMAGE)
            self.court_img = pygame.transform.scale(self.court_img, (WIDTH, HEIGHT))
        except Exception as e:
            print(f"Error loading court image: {e}")
            self.court_img = None
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Handle key presses
            if event.type == pygame.KEYDOWN:
                # Serve with spacebar
                if self.game_state == SERVE_STATE and event.key == pygame.K_SPACE and self.player_serves and not self.match_over and self.serving:
                    # Set initial velocity for proper animation instead of teleporting
                    self.serving = False
                    
                    # Add some randomness to the serve
                    angle_variance = random.uniform(-0.3, 0.3)
                    speed = random.uniform(7, 9)
                    
                    # Set initial velocities for player serve (angled toward NPC)
                    self.shuttle.vx = speed
                    self.shuttle.vy = SHUTTLE_INITIAL_VELOCITY * (1 + angle_variance)
                    
                    # Display serving feedback
                    self.show_feedback("Serve!", GREEN)
                
                # Restart match with R key
                if event.key == pygame.K_r and self.match_over:
                    self.__init__()  # Reset the game
                    
                # Display controls with H key
                if event.key == pygame.K_h:
                    self.show_controls = not getattr(self, 'show_controls', False)
    
    def show_feedback(self, message, color=WHITE, duration=60):
        """Show a feedback message on screen for a duration in frames"""
        self.feedback_message = message
        self.feedback_color = color
        self.feedback_timer = duration
    
    def update(self):
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        
        # Update feedback timer
        if self.feedback_timer > 0:
            self.feedback_timer -= 1
        
        # Update players
        self.player.update()
        
        # Update NPC with AI behavior
        self.npc.track_shuttlecock(self.shuttle)
        self.npc.update()
        
        # Don't proceed with game logic if match is over
        if self.match_over:
            return
        
        # Update shuttlecock position in all states
        if not self.serving:
            self.shuttle.update()
            
            # If we're in serve state and shuttlecock is moving, transition to play state
            if self.game_state == SERVE_STATE:
                self.game_state = PLAY_STATE
        
        # Check for racket hits
        if self.game_state == PLAY_STATE:
            # Check if player hits shuttlecock
            if self.player.hit_shuttlecock(self.shuttle):
                if self.player.swing_type == "smash":
                    self.show_feedback("SMASH!", (255, 0, 0))
                elif self.player.swing_type == "drop":
                    self.show_feedback("Drop Shot", (0, 255, 255))
                else:
                    self.show_feedback("Hit!", GREEN)
            
            # Check if NPC hits shuttlecock
            if self.npc.hit_shuttlecock(self.shuttle):
                if self.npc.swing_type == "smash":
                    self.show_feedback("NPC SMASH!", (255, 100, 100))
                elif self.npc.swing_type == "drop":
                    self.show_feedback("NPC Drop", (100, 200, 255))
            
            # Check if shuttlecock hits the ground, goes out of bounds, or hits the net
            if self.shuttle.is_grounded() or self.shuttle.out_of_bounds:
                # Award point based on where the fault occurred
                if self.shuttle.is_grounded():
                    # Point goes to opposite side of where shuttlecock landed
                    if self.shuttle.x < NET_X:
                        # Point for NPC if shuttle lands in player's court
                        self.npc_score += 1
                        self.player_serves = False
                        self.show_feedback("Point for NPC!", RED)
                    else:
                        # Point for player if shuttle lands in NPC's court
                        self.player_score += 1
                        self.player_serves = True
                        self.show_feedback("Point for Player!", BLUE)
                elif self.shuttle.out_of_bounds:
                    # Point goes to the side that didn't hit it last
                    # We'll determine this based on the direction the shuttle was moving
                    if self.shuttle.vx > 0:
                        # Shuttle was moving right (toward NPC), so last hit by player
                        self.npc_score += 1
                        self.player_serves = False
                        self.show_feedback("Out of bounds! Point for NPC", RED)
                    else:
                        # Shuttle was moving left (toward player), so last hit by NPC
                        self.player_score += 1
                        self.player_serves = True
                        self.show_feedback("Out of bounds! Point for Player", BLUE)
                
                # Check if game has been won
                winner = check_win_condition(self.player_score, self.npc_score)
                if winner:
                    # Add a game to the winner's total
                    if winner == "Player":
                        self.player_games += 1
                        self.show_feedback("Player wins the game!", BLUE, 120)
                    else:
                        self.npc_games += 1
                        self.show_feedback("NPC wins the game!", RED, 120)
                    
                    # Check if match has been won (best of 3)
                    if self.player_games >= GAMES_TO_WIN_MATCH or self.npc_games >= GAMES_TO_WIN_MATCH:
                        self.match_over = True
                    else:
                        # Reset for the next game
                        self.player_score = 0
                        self.npc_score = 0
                        self.games_played += 1
                
                # Reset for next serve
                self.game_state = SERVE_STATE
                self.serving = True
                
                # Reset shuttlecock for next serve
                self.shuttle.out_of_bounds = False
                self.shuttle.vx = 0
                self.shuttle.vy = 0
        
        # Auto-serve for NPC after a delay
        elif self.game_state == SERVE_STATE and not self.player_serves and self.serving:
            # NPC serve after a short delay
            pygame.time.delay(500)  # Reduced delay for better responsiveness
            
            # Set initial velocity for proper animation instead of teleporting
            self.serving = False
            
            # Add some randomness to the serve
            angle_variance = random.uniform(-0.3, 0.3)
            speed = random.uniform(7, 9)
            
            # Set initial velocities for NPC serve (angled toward player)
            self.shuttle.vx = -speed
            self.shuttle.vy = SHUTTLE_INITIAL_VELOCITY * (1 + angle_variance)
            
            self.show_feedback("NPC Serve", RED)
        
        # Set shuttle position during serve state if we're still in serving mode
        if self.game_state == SERVE_STATE and self.serving:
            if self.player_serves:
                self.shuttle.x = self.player.rect.centerx
                self.shuttle.y = self.player.rect.top - 20
            else:
                self.shuttle.x = self.npc.rect.centerx
                self.shuttle.y = self.npc.rect.top - 20
    
    def draw(self):
        # Fill background
        if self.court_img:
            self.screen.blit(self.court_img, (0, 0))
        else:
            self.screen.fill(WHITE)
            draw_court(self.screen)
        
        # Draw net
        pygame.draw.rect(self.screen, BLACK, (NET_X - 2, 0, 4, COURT_GROUND_Y))
        
        # Draw players
        self.player.draw(self.screen)
        self.npc.draw(self.screen)
        
        # Draw shuttlecock
        self.shuttle.draw(self.screen)
        
        # Draw scores and games
        score_text = self.font.render(f"{self.player_score} - {self.npc_score}", True, BLACK)
        self.screen.blit(score_text, (WIDTH//2 - 30, 20))
        
        games_text = self.font.render(f"Games: {self.player_games} - {self.npc_games}", True, BLACK)
        self.screen.blit(games_text, (WIDTH//2 - 60, 60))
        
        # Draw serve instructions
        if self.game_state == SERVE_STATE and self.player_serves and self.serving and not self.match_over:
            display_message(self.screen, "Press SPACE to serve", (WIDTH//2 - 100, 100))
        
        # Draw feedback message
        if self.feedback_timer > 0:
            feedback_font = pygame.font.SysFont(None, 48)
            text = feedback_font.render(self.feedback_message, True, self.feedback_color)
            self.screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 150))
        
        # Draw controls if requested
        if getattr(self, 'show_controls', False):
            controls = [
                "Controls:",
                "Move: Arrow Left/Right",
                "Jump: Space",
                "Crouch: Down Arrow",
                "Normal Shot: Z",
                "Smash (while jumping): X",
                "Drop Shot: C",
                "Toggle Controls: H"
            ]
            
            control_y = HEIGHT - 200
            for line in controls:
                control_text = pygame.font.SysFont(None, 24).render(line, True, BLACK)
                self.screen.blit(control_text, (20, control_y))
                control_y += 25
        
        # Draw badminton rules
        if self.game_state == SERVE_STATE and not getattr(self, 'show_controls', False):
            # Display compact rules at the bottom of the screen
            display_message(self.screen, f"First to {POINTS_TO_WIN} wins. If {POINTS_TO_WIN-1}-{POINTS_TO_WIN-1}, win by {MIN_POINT_DIFFERENCE} points. If {MAX_SCORE-1}-{MAX_SCORE-1}, first to {MAX_SCORE} wins.", 
                           (50, HEIGHT - 40), 20)
        
        # Display match result if over
        if self.match_over:
            winner = "Player" if self.player_games > self.npc_games else "NPC"
            display_message(self.screen, f"{winner} wins the match!", (WIDTH//2 - 120, HEIGHT//2 - 50), 48)
            display_message(self.screen, f"Final score: {self.player_games}-{self.npc_games}", (WIDTH//2 - 100, HEIGHT//2), 36)
            display_message(self.screen, "Press R to restart", (WIDTH//2 - 80, HEIGHT//2 + 50), 28)
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.clock.tick(60)
            self.handle_events()
            self.update()
            self.draw()
        
        pygame.quit()
