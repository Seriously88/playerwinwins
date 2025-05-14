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
        
        # Try to load shuttlecock image
        try:
            self.image = pygame.image.load(SHUTTLE_IMAGE)
            self.image = pygame.transform.scale(self.image, (20, 20))
        except:
            pass

    def update(self):
        # Store previous position for trajectory analysis
        prev_x = self.x
        prev_y = self.y
        
        # Apply velocities
        self.x += self.vx
        self.y += self.vy
        self.vy += SHUTTLE_GRAVITY * self.gravity_multiplier
        
        # Gradually slow down the shuttlecock (air resistance)
        if abs(self.vx) > 0.1:
            self.vx *= 0.995
        if abs(self.vy) > 0.1:
            self.vy *= 0.995

        # Bounce off top
        if self.y - self.radius <= 0:
            self.vy *= -1
            self.y = self.radius  # Prevent sticking to ceiling

        # Check if out of bounds (outside of court sidelines)
        if self.x < COURT_LEFT or self.x > COURT_RIGHT:
            self.out_of_bounds = True
        
        # If shuttlecock is below the ground level, it's also out of bounds
        if self.y > HEIGHT:
            self.out_of_bounds = True
            
        # Check for net collision with enhanced trajectory prediction
        net_rect = pygame.Rect(NET_X - 2, 0, 4, COURT_GROUND_Y)
        
        # Direct collision with net
        if net_rect.collidepoint(self.x, self.y):
            self.out_of_bounds = True
            return
            
        # Check if shuttlecock crossed the net
        crossed_net = (prev_x < NET_X and self.x >= NET_X) or (prev_x >= NET_X and self.x < NET_X)
        
        if crossed_net:
            # Calculate y-position at the point of crossing
            # Using linear interpolation to find y at the net position
            if abs(self.x - prev_x) > 0.001:  # Avoid division by zero
                t = (NET_X - prev_x) / (self.x - prev_x)
                y_at_net = prev_y + t * (self.y - prev_y)
                
                # If y at net is below the top of the net, it's out of bounds
                if y_at_net >= COURT_GROUND_Y - 10:  # Net height adjustment
                    self.out_of_bounds = True
                    
                # If shuttlecock is moving too horizontally near the net
                # Give it a slight boost upward to help it over
                if abs(self.vy) < 1 and not self.out_of_bounds and y_at_net > COURT_GROUND_Y - 200:
                    self.vy -= 0.5  # Small upward boost

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

    def draw(self, surface):
        if self.image:
            # Calculate the rect for image placement
            img_rect = self.image.get_rect()
            img_rect.center = (int(self.x), int(self.y))
            
            # Rotate shuttlecock based on velocity (optional)
            angle = 0
            if abs(self.vx) > 0:
                # Calculate angle based on velocity
                angle = 30 * (self.vx / 10)  # Scale rotation by speed
                
                # Flip direction if moving left
                if self.vx < 0:
                    angle += 180
                
            rotated_img = pygame.transform.rotate(self.image, angle)
            rotated_rect = rotated_img.get_rect(center=img_rect.center)
            
            surface.blit(rotated_img, rotated_rect)
        else:
            pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), self.radius)