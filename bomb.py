import pygame
import random
import math
from config import *

class ExplosionAnimation:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frame = 0
        self.alive = True
        
        # TIMING SETTINGS
        self.animation_speed = 6    # Increased from 3 to 6 for slower animation
                                   # Updates every 6 frames instead of 3
        self.frame_counter = 0
        
        # Load explosion sprite sheet
        try:
            self.sprite_sheet = pygame.image.load("assests/explorationeffect.png").convert_alpha()
            
            # FRAME SETTINGS
            self.total_frames = 5   # Total number of frames in the sprite sheet
            # For vertical frames, divide height by total frames instead of width
            self.frame_width = self.sprite_sheet.get_width()
            self.frame_height = self.sprite_sheet.get_height() // self.total_frames
            
            # SIZE SETTINGS
            self.scale_factor = 0.5  # Changed from 1.0 to 0.5 to make it 50% smaller
            self.frame_width_scaled = int(self.frame_width * self.scale_factor)
            self.frame_height_scaled = int(self.frame_height * self.scale_factor)
            
        except Exception as e:
            print(f"Error loading explosion sprite: {e}")
            self.sprite_sheet = None
            
    def update(self):
        if not self.alive:
            return
            
        self.frame_counter += 1
        if self.frame_counter >= self.animation_speed:
            self.frame += 1
            self.frame_counter = 0
            
            # End animation after last frame
            if self.frame >= self.total_frames:
                self.alive = False
    
    def draw(self, surface):
        if not self.alive or not self.sprite_sheet:
            return
            
        # Calculate the source rectangle for current frame
        # Changed to get vertical frames instead of horizontal
        src_rect = pygame.Rect(
            0,                              # X position in sprite sheet (always 0 for vertical)
            self.frame * self.frame_height, # Y position changes for each frame
            self.frame_width,               # Width of one frame
            self.frame_height               # Height of one frame
        )
        
        # Create a surface for the current frame and scale it
        frame_surface = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
        frame_surface.blit(self.sprite_sheet, (0, 0), src_rect)
        
        # Scale the frame
        scaled_frame = pygame.transform.scale(frame_surface, 
                                           (self.frame_width_scaled, self.frame_height_scaled))
        
        # POSITION/CENTERING
        # Center the explosion on the bomb's position
        dest_x = self.x - self.frame_width_scaled // 2
        dest_y = self.y - self.frame_height_scaled // 2
        
        # Draw the frame
        surface.blit(scaled_frame, (dest_x, dest_y))

class Bomb:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 15
        self.vy = 0  # Vertical velocity
        self.gravity = 0.5
        self.should_remove = False
        self.explosion_timer = 0
        self.explosion_duration = 30  # Duration in frames
        self.is_exploding = False
        
        # Load explosion sound
        try:
            self.explosion_sound = pygame.mixer.Sound('assests/Explosion Sound.wav')
            self.explosion_sound.set_volume(0.7)  # Set volume to 70%
        except Exception as e:
            print(f"Error loading explosion sound: {e}")
            self.explosion_sound = None
        
        # Load the bomb image
        self.image = None
        self.load_image()
        
        # State
        self.hit_player = False
        
        # Explosion animation
        self.explosion = None
        
    def load_image(self):
        """Load the bomb sprite"""
        try:
            # Load the bomb image
            self.image = pygame.image.load("assests/Boombe.png").convert_alpha()
            
            # Scale the image
            self.image = pygame.transform.scale(self.image, (40, 40))
            
        except Exception as e:
            print(f"Error loading bomb sprite: {e}")
            # Create a fallback circle if image loading fails
            self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (50, 50, 50), (20, 20), 20)  # Dark gray
    
    def update(self):
        """Update bomb position and explosion animation"""
        if not self.is_exploding:
            # Apply gravity
            self.vy += self.gravity
            self.y += self.vy
            
            # Check if bomb hits the ground
            if self.y >= COURT_GROUND_Y - self.radius:
                self.explode()
        else:
            # Update explosion animation
            self.explosion_timer += 1
            if self.explosion_timer >= self.explosion_duration:
                self.should_remove = True
    
    def draw(self, surface):
        """Draw the bomb or its explosion animation"""
        if self.is_exploding:
            self.explosion.draw(surface)
        elif not self.should_remove and self.image:
            rect = self.image.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(self.image, rect)
    
    def collides_with_player(self, player_rect):
        """Check if the bomb collides with the player"""
        if self.is_exploding:
            return False
            
        # Calculate distance between bomb center and player center
        bomb_center = (self.x, self.y)
        player_center = (player_rect.centerx, player_rect.centery)
        
        distance = math.sqrt(
            (bomb_center[0] - player_center[0])**2 +
            (bomb_center[1] - player_center[1])**2
        )
        
        # Collision occurs if distance is less than sum of bomb radius and player "radius"
        player_radius = (player_rect.width + player_rect.height) / 4  # Approximate player as circle
        return distance < (self.radius + player_radius)
    
    def hit(self):
        """Mark bomb as hit by player and create explosion"""
        if not self.is_exploding:
            self.explode()
            return -5  # Penalty of 5 coins
        return 0
        
    def explode(self):
        """Start the explosion animation and play sound"""
        if not self.is_exploding:
            self.is_exploding = True
            # Play explosion sound
            if self.explosion_sound:
                pygame.mixer.Channel(4).play(self.explosion_sound)
            self.explosion = ExplosionAnimation(self.x, self.y) 