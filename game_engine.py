import pygame
import random
import math
import cv2
import numpy as np
from config import *
from player import Player, NPC
from shuttle import Shuttlecock
from coin import Coin
from bomb import Bomb
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
        
        # Load victory video audio
        try:
            self.victory_video_audio = pygame.mixer.Sound('assests/endscenessound.WAV')
            self.victory_video_audio.set_volume(0.8)  # Set appropriate volume
        except Exception as e:
            print(f"Error loading victory video audio: {e}")
            self.victory_video_audio = None
        
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
            
        # Load cutscene sound effect
        try:
            self.cutscene_sound = pygame.mixer.Sound('assests/Cutscenes.wav')
            self.cutscene_sound.set_volume(0.7)  # Set appropriate volume
        except Exception as e:
            print(f"Error loading cutscene sound: {e}")
            self.cutscene_sound = None

        # Load final victory sound effect
        try:
            self.final_victory_sound = pygame.mixer.Sound('assests/Victory Sound Effect.wav')
            self.final_victory_sound.set_volume(0.8)  # Slightly louder for final victory
        except Exception as e:
            print(f"Error loading final victory sound: {e}")
            self.final_victory_sound = None

        # Track which scenes have played their sound
        self.scene_sounds_played = {2: False, 3: False, 4: False, 5: False}
        
        # Victory sequence variables
        self.victory_sequence = False
        self.victory_sequence_start = 0
        self.victory_video_played = False
        
        # Next button properties - positioned at bottom right
        self.next_button_rect = pygame.Rect(WIDTH - 150, HEIGHT - 80, 100, 40)
        self.next_button_color = (0, 255, 255)  # Neon cyan
        self.next_button_hover_color = (0, 200, 255)  # Slightly darker for hover
        self.next_button_font = pygame.font.SysFont(None, 36)
        self.next_button_text = self.next_button_font.render("Skip", True, WHITE)
        self.next_button_text_rect = self.next_button_text.get_rect(center=self.next_button_rect.center)
        
        # Load losing scene and sound
        try:
            self.losing_scene = pygame.image.load('assests/cutscenes/losingscene.png')
            self.losing_scene = pygame.transform.scale(self.losing_scene, (WIDTH, HEIGHT))
            self.losing_sound = pygame.mixer.Sound('assests/losesound effect.wav')
            self.losing_sound.set_volume(0.8)  # Set appropriate volume
        except Exception as e:
            print(f"Error loading losing scene assets: {e}")
            self.losing_scene = None
            self.losing_sound = None
        
        # Restart button properties
        self.restart_button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 100, 200, 60)
        self.restart_button_color = (255, 215, 0)  # Gold color
        self.restart_button_hover_color = (255, 255, 0)  # Bright yellow for hover
        self.restart_button_font = pygame.font.SysFont(None, 48)
        self.restart_button_text = self.restart_button_font.render("Restart Game", True, (0, 0, 0))
        self.restart_button_text_rect = self.restart_button_text.get_rect(center=self.restart_button_rect.center)
        
        # Track if losing sound has been played
        self.losing_sound_played = False
        
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
        
        # Flash effect variables
        self.flash_effect = False
        self.flash_start_time = 0
        self.flash_duration = 2000  # Changed back to 2 seconds (2000 milliseconds)
        self.flash_intensity = 0
        self.flash_speed = 15  # Speed of flash pulsing
        
        # Bomb system
        self.bombs = []
        self.bomb_spawn_timer = 0
        self.bomb_spawn_interval = 300  # Spawn a bomb every ~5 seconds
        
        # Load bomb hit sound
        try:
            self.bomb_hit_sound = pygame.mixer.Sound('assests/bomb_hit.wav')
            self.bomb_hit_sound.set_volume(SFX_VOLUME * 1.2)
        except Exception as e:
            print(f"Error loading bomb hit sound: {e}")
            self.bomb_hit_sound = None
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Handle mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                if self.match_over and self.player_lives <= 0:
                    # Check if restart button was clicked
                    if self.restart_button_rect.collidepoint(event.pos):
                        # Stop the losing sound if it's playing
                        if self.losing_sound:
                            self.losing_sound.stop()
                        self.reset_game(full_reset=True)
                        self.losing_sound_played = False  # Reset the sound played flag
            
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
        
        # Start flash effect after 5 consecutive wins
        if "Point for Player" in message:
            self.consecutive_wins += 1
            print(f"Consecutive wins: {self.consecutive_wins}")  # Debug print
            if self.consecutive_wins >= 5:
                self.flash_effect = True
                self.flash_start_time = pygame.time.get_ticks()
                self.consecutive_wins = 0  # Reset consecutive wins
                self.show_feedback("FLASH ATTACK!", (255, 255, 0), 120)  # Show special feedback for flash effect
        elif "Point for NPC" in message:
            # Only reset consecutive wins when NPC scores
            self.consecutive_wins = 0
    
    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Update bomb spawn timer
        self.bomb_spawn_timer += 1
        if self.bomb_spawn_timer >= self.bomb_spawn_interval:
            self.spawn_bomb()
            self.bomb_spawn_timer = 0
            
        # Update and check bomb collisions
        for bomb in self.bombs[:]:  # Use slice to avoid modification during iteration
            bomb.update()
            
            # Check for collision with player
            if bomb.collides_with_player(self.player.rect):
                coin_penalty = bomb.hit()
                self.coin_count = max(0, self.coin_count + coin_penalty)  # Don't go below 0
                self.show_feedback("Lost 5 coins!", (255, 0, 0), 120)
                
                # Play bomb hit sound
                if self.bomb_hit_sound:
                    pygame.mixer.Channel(3).play(self.bomb_hit_sound)
            
            # Remove bombs that are marked for removal
            if bomb.should_remove:
                self.bombs.remove(bomb)
        
        # Get the current time for cutscene timing
        current_time = pygame.time.get_ticks()
        
        # Update flash effect
        if self.flash_effect:
            time_elapsed = current_time - self.flash_start_time
            if time_elapsed < self.flash_duration:
                # Create a pulsing effect using sine wave
                self.flash_intensity = abs(math.sin(time_elapsed * 0.01)) * 255  # Increased max intensity
            else:
                self.flash_effect = False
                self.flash_intensity = 0
        
        # Handle victory sequence
        if self.victory_sequence:
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
                        
                        # Spawn coins after two consecutive wins
                        if self.consecutive_wins >= 2:
                            self.spawn_coins(3)  # Spawn 3 coins
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
                        
                        # Spawn coins after two consecutive wins
                        if self.consecutive_wins >= 2:
                            self.spawn_coins(3)  # Spawn 3 coins
                
                # Check for match over
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
        if self.victory_sequence:
            if not hasattr(self, 'victory_video_played'):
                self.victory_video_played = False
            
            if not self.victory_video_played:
                self.victory_video_played = True
                if not self.play_victory_video():
                    return
                # End the game after video
                self.running = False
                return
            
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
        
        # Draw lives (hearts) - increased size
        heart_size = 40  # Increased from default
        for i in range(self.player_lives):
            pygame.draw.polygon(self.screen, BLUE, 
                [(30 + i*45, 30),  # Increased spacing between hearts
                 (45 + i*45, 15),  # Increased heart size
                 (60 + i*45, 30), 
                 (45 + i*45, 55)])  # Made hearts taller
                
        # Draw coin count below lives with larger font
        coin_font = pygame.font.SysFont(None, 48)  # Increased font size
        coin_text = coin_font.render(f"Coins: {self.coin_count}", True, YELLOW)
        self.screen.blit(coin_text, (30, 70))  # Adjusted position to account for larger hearts
        
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
        
        # Draw all bombs
        for bomb in self.bombs:
            bomb.draw(self.screen)
        
        # Display match result if over
        if self.match_over:
            if self.player_lives <= 0:
                # Fill screen with black first
                self.screen.fill(BLACK)
                
                # Display the losing scene image
                if self.losing_scene:
                    self.screen.blit(self.losing_scene, (0, 0))
                    
                    # Play losing sound if not already played
                    if not self.losing_sound_played and self.losing_sound:
                        self.losing_sound.play()
                        self.losing_sound_played = True
                    
                    # Draw restart button with hover effect
                    mouse_pos = pygame.mouse.get_pos()
                    button_color = self.restart_button_hover_color if self.restart_button_rect.collidepoint(mouse_pos) else self.restart_button_color
                    pygame.draw.rect(self.screen, button_color, self.restart_button_rect, border_radius=10)
                    self.screen.blit(self.restart_button_text, self.restart_button_text_rect)

            elif self.player_score > self.npc_score:
                # Start victory sequence
                if not self.victory_sequence:
                    self.victory_sequence = True
                    self.victory_sequence_start = pygame.time.get_ticks()
            else:
                # Fallback text messages
                display_message(self.screen, "Game Over!", (WIDTH//2 - 100, HEIGHT//2 - 50), 48)
                display_message(self.screen, f"Final score: {self.player_score}-{self.npc_score}", (WIDTH//2 - 100, HEIGHT//2), 36)
                display_message(self.screen, "Press R to restart", (WIDTH//2 - 80, HEIGHT//2 + 50), 28)
        
        # Draw flash effect overlay
        if self.flash_effect and self.flash_intensity > 0:
            flash_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash_color = (255, 255, 255, int(self.flash_intensity))
            flash_surface.fill(flash_color)
            self.screen.blit(flash_surface, (0, 0))
        
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
            self.game_over_played = False
            self.victory_played = False
            self.victory_sequence = False
            self.victory_video_played = False
            self.losing_sound_played = False  # Reset losing sound flag
            
            # Reset flash effect
            self.flash_effect = False
            self.flash_intensity = 0
            self.consecutive_wins = 0
            
            # Reset coin system
            self.coin_count = 0
            
            # Reset bomb system
            self.bombs.clear()
            self.bomb_spawn_timer = 0
            
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

    def spawn_bomb(self):
        """Spawn a bomb at a random position above the player's side of the court"""
        # Only spawn between left court edge and net (player's side)
        x = random.randint(COURT_LEFT + 50, NET_X - 50)
        y = -20  # Start above the screen
        self.bombs.append(Bomb(x, y))

    def play_victory_video(self):
        """Play the victory ending video sequence with confetti effect"""
        # Open the video file
        video = cv2.VideoCapture('assests/introscene+BGM/victoryendingscene(1).mp4')
        
        if not video.isOpened():
            print("Error loading victory video file")
            return False
            
        # Stop background music during video
        pygame.mixer.music.pause()
        
        # Play victory video audio
        if self.victory_video_audio:
            pygame.mixer.Channel(1).play(self.victory_video_audio)
        
        # Create confetti effect
        confetti = Confetti()
        confetti_start_time = pygame.time.get_ticks()
        confetti_duration = 4000  # 4 seconds (4000 milliseconds)
            
        while True:
            ret, frame = video.read()
            
            if not ret:
                break
                
            # Convert frame from BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (WIDTH, HEIGHT))
            
            # Convert to pygame surface
            frame = np.swapaxes(frame, 0, 1)
            frame = pygame.surfarray.make_surface(frame)
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    video.release()
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        video.release()
                        return True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        if self.next_button_rect.collidepoint(event.pos):
                            video.release()
                            return True
            
            # Display frame
            self.screen.blit(frame, (0, 0))
            
            # Update and draw confetti if within duration
            current_time = pygame.time.get_ticks()
            if current_time - confetti_start_time < confetti_duration:
                confetti.update()
                confetti.draw(self.screen)
            
            # Draw skip button with hover effect
            mouse_pos = pygame.mouse.get_pos()
            button_color = self.next_button_hover_color if self.next_button_rect.collidepoint(mouse_pos) else self.next_button_color
            pygame.draw.rect(self.screen, button_color, self.next_button_rect, border_radius=5)
            self.screen.blit(self.next_button_text, self.next_button_text_rect)
            
            pygame.display.flip()
            self.clock.tick(30)
            
        video.release()
        return True

class Confetti:
    def __init__(self):
        self.particles = []
        self.colors = [
            (255, 0, 0),     # Red
            (0, 255, 0),     # Green
            (0, 0, 255),     # Blue
            (255, 255, 0),   # Yellow
            (255, 0, 255),   # Magenta
            (0, 255, 255),   # Cyan
            (255, 165, 0),   # Orange
            (255, 192, 203), # Pink
        ]
        
    def create_particle(self):
        x = random.randint(0, WIDTH)
        y = random.randint(-50, 0)
        size = random.randint(5, 10)
        color = random.choice(self.colors)
        speed_x = random.uniform(-2, 2)
        speed_y = random.uniform(2, 5)
        rotation = random.uniform(0, 360)
        rotation_speed = random.uniform(-5, 5)
        
        return {
            'x': x, 'y': y,
            'size': size,
            'color': color,
            'speed_x': speed_x,
            'speed_y': speed_y,
            'rotation': rotation,
            'rotation_speed': rotation_speed
        }
    
    def update(self):
        # Add new particles
        if len(self.particles) < 200:  # Limit total particles
            for _ in range(5):  # Add 5 particles per frame
                self.particles.append(self.create_particle())
        
        # Update existing particles
        for particle in self.particles[:]:
            particle['y'] += particle['speed_y']
            particle['x'] += particle['speed_x']
            particle['rotation'] += particle['rotation_speed']
            
            # Remove particles that are off screen
            if particle['y'] > HEIGHT:
                self.particles.remove(particle)
    
    def draw(self, surface):
        for particle in self.particles:
            # Create a surface for the rotated rectangle
            particle_surface = pygame.Surface((particle['size'], particle['size']), pygame.SRCALPHA)
            pygame.draw.rect(particle_surface, particle['color'], (0, 0, particle['size'], particle['size']))
            
            # Rotate the particle
            rotated_surface = pygame.transform.rotate(particle_surface, particle['rotation'])
            
            # Get the rect for positioning
            rect = rotated_surface.get_rect(center=(particle['x'], particle['y']))
            
            # Draw the rotated particle
            surface.blit(rotated_surface, rect)