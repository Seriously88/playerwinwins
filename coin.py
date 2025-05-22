import pygame
import random
import math
from config import *

class Coin:
    def __init__(self, x, y):
        # Position
        self.x = x
        self.y = y
        self.radius = 15  # Collision radius
        
        # Floating properties
        self.fall_speed = random.uniform(0.5, 1.5)  # Random fall speed for varied effect
        self.target_y = COURT_GROUND_Y - 50  # Final y position where coin stops falling
        
        # Load the coin image
        self.image = None
        self.load_image()
        
        # State
        self.collected = False
        
    def load_image(self):
        """Load the coin sprite"""
        try:
            # Load the coin image
            self.image = pygame.image.load("assests/collectcoins.png").convert_alpha()
            
            # Scale if needed (adjust size as desired)
            self.image = pygame.transform.scale(self.image, (30, 30))
                
            print("Loaded coin image")
        except Exception as e:
            print(f"Error loading coin sprite: {e}")
            # Create a fallback yellow circle if image loading fails
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 215, 0), (15, 15), 15)  # Gold color
    
    def update(self):
        """Update coin position for floating down effect"""
        if not self.collected:
            # Only move down if not at the target position
            if self.y < self.target_y:
                self.y += self.fall_speed
                
                # Add slight side-to-side movement for a floating effect
                self.x += random.uniform(-0.3, 0.3)
            else:
                # Slightly hover when reached target position
                self.y += math.sin(pygame.time.get_ticks() * 0.003) * 0.2
    
    def collect(self):
        """Mark coin as collected"""
        self.collected = True
        return 1  # Return coin value
    
    def draw(self, surface):
        """Draw the coin if not collected"""
        if not self.collected and self.image:
            # Calculate position (centered on the coin's position)
            rect = self.image.get_rect(center=(int(self.x), int(self.y)))
            
            # Draw the coin
            surface.blit(self.image, rect)
    
    def collides_with_player(self, player_rect):
        """Check if the coin collides with the player"""
        if self.collected:
            return False
            
        # Simple circle-rectangle collision
        # Find the closest point on the rectangle to the circle
        closest_x = max(player_rect.left, min(self.x, player_rect.right))
        closest_y = max(player_rect.top, min(self.y, player_rect.bottom))
        
        # Calculate the distance between the circle's center and the closest point
        distance_x = self.x - closest_x
        distance_y = self.y - closest_y
        
        # If the distance is less than the circle's radius, there is a collision
        return (distance_x * distance_x + distance_y * distance_y) < (self.radius * self.radius) 