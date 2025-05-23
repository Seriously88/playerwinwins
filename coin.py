import pygame
import random
import math
from config import *

class CoinBurst:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.particles = []
        self.alive = True
        self.lifetime = 60  # Animation frames
        self.current_frame = 0
        
        # Create particles
        for _ in range(10):  # 8 particles in the burst
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 5)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'alpha': 255,  # Start fully opaque
                'size': random.uniform(5, 10)  # Random particle sizes
            })
    
    def update(self):
        if not self.alive:
            return
        
        self.current_frame += 1
        if self.current_frame >= self.lifetime:
            self.alive = False
            return
            
        # Update each particle
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            # Fade out
            particle['alpha'] = max(0, 255 * (1 - self.current_frame / self.lifetime))
    
    def draw(self, surface):
        if not self.alive:
            return
            
        for particle in self.particles:
            # Create a surface for the particle with alpha channel
            particle_surface = pygame.Surface((particle['size'], particle['size']), pygame.SRCALPHA)
            # Gold color with current alpha
            color = (255, 215, 0, int(particle['alpha']))
            pygame.draw.circle(particle_surface, color, 
                             (particle['size']/2, particle['size']/2), 
                             particle['size']/2)
            surface.blit(particle_surface, 
                        (particle['x'] - particle['size']/2, 
                         particle['y'] - particle['size']/2))

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
        self.should_remove = False
        
        # Burst animation
        self.burst = None
        
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
        if not self.collected and not self.should_remove:
            # Only move down if not at the target position
            if self.y < self.target_y:
                self.y += self.fall_speed
                
                # Add slight side-to-side movement for a floating effect
                self.x += random.uniform(-0.3, 0.3)
            else:
                # Mark the coin for removal when it hits the ground
                self.should_remove = True
                
        # Update burst animation if it exists
        if self.burst:
            self.burst.update()
            if not self.burst.alive:
                self.should_remove = True
    
    def collect(self):
        """Mark coin as collected and create burst effect"""
        if not self.collected:
            self.collected = True
            self.burst = CoinBurst(self.x, self.y)
            return 1  # Return coin value
        return 0
    
    def draw(self, surface):
        """Draw the coin if not collected, or the burst animation if collecting"""
        if not self.collected and not self.should_remove and self.image:
            # Calculate position (centered on the coin's position)
            rect = self.image.get_rect(center=(int(self.x), int(self.y)))
            
            # Draw the coin
            surface.blit(self.image, rect)
        
        # Draw burst animation if it exists
        if self.burst and self.burst.alive:
            self.burst.draw(surface)
    
    def collides_with_player(self, player_rect):
        """Check if the coin collides with the player"""
        if self.collected or self.should_remove:
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