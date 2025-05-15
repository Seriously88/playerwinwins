import pygame
import random
from config import *

class Shuttlecock:
    def __init__(self, x, y):
        self.radius = 10
        self.x = x
        self.y = y
        self.vx = random.choice([-5, 5])
        self.vy = -5
        self.image = None
        self.out_of_bounds = False
        self.gravity_multiplier = 1.0  # Added for drop shots
        self.prev_x = x
        self.prev_y = y
        
        # Try to load shuttlecock image
        try:
            self.image = pygame.image.load(SHUTTLE_IMAGE)
            self.image = pygame.transform.scale(self.image, (20, 20))
            # Pre-rotate images for common angles to avoid recalculating on every frame
            self.rotated_images = {}
        except:
            pass

    def update(self):
        # Store previous position for trajectory analysis
        self.prev_x = self.x
        self.prev_y = self.y
        
        # Apply velocities
        self.x += self.vx
        self.y += self.vy
        self.vy += SHUTTLE_GRAVITY * self.gravity_multiplier
        
        # Gradually slow down the shuttlecock (air resistance) - simplified
        if abs(self.vx) > 0.1:
            self.vx *= 0.995
        
        # Quick bounds checks
        # Bounce off top
        if self.y - self.radius <= 0:
            self.vy *= -1
            self.y = self.radius  # Prevent sticking to ceiling

        # Check if out of bounds (outside of court sidelines)
        if self.x < COURT_LEFT or self.x > COURT_RIGHT or self.y > HEIGHT:
            self.out_of_bounds = True
            return
            
        # Simplified net collision check
        if abs(self.x - NET_X) < 10:  # Near the net
            # Check if crossing the net
            crossed_net = (self.prev_x < NET_X and self.x >= NET_X) or (self.prev_x >= NET_X and self.x < NET_X)
            
            if crossed_net:
                # Calculate y-position at the point of crossing using simpler estimate
                # If y at net is below the top of the net, it's out of bounds
                if self.y >= COURT_GROUND_Y - 10:  # Net height adjustment
                    self.out_of_bounds = True

    def check_collision(self, player_rect):
        """Legacy collision method - replaced by player's hit_shuttlecock method"""
        pass

    def is_grounded(self):
        return self.y + self.radius >= COURT_GROUND_Y

    def reset(self, direction=1):
        """Reset the shuttlecock to a neutral starting position"""
        self.x = WIDTH // 2
        self.y = 200
        self.vx = 0  # Reset velocity to zero initially
        self.vy = 0  # Reset velocity to zero initially
        self.out_of_bounds = False
        self.gravity_multiplier = 1.0  # Reset gravity multiplier
        self.prev_x = self.x
        self.prev_y = self.y

    def draw(self, surface):
        if self.image:
            # Calculate the rect for image placement
            img_rect = self.image.get_rect()
            img_rect.center = (int(self.x), int(self.y))
            
            # Simplified rotation based on velocity - fewer angle calculations
            if abs(self.vx) > 0.5:
                # Round angle to nearest 15 degrees to use cached rotations
                angle = 0
                if abs(self.vx) > 0:
                    angle = int(30 * (self.vx / 10) / 15) * 15  # Round to nearest 15 degrees
                    
                # Flip direction if moving left
                if self.vx < 0:
                    angle += 180
                
                # Use cached rotated image if available
                if angle not in self.rotated_images:
                    self.rotated_images[angle] = pygame.transform.rotate(self.image, angle)
                    
                rotated_img = self.rotated_images[angle]
                rotated_rect = rotated_img.get_rect(center=img_rect.center)
                
                surface.blit(rotated_img, rotated_rect)
            else:
                # No rotation needed for slow-moving shuttlecock
                surface.blit(self.image, img_rect)
        else:
            pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), self.radius)