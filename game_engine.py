import pygame
import random
from config import *
from player import Player, NPC
from shuttle import Shuttlecock
from coin import Coin
from utils import draw_court, display_message, check_win_condition


class BadmintonGame:
    def __init__(self):
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Badminton Smash Game")
        self.clock = pygame.time.Clock()
        
        # Initialize pygame mixer for sound
        pygame.mixer.init()
        
        # Load sound effects
        try:
            self.hit_sound = pygame.mixer.Sound(HIT_SOUND)
            # Set volume level (0.0 to 1.0)
            self.hit_sound.set_volume(SFX_VOLUME)
        except Exception as e:
            print(f"Error loading sound effect: {e}")
            self.hit_sound = None
            
        # Load game over sound
        try:
            self.game_over_sound = pygame.mixer.Sound(GAME_OVER_SOUND)
            self.game_over_sound.set_volume(SFX_VOLUME * 1.2)  # Slightly louder
        except Exception as e:
            print(f"Error loading game over sound: {e}")
            self.game_over_sound = None
            
        # Load victory sound
        try:
            self.victory_sound = pygame.mixer.Sound(VICTORY_SOUND)
            self.victory_sound.set_volume(SFX_VOLUME * 1.2)  # Slightly louder
        except Exception as e:
            print(f"Error loading victory sound: {e}")
            self.victory_sound = None
        
        # Load and play background music
        try:
            pygame.mixer.music.load(BACKGROUND_MUSIC)
            pygame.mixer.music.set_volume(MUSIC_VOLUME)
            pygame.mixer.music.play(-1)  # -1 means loop indefinitely
        except Exception as e:
            print(f"Error loading background music: {e}")
        
        # Music state
        self.music_playing = True
        self.game_over_played = False
        self.victory_played = False
        
        # Game state
        self.game_state = SERVE_STATE
        self.running = True
        self.match_over = False
        
        # Coin system
        self.coins = []
        self.coin_count = 0
        self.consecutive_wins = 0
        
        # Load coin sound
        try:
            self.coin_sound = pygame.mixer.Sound(COIN_SOUND)
            self.coin_sound.set_volume(SFX_VOLUME)
        except Exception as e:
            print(f"Error loading coin sound: {e}")
            self.coin_sound = None
        
        # Game state variables
        self.showing_controls = False
        
        # Lives system (only for player)
        self.player_lives = 3
        
        # Create players
        self.player = Player(100, 400, BLUE)
        self.npc = NPC(600, 400, RED)
        
        # Create shuttlecock
        self.shuttle = Shuttlecock(self.player.rect.centerx, self.player.rect.top - 20)
        
        # Score
        self.player_score = 0
        self.npc_score = 0
        self.font = pygame.font.SysFont(None, 36)
        
        # Determine who serves first (random)
        self.player_serves = random.choice([True, False])
        self.serving = True
        
        # Shuttlecock possession tracking
        self.shuttle_in_possession = "player" if self.player_serves else "npc"
        
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
        
        # Load crowd cheering sound
        try:
            self.crowd_cheering = pygame.mixer.Sound('assests/crowd-cheering.wav')
            self.crowd_cheering.set_volume(0.7)  # Set appropriate volume
        except Exception as e:
            print(f"Error loading crowd cheering sound: {e}")
            self.crowd_cheering = None
            
        # Victory sequence variables
        self.victory_sequence = False
        self.victory_sequence_start = 0
        self.current_victory_scene = 0
        self.crowd_cheer_played = False  # Track if cheer has been played
        
        # Next button properties - positioned at bottom right
        self.next_button_rect = pygame.Rect(WIDTH - 150, HEIGHT - 80, 100, 40)
        self.next_button_color = (0, 255, 255)  # Neon cyan
        self.next_button_hover_color = (0, 200, 255)  # Slightly darker for hover
        self.next_button_font = pygame.font.SysFont(None, 36)
        self.next_button_text = self.next_button_font.render("Next", True, WHITE)
        self.next_button_text_rect = self.next_button_text.get_rect(center=self.next_button_rect.center)
        
        # Load victory cutscene images
        try:
            self.victory_scenes = [
                pygame.image.load('assests/cutscenes/lv2victorycutecene1.png'),
                pygame.image.load('assests/cutscenes/lv2victorycutscene2.png'),
                pygame.image.load('assests/cutscenes/lv2victorycutscene3.png'),
                pygame.image.load('assests/cutscenes/lv2victorycutscene4.png')
            ]
            # Scale all victory scenes
            self.victory_scenes = [pygame.transform.scale(img, (WIDTH, HEIGHT)) for img in self.victory_scenes]
        except Exception as e:
            print(f"Error loading victory cutscene images: {e}")
            self.victory_scenes = None

        # Load losing scene
        try:
            self.losing_cutscene = pygame.image.load('assests/cutscenes/losingscene.png')
            self.losing_cutscene = pygame.transform.scale(self.losing_cutscene, (WIDTH, HEIGHT))
        except Exception as e:
            print(f"Error loading losing scene: {e}")
            self.losing_cutscene = None
        
        # Restart button properties - bigger and centered
        self.restart_button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2, 200, 70)  # Increased size and centered
        self.restart_button_color = (255, 215, 0)  # Golden color
        self.restart_button_hover_color = (255, 255, 0)  # Bright yellow
        self.restart_button_font = pygame.font.SysFont(None, 60)  # Increased font size
        self.restart_button_text = self.restart_button_font.render("Restart", True, (0, 0, 0))
        self.restart_button_text_rect = self.restart_button_text.get_rect(center=self.restart_button_rect.center)
        
        # Victory dialog texts
        self.victory_dialog_font = pygame.font.SysFont(None, 48)
        self.victory_dialog = self.victory_dialog_font.render("Finally, Alex has won the ultimate sport quest", True, (255, 255, 255))
        self.victory_dialog_rect = self.victory_dialog.get_rect(center=(WIDTH//2, HEIGHT - 100))
        
        # Second victory dialog
        self.victory_dialog2 = self.victory_dialog_font.render("!!! Alex Shock!! ", True, (255, 255, 255))
        self.victory_dialog2_rect = self.victory_dialog2.get_rect(center=(WIDTH//2, HEIGHT - 100))
        
        # Third victory dialog - Alex walking towards door
        self.victory_dialog3 = self.victory_dialog_font.render("The door has appeared again!! ", True, (255, 255, 255))
        self.victory_dialog3_rect = self.victory_dialog3.get_rect(center=(WIDTH//2, HEIGHT - 100))

        self.victory_dialog4 = self.victory_dialog_font.render("Alex walks towards the door...", True, (255, 255, 255))
        self.victory_dialog4_rect = self.victory_dialog4.get_rect(center=(WIDTH//2, HEIGHT - 100))

        self.victory_dialog5 = self.victory_dialog_font.render("Alex is disappearing as he walks towards the door...", True, (255, 255, 255))
        self.victory_dialog5_rect = self.victory_dialog5.get_rect(center=(WIDTH//2, HEIGHT - 100))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                if self.match_over and self.player_lives <= 0:
                    if self.restart_button_rect.collidepoint(event.pos):
                        self.reset_game(full_reset=True)
                elif self.victory_sequence and self.next_button_rect.collidepoint(event.pos):
                    self.advance_victory_scene()
            
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
                    
                    # Play serve sound
                    if self.hit_sound:
                        pygame.mixer.Channel(0).play(self.hit_sound)
                    
                    # Display serving feedback
                    self.show_feedback("Serve!", GREEN)
                
                # Restart match with R key
                if event.key == pygame.K_r and self.match_over:
                    self.reset_game(full_reset=True)  # Full reset when match is over
                
                # Display controls with H key
                if event.key == pygame.K_h:
                    self.showing_controls = not self.showing_controls
                
                # Toggle music with M key
                if event.key == pygame.K_m:
                    if self.music_playing:
                        pygame.mixer.music.pause()
                        self.music_playing = False
                        self.show_feedback("Music Paused", CYAN, 60)
                    else:
                        pygame.mixer.music.unpause()
                        self.music_playing = True
                        self.show_feedback("Music Playing", CYAN, 60)
    
    def show_feedback(self, message, color=WHITE, duration=60):
        """Show a feedback message on screen for a duration in frames"""
        self.feedback_message = message
        self.feedback_color = color
        self.feedback_timer = duration
    
    def update(self):
        # Get the current time for cutscene timing
        current_time = pygame.time.get_ticks()
        
        # Handle victory sequence
        if self.victory_sequence:
            # Calculate time since sequence started
            elapsed = (current_time - self.victory_sequence_start) / 1000  # Convert to seconds
            
            # Auto-advance after 6 seconds if not manually advanced
            if elapsed >= 6:
                self.advance_victory_scene()
            
            # Update button hover effect
            mouse_pos = pygame.mouse.get_pos()
            self.next_button_color = (0, 200, 255) if self.next_button_rect.collidepoint(mouse_pos) else (0, 255, 255)
            
            return
            
        # Regular game updates
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        
        # Update feedback timer
        if self.feedback_timer > 0:
            self.feedback_timer -= 1
        
        # Update players
        self.player.update()
        
        # Update and check coin collection
        self.update_coins()
        
        # Track shuttlecock crossing from player to NPC side
        if self.shuttle.vx > 0 and self.shuttle.x > NET_X:
            # Shuttle is crossing from player to NPC side or continues to be on NPC side
            self.npc.track_shuttlecock(self.shuttle, self.player)
        elif self.shuttle.vx < 0 and self.shuttle.x < NET_X:
            # Player should prepare to receive
            pass
        else:
            # Always track shuttlecock position for better NPC awareness
            self.npc.track_shuttlecock(self.shuttle, self.player)
        
        # Update NPC with AI behavior
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
                # Update possession - shuttle now belongs to player
                self.shuttle_in_possession = "player"
                
                # Play hit sound effect
                if self.hit_sound:
                    # Play the sound with pitch variation based on shot type
                    pitch = 1.0  # Default pitch
                    if self.player.swing_type == "smash":
                        pitch = 1.2  # Higher pitch for smash
                    elif self.player.swing_type == "drop":
                        pitch = 0.8  # Lower pitch for drop shot
                    
                    # Use a channel to control pitch (pygame doesn't directly support pitch)
                    # Instead, we play at normal pitch but use different volumes for shot types
                    channel = pygame.mixer.find_channel()
                    if channel:
                        channel.set_volume(0.7 * (pitch if pitch > 1.0 else 1.0))
                        channel.play(self.hit_sound)
                
                if self.player.swing_type == "smash":
                    self.show_feedback("SMASH!", (255, 0, 0))
                elif self.player.swing_type == "drop":
                    self.show_feedback("Drop Shot", (0, 255, 255))
                else:
                    self.show_feedback("Hit!", GREEN)
            
            # Check if NPC hits shuttlecock
            if self.npc.hit_shuttlecock(self.shuttle):
                # Update possession - shuttle now belongs to NPC
                self.shuttle_in_possession = "npc"
                
                # Play hit sound effect with different characteristics for NPC
                if self.hit_sound:
                    # Use slightly different pitch/volume for NPC hits
                    pitch = 1.0  # Default pitch
                    if self.npc.swing_type == "smash":
                        pitch = 1.3  # Higher pitch for smash
                    elif self.npc.swing_type == "drop":
                        pitch = 0.9  # Lower pitch for drop shot
                    
                    # Use a channel to control volume
                    channel = pygame.mixer.find_channel()
                    if channel:
                        channel.set_volume(0.6 * (pitch if pitch > 1.0 else 1.0))
                        channel.play(self.hit_sound)
                
                if self.npc.swing_type == "smash":
                    self.show_feedback("NPC SMASH!", (255, 100, 100))
                elif self.npc.swing_type == "drop":
                    self.show_feedback("NPC Drop", (100, 200, 255))
            
            # Check if shuttlecock hits the ground, goes out of bounds, or hits the net
            if self.shuttle.is_grounded() or self.shuttle.out_of_bounds:
                # Reset shuttle possession
                self.shuttle_in_possession = "none"
                
                # Award point based on where the fault occurred
                if self.shuttle.is_grounded():
                    # Point goes to opposite side of where shuttlecock landed
                    if self.shuttle.x < NET_X:
                        # Point for NPC if shuttle lands in player's court
                        self.npc_score += 1
                        self.player_serves = False
                        self.show_feedback("Point for NPC!", RED)
                        
                        # Check if player loses a life
                        if self.npc_score % 10 == 0:  # Lose a life every 10 points
                            self.player_lives -= 1
                            self.show_feedback(f"Player lost a life! Lives: {self.player_lives}", RED, 120)
                            # Reset scores after life loss
                            self.player_score = 0
                            self.npc_score = 0
                    else:
                        # Point for player if shuttle lands in NPC's court
                        self.player_score += 1
                        self.player_serves = True
                        self.show_feedback("Point for Player!", BLUE)
                        
                        # Track consecutive player wins for coin spawning
                        self.consecutive_wins += 1
                        
                        # Spawn coins after two consecutive wins
                        if self.consecutive_wins >= 2:
                            self.spawn_coins(3)  # Spawn 3 coins
                            self.consecutive_wins = 0  # Reset counter
                elif self.shuttle.out_of_bounds:
                    # Point goes to the side that didn't hit it last
                    # We'll determine this based on the direction the shuttle was moving
                    if self.shuttle.vx > 0:
                        # Shuttle was moving right (toward NPC), so last hit by player
                        self.npc_score += 1
                        self.player_serves = False
                        self.show_feedback("Out of bounds! Point for NPC", RED)
                        
                        # Check if player loses a life
                        if self.npc_score % 10 == 0:  # Lose a life every 10 points
                            self.player_lives -= 1
                            self.show_feedback(f"Player lost a life! Lives: {self.player_lives}", RED, 120)
                            # Reset scores after life loss
                            self.player_score = 0
                            self.npc_score = 0
                    else:
                        # Shuttle was moving left (toward player), so last hit by NPC
                        self.player_score += 1
                        self.player_serves = True
                        self.show_feedback("Out of bounds! Point for Player", BLUE)
                        
                        # Track consecutive player wins for coin spawning
                        self.consecutive_wins += 1
                        
                        # Spawn coins after two consecutive wins
                        if self.consecutive_wins >= 2:
                            self.spawn_coins(3)  # Spawn 3 coins
                            self.consecutive_wins = 0  # Reset counter
                
                # Check if match has been won due to lives
                if self.player_lives <= 0:
                    self.match_over = True
                    self.show_feedback("Game Over! Player is out of lives!", RED, 120)
                else:
                    # Check if match has been won by score
                    winner = check_win_condition(self.player_score, self.npc_score)
                    if winner:
                        self.match_over = True
                        self.show_feedback(f"{winner} wins the match!", GREEN if winner == "Player" else RED, 120)
                        
                        # Player victory event
                        if winner == "Player":
                            pass  # No video cutscene
                
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
        # Handle victory sequence display
        if self.victory_sequence and self.victory_scenes:
            self.screen.fill(BLACK)
            self.screen.blit(self.victory_scenes[self.current_victory_scene], (0, 0))
            
            # Play crowd cheering on first scene
            if self.current_victory_scene == 0 and not self.crowd_cheer_played and self.crowd_cheering:
                self.crowd_cheering.play(-1)  # -1 means loop indefinitely
                self.crowd_cheer_played = True
                
            # Show appropriate dialog based on current scene
            if self.current_victory_scene == 0:
                self.screen.blit(self.victory_dialog, self.victory_dialog_rect)
            elif self.current_victory_scene == 1:
                self.screen.blit(self.victory_dialog2, self.victory_dialog2_rect)
            elif self.current_victory_scene == 2:
                self.screen.blit(self.victory_dialog3, self.victory_dialog3_rect)
            
            # Draw Next button
            pygame.draw.rect(self.screen, self.next_button_color, self.next_button_rect, border_radius=10)
            self.screen.blit(self.next_button_text, self.next_button_text_rect)
            
            pygame.display.flip()
            return
            
        # Normal game rendering
        if self.court_img:
            self.screen.blit(self.court_img, (0, 0))
        else:
            self.screen.fill(WHITE)
            draw_court(self.screen)
        
        # Draw players
        self.player.draw(self.screen)
        self.npc.draw(self.screen)
        
        # Draw shuttlecock only if in play
        if not self.serving or self.game_state == PLAY_STATE:
            self.shuttle.draw(self.screen)
            
        # Draw all coins
        for coin in self.coins:
            coin.draw(self.screen)
        
        # Draw scores
        score_text = self.font.render(f"{self.player_score} - {self.npc_score}", True, BLACK)
        self.screen.blit(score_text, (WIDTH//2 - 30, 20))
        
        # Draw lives (hearts)
        for i in range(self.player_lives):
            pygame.draw.polygon(self.screen, BLUE, 
                [(30 + i*25, 30), (40 + i*25, 20), (50 + i*25, 30), (40 + i*25, 45)])
                
        # Draw coin count below lives
        coin_text = self.font.render(f"Coins: {self.coin_count}", True, YELLOW)
        self.screen.blit(coin_text, (30, 55))  # Position below the hearts
        
        # Draw serve instructions
        if self.game_state == SERVE_STATE and self.player_serves and self.serving and not self.match_over:
            display_message(self.screen, "Press SPACE to serve", (WIDTH//2 - 100, 100))
        
        # Draw feedback message
        if self.feedback_timer > 0:
            feedback_font = pygame.font.SysFont(None, 48)
            text = feedback_font.render(self.feedback_message, True, self.feedback_color)
            self.screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 150))
        
        # Draw controls only when requested
        if self.showing_controls:
            controls = [
                "Controls:",
                "Move Left/Right: Arrow Left/Right",
                "Jump: Arrow Up",
                "Crouch: Down Arrow (when on ground)",
                "Normal Shot: Z",
                "Smash (while in air): X",
                "Drop Shot: C",
                "Toggle Controls: H",
                "Toggle Music: M"
            ]
            
            # Draw a semi-transparent background for better readability
            controls_surface = pygame.Surface((300, 225))
            controls_surface.set_alpha(200)
            controls_surface.fill((240, 240, 240))
            self.screen.blit(controls_surface, (10, HEIGHT - 210))
            
            control_y = HEIGHT - 200
            for line in controls:
                control_text = pygame.font.SysFont(None, 24).render(line, True, BLACK)
                self.screen.blit(control_text, (20, control_y))
                control_y += 25
        
        # Draw badminton rules
        if self.game_state == SERVE_STATE and not self.showing_controls:
            # Display compact rules at the bottom of the screen
            display_message(self.screen, f"First to {POINTS_TO_WIN} wins. Must win by {MIN_POINT_DIFFERENCE} clear points.", 
                           (50, HEIGHT - 40), 20)
        
        # Display match result if over
        if self.match_over:
            self.screen.fill(BLACK)
            
            if self.player_lives <= 0 and self.losing_cutscene:
                # Display the losing scene image
                self.screen.blit(self.losing_cutscene, (0, 0))
                
                # Draw restart button with hover effect
                mouse_pos = pygame.mouse.get_pos()
                button_color = self.restart_button_hover_color if self.restart_button_rect.collidepoint(mouse_pos) else self.restart_button_color
                pygame.draw.rect(self.screen, button_color, self.restart_button_rect, border_radius=10)
                self.screen.blit(self.restart_button_text, self.restart_button_text_rect)
            
            elif self.player_score > self.npc_score and self.victory_scenes:
                # Start victory sequence
                if not self.victory_sequence:
                    self.victory_sequence = True
                    self.victory_sequence_start = pygame.time.get_ticks()
                    self.current_victory_scene = 0
            else:
                # Fallback to displaying text messages if images aren't available
                winner = "Player" if (self.player_score > self.npc_score and self.player_lives > 0) else "NPC"
                display_message(self.screen, f"{winner} wins the match!", (WIDTH//2 - 120, HEIGHT//2 - 50), 48)
                if self.player_lives <= 0:
                    display_message(self.screen, "Player is out of lives!", (WIDTH//2 - 100, HEIGHT//2), 36)
                else:
                    display_message(self.screen, f"Final score: {self.player_score}-{self.npc_score}", (WIDTH//2 - 100, HEIGHT//2), 36)
                display_message(self.screen, "Press R to restart", (WIDTH//2 - 80, HEIGHT//2 + 50), 28)
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.clock.tick(60)
            self.handle_events()
            self.update()
            self.draw()
        
        pygame.quit()

    def reset_game(self, full_reset=False):
        """Reset the game state after losing a life. 
        If full_reset is True, reset everything including lives."""
        
        # Reset scores only on full reset
        if full_reset:
            self.player_score = 0
            self.npc_score = 0
            self.player_lives = 3
            self.match_over = False
            self.game_over_played = False  # Reset sound flag
            self.victory_played = False    # Reset victory sound flag
            self.crowd_cheer_played = False  # Reset crowd cheer flag
            
            # Reset coin system on full game reset
            self.consecutive_wins = 0
            # Don't reset coin_count to preserve player's collection
            
            # Restart background music if it was stopped
            if not self.music_playing:
                pygame.mixer.music.play(-1)
                self.music_playing = True
            
            # Restore background music volume
            pygame.mixer.music.set_volume(MUSIC_VOLUME)
        
        # Reset game state
        self.game_state = SERVE_STATE
        
        # Reset player positions
        self.player.rect.x = 100
        self.player.rect.y = 400
        self.npc.rect.x = 600 
        self.npc.rect.y = 400
        
        # Reset shuttlecock
        self.shuttle.x = self.player.rect.centerx
        self.shuttle.y = self.player.rect.top - 20
        self.shuttle.vx = 0
        self.shuttle.vy = 0
        self.shuttle.out_of_bounds = False
        self.shuttle.gravity_multiplier = 1.0
        
        # Reset serving state
        self.serving = True
        
        # Randomly determine who serves
        self.player_serves = random.choice([True, False])
        
        # Reset shuttle possession
        self.shuttle_in_possession = "player" if self.player_serves else "npc"
        
        # Show feedback message
        if not full_reset:
            if self.player_lives > 0:
                self.show_feedback("Get ready for the next round!", GREEN, 120)
            else:
                self.match_over = True

    def update_coins(self):
        """Update coins and check for player collection"""
        # Update all coin animations
        for coin in self.coins:
            coin.update()
            
        # Check for coin collection
        for coin in self.coins:
            if not coin.collected and coin.collides_with_player(self.player.rect):
                # Collect the coin
                coin.collect()
                self.coin_count += 1
                
                # Play coin sound
                if self.coin_sound:
                    pygame.mixer.Channel(2).play(self.coin_sound)
                
                # Show feedback
                self.show_feedback(f"Coin Collected! Total: {self.coin_count}", YELLOW, 60)
        
        # Remove collected coins after a delay
        self.coins = [coin for coin in self.coins if not coin.collected]
    
    def spawn_coins(self, count=3):
        """Spawn coins randomly on the player's side of court"""
        for _ in range(count):
            # Randomize position only on player's side (left of the net)
            x = random.randint(COURT_LEFT + 50, NET_X - 70)
            
            # Start coins high up for floating down effect
            y = random.randint(50, 150)
                
            # Create and add the coin
            self.coins.append(Coin(x, y))
            
        # Show feedback
        self.show_feedback("Coins Spawned!", YELLOW, 60)

    def advance_victory_scene(self):
        """Advance to the next victory scene or end sequence"""
        if self.current_victory_scene < 3:
            # Stop crowd cheering when moving from first scene
            if self.current_victory_scene == 0 and self.crowd_cheering:
                self.crowd_cheering.stop()
            self.current_victory_scene += 1
            self.victory_sequence_start = pygame.time.get_ticks()
        else:
            # End of sequence, reset game
            self.reset_game(full_reset=True)