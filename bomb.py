import pygame
import random
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
        # Position
        self.x = x
        self.y = y
        self.radius = 20  # Collision radius
        
        # Movement
        self.fall_speed = random.uniform(2, 4)  # Faster than coins
        self.target_y = COURT_GROUND_Y - 30  # Where bomb disappears
        
        # Load the bomb image
        self.image = None
        self.load_image()
        
        # State
        self.hit_player = False
        self.should_remove = False
        
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
        # Update explosion if it exists
        if self.explosion:
            self.explosion.update()
            if not self.explosion.alive:
                self.should_remove = True
            return
            
        # Update bomb position if not exploded
        if not self.hit_player and not self.should_remove:
            # Move down
            self.y += self.fall_speed
            
            # Add slight swaying motion
            self.x += random.uniform(-0.5, 0.5)
            
            # Check if reached ground
            if self.y >= self.target_y:
                self.explode()
    
    def draw(self, surface):
        """Draw the bomb or its explosion animation"""
        if self.explosion:
            self.explosion.draw(surface)
        elif not self.should_remove and self.image:
            rect = self.image.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(self.image, rect)
    
    def collides_with_player(self, player_rect):
        """Check if the bomb collides with the player"""
        if self.hit_player or self.should_remove or self.explosion:
            return False
            
        # Circle-rectangle collision check
        closest_x = max(player_rect.left, min(self.x, player_rect.right))
        closest_y = max(player_rect.top, min(self.y, player_rect.bottom))
        
        distance_x = self.x - closest_x
        distance_y = self.y - closest_y
        
        return (distance_x * distance_x + distance_y * distance_y) < (self.radius * self.radius)
    
    def hit(self):
        """Mark bomb as hit by player and create explosion"""
        if not self.hit_player and not self.explosion:
            self.hit_player = True
            self.explode()
            return -5  # Penalty of 5 coins
        return 0
        
    def explode(self):
        """Create explosion animation at current position"""
        self.explosion = ExplosionAnimation(self.x, self.y) 