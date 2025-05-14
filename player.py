import pygame
import random
from config import *

GRAVITY = 0.5
JUMP_STRENGTH = -10
SPRINT_SPEED = 8
WALK_SPEED = 4

class Player:
    def __init__(self, x, y, color):
        self.rect = pygame.Rect(x, y, 40, 80)
        self.color = color
        self.velocity_y = 0
        self.velocity_x = 0
        self.on_ground = True
        self.image = None
        self.facing_right = True
        
        # Player state
        self.is_crouching = False
        self.is_swinging = False
        self.swing_cooldown = 0
        self.swing_power = 0
        self.swing_type = None  # Can be "normal", "smash", or "drop"
        
        # Create racket hitbox (positioned relative to player)
        self.racket_rect = pygame.Rect(0, 0, 30, 20)
        self.update_racket_position()
        
        # Try to load player image
        try:
            self.image = pygame.image.load(PLAYER_IMAGE)
            self.image = pygame.transform.scale(self.image, (40, 80))
        except:
            pass

    def update_racket_position(self):
        """Update the racket position based on player position and facing direction"""
        if self.facing_right:
            self.racket_rect.midleft = (self.rect.right, self.rect.centery - 20)
        else:
            self.racket_rect.midright = (self.rect.left, self.rect.centery - 20)

    def handle_input(self, keys):
        # Reset velocities
        self.velocity_x = 0
        self.velocity_y = 0
        
        # Left/Right movement
        if keys[pygame.K_LEFT]:
            self.velocity_x = -SPRINT_SPEED if keys[pygame.K_LSHIFT] else -WALK_SPEED
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            self.velocity_x = SPRINT_SPEED if keys[pygame.K_LSHIFT] else WALK_SPEED
            self.facing_right = True

        # Up/Down movement
        if keys[pygame.K_UP]:
            self.velocity_y = -WALK_SPEED
            self.on_ground = False
        elif keys[pygame.K_DOWN]:
            if self.on_ground:
                self.is_crouching = True
            else:
                self.velocity_y = WALK_SPEED
        else:
            self.is_crouching = False
        
        # Adjust hitbox when crouching
        if self.is_crouching:
            if not hasattr(self, 'standing_height'):
                self.standing_height = self.rect.height
            self.rect.height = self.standing_height * 0.7
        else:
            # Restore normal hitbox
            if hasattr(self, 'standing_height'):
                self.rect.height = self.standing_height
        
        # Racket swings
        if self.swing_cooldown > 0:
            self.swing_cooldown -= 1
        elif not self.is_swinging:
            # Normal swing
            if keys[pygame.K_z]:
                self.swing_racket("normal")
            # Smash (while in air)
            elif keys[pygame.K_x] and not self.on_ground:
                self.swing_racket("smash")
            # Drop shot
            elif keys[pygame.K_c]:
                self.swing_racket("drop")

    def swing_racket(self, swing_type):
        """Perform a racket swing of the specified type"""
        if self.swing_cooldown <= 0:
            self.is_swinging = True
            self.swing_type = swing_type
            self.swing_cooldown = 30  # Half a second cooldown at 60 FPS
            
            # Set swing power based on type
            if swing_type == "normal":
                self.swing_power = 1.0
            elif swing_type == "smash":
                self.swing_power = 1.5
            elif swing_type == "drop":
                self.swing_power = 0.5
            
            # Expanding racket hitbox during swing for better hit detection
            if self.facing_right:
                self.racket_rect.width = 40
            else:
                self.racket_rect.width = 40

    def hit_shuttlecock(self, shuttle):
        """Handle shuttlecock hit with racket, return True if hit"""
        if not self.is_swinging:
            return False
            
        # Check if racket intersects with shuttlecock
        shuttle_rect = pygame.Rect(shuttle.x - shuttle.radius, shuttle.y - shuttle.radius, 
                                 shuttle.radius * 2, shuttle.radius * 2)
        
        # For NPC, give a slightly larger hitbox for better hit probability
        if isinstance(self, NPC):
            # Extend the racket hitbox slightly for NPC
            extended_racket = self.racket_rect.inflate(10, 10)
            hit = extended_racket.colliderect(shuttle_rect)
        else:
            hit = self.racket_rect.colliderect(shuttle_rect)
        
        if hit:
            # Calculate hit position relative to racket center (for angle)
            hit_position = (shuttle.x - self.racket_rect.centerx) / (self.racket_rect.width / 2)
            
            # Calculate new velocities based on swing type
            if self.swing_type == "normal":
                # Normal hit - good balance of speed and height
                speed = 8 * self.swing_power
                shuttle.vx = speed * (1 if self.facing_right else -1)
                shuttle.vy = -8 + random.uniform(-1, 1) 
                
            elif self.swing_type == "smash":
                # Smash - fast and downward trajectory
                speed = 12 * self.swing_power
                shuttle.vx = speed * (1 if self.facing_right else -1)
                shuttle.vy = -4 + random.uniform(-1, 1)
                
            elif self.swing_type == "drop":
                # Drop shot - short, high arc that falls quickly
                speed = 4 * self.swing_power
                shuttle.vx = speed * (1 if self.facing_right else -1)
                shuttle.vy = -10 + random.uniform(-1, 1)
                shuttle.gravity_multiplier = 1.5  # Falls faster
            
            # End the swing
            self.is_swinging = False
            
            # Reset gravity multiplier for non-drop shots
            if self.swing_type != "drop":
                shuttle.gravity_multiplier = 1.0
                
            return True
            
        return False

    def update(self):
        # Apply horizontal movement
        self.rect.x += self.velocity_x
        
        # Apply vertical movement (no gravity)
        self.rect.y += self.velocity_y

        # Keep player within screen bounds
        if self.rect.left < COURT_LEFT:
            self.rect.left = COURT_LEFT
        if self.rect.right > COURT_RIGHT:
            self.rect.right = COURT_RIGHT
            
        # Prevent player from crossing the net
        if self.rect.right > NET_X and self.rect.left < NET_X:
            # If player is mostly on the left side, push left
            if self.rect.centerx < NET_X:
                self.rect.right = NET_X
            # If player is mostly on the right side, push right
            else:
                self.rect.left = NET_X
                
        # Ground collision
        if self.rect.bottom >= COURT_GROUND_Y:
            self.rect.bottom = COURT_GROUND_Y
            self.on_ground = True
            
        # Ceiling collision
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity_y = 0
        
        # Update racket position
        self.update_racket_position()
        
        # Reset swing state after cooldown
        if self.swing_cooldown <= 0:
            self.is_swinging = False

    def draw(self, surface):
        # Draw player
        if self.image:
            # Flip image if facing left
            img = pygame.transform.flip(self.image, not self.facing_right, False)
            
            # Adjust image when crouching
            if self.is_crouching:
                img = pygame.transform.scale(img, (self.rect.width, self.rect.height))
                
            surface.blit(img, self.rect)
        else:
            pygame.draw.rect(surface, self.color, self.rect)
        
        # Draw racket (for debugging, could be replaced with racket sprite)
        racket_color = (220, 180, 50) if not self.is_swinging else (255, 100, 0)
        pygame.draw.rect(surface, racket_color, self.racket_rect)


class NPC(Player):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.direction = -1
        self.jump_timer = 0
        self.decision_timer = 0
        self.target_x = 0
        self.facing_right = False
        self.stuck_timer = 0  # Track if NPC is stuck
        self.last_position = (x, y)  # Track last position to detect being stuck
        
        # AI behavior settings
        self.base_difficulty = 0.75  # Increased base difficulty for better performance
        self.difficulty = self.base_difficulty  # Current difficulty
        self.reaction_time = int(60 * (1.0 - self.difficulty))  # Frames to react
        self.accuracy = self.difficulty  # How accurately NPC aims shots
        
        # Load NPC image
        try:
            self.image = pygame.image.load(NPC_IMAGE)
            self.image = pygame.transform.scale(self.image, (40, 80))
        except Exception as e:
            print(f"Error loading NPC image: {e}")

    def adjust_difficulty(self, player_lives):
        """Adjust NPC difficulty based on player's lives"""
        # Make NPC slightly easier when player has fewer lives, but keep it challenging
        if player_lives == 1:
            self.difficulty = self.base_difficulty - 0.1  # Slightly easier when on last life
        elif player_lives == 2:
            self.difficulty = self.base_difficulty - 0.05  # Very slightly easier
        else:
            self.difficulty = self.base_difficulty  # Normal difficulty
            
        # Update dependent attributes
        self.reaction_time = int(60 * (1.0 - self.difficulty))
        self.accuracy = self.difficulty

    def track_shuttlecock(self, shuttle):
        """AI logic to track and respond to shuttlecock"""
        # Reset vertical velocity
        self.velocity_y = 0
        
        # Detect if shuttlecock is heading toward NPC side
        # Added support for tracking shuttlecock moving in both directions
        shuttle_in_npc_court = shuttle.x > NET_X
        shuttle_heading_to_npc = shuttle.vx < 0
        
        # Enhanced tracking logic to track shuttlecock better on NPC side
        if (shuttle_heading_to_npc and shuttle_in_npc_court) or (shuttle_in_npc_court and abs(shuttle.x - self.rect.centerx) < 200):
            # Decide if NPC will try to catch the shuttlecock or deliberately miss
            # Increase the chance of attempting to catch significantly
            will_attempt_catch = random.random() < (self.difficulty + 0.25)  # Higher base chance to attempt catch
            
            # If NPC decides not to attempt catch, move away from the predicted landing spot
            if not will_attempt_catch:
                # Create a movement away from the shuttlecock
                dodge_x = shuttle.x + random.uniform(-150, -50) if shuttle.x < self.rect.centerx else shuttle.x + random.uniform(50, 150)
                # Stay within court bounds
                dodge_x = max(NET_X + 50, min(dodge_x, COURT_RIGHT - 50))
                
                # Set dodge position as target
                self.target_x = dodge_x
                
                # Move toward dodge position
                if abs(self.rect.centerx - self.target_x) > 20:
                    if self.rect.centerx < self.target_x:
                        self.velocity_x = WALK_SPEED * 0.7  # Move slower when dodging
                        self.facing_right = True
                    else:
                        self.velocity_x = -WALK_SPEED * 0.7
                        self.facing_right = False
                else:
                    self.velocity_x = 0
                    
                # Random vertical movement when dodging
                if random.random() < 0.3:
                    self.velocity_y = random.choice([-WALK_SPEED, WALK_SPEED]) * 0.6
                
                return  # Skip the rest of the tracking logic
            
            # Normal tracking behavior when attempting to catch
            # Improved prediction algorithm
            # Calculate time to intercept based on current shuttle position and velocity
            shuttle_speed = abs(shuttle.vx)
            time_to_intercept = min(40, max(5, abs(shuttle.x - self.rect.centerx) / (shuttle_speed + 0.1)))
            
            # Predict shuttle position at intercept time
            predicted_x = shuttle.x + (shuttle.vx * time_to_intercept)
            predicted_y = shuttle.y + (shuttle.vy * time_to_intercept) + (0.5 * SHUTTLE_GRAVITY * time_to_intercept * time_to_intercept)
            
            # Add smaller randomness/error based on difficulty to improve accuracy
            error_margin = (1.0 - self.accuracy) * 60  # Reduced error margin
            predicted_x += random.uniform(-error_margin, error_margin)
            
            # Constrain prediction to right side of court
            predicted_x = max(NET_X + 30, min(predicted_x, COURT_RIGHT - 30))
            predicted_y = max(50, min(predicted_y, COURT_GROUND_Y - 30))
            
            # Set target position
            self.target_x = predicted_x
            
            # Adjust movement speed based on urgency - increase speed for better response
            # Make NPC move faster for fast shuttlecocks
            urgency = max(0.8, min(1.8, shuttle_speed / 6))
            
            # Move toward target horizontally
            if abs(self.rect.centerx - self.target_x) > 15:
                if self.rect.centerx < self.target_x:
                    self.velocity_x = WALK_SPEED * urgency
                    self.facing_right = True
                else:
                    self.velocity_x = -WALK_SPEED * urgency
                    self.facing_right = False
            else:
                self.velocity_x = 0
            
            # Vertical movement based on predicted shuttlecock height
            target_y = predicted_y - 30  # Aim to hit with racket
            
            # Move toward target vertically with urgency
            if abs(self.rect.centery - target_y) > 15:
                if self.rect.centery > target_y:
                    self.velocity_y = -WALK_SPEED * urgency
                else:
                    self.velocity_y = WALK_SPEED * urgency
            
            # Decide what type of shot to use based on shuttlecock position
            if self.decision_timer <= 0:
                # Calculate distance to shuttle
                distance = abs(shuttle.x - self.rect.centerx)
                vertical_dist = abs(shuttle.y - self.rect.centery)
                
                # Try to hit the shuttlecock if it's close enough
                # Increased detection range for more reliable hits
                if distance < 100 and vertical_dist < 80:
                    # Increase chance to swing even when in position
                    if random.random() < (self.difficulty + 0.4):  # Much higher chance to swing
                        # Choose shot type based on situation
                        if not self.on_ground and shuttle.y < self.rect.centery:
                            # Smash if jumping and shuttlecock is high
                            self.swing_racket("smash")
                        elif shuttle.y > self.rect.centery and random.random() < 0.3:
                            # Occasionally use drop shot
                            self.swing_racket("drop")
                        else:
                            # Normal shot
                            self.swing_racket("normal")
                    
                    self.decision_timer = self.reaction_time
    
    def update(self):
        # Decrement timers
        if self.decision_timer > 0:
            self.decision_timer -= 1
        
        # Check if NPC is stuck in the same position
        current_pos = (self.rect.x, self.rect.y)
        if (abs(current_pos[0] - self.last_position[0]) < 2 and
            abs(current_pos[1] - self.last_position[1]) < 2):
            self.stuck_timer += 1
        else:
            self.stuck_timer = 0
        
        # If stuck for too long, reset position to center of court
        if self.stuck_timer > 120:  # If stuck for 2 seconds (60fps * 2)
            self.unstick()
            self.stuck_timer = 0
        
        # Update last position
        self.last_position = current_pos
        
        # Prevent NPC from getting stuck at edges
        if self.rect.right >= COURT_RIGHT - 5:
            self.velocity_x = -WALK_SPEED
            self.direction = -1
        elif self.rect.left <= NET_X + 5:
            self.velocity_x = WALK_SPEED
            self.direction = 1
        
        # Default movement if not tracking shuttlecock
        if self.velocity_x == 0:
            # Move back and forth in right half of court
            # Stay more centrally positioned
            target_x = NET_X + (COURT_RIGHT - NET_X) * 0.5  # Target center of right court
            if abs(self.rect.centerx - target_x) > 50:
                if self.rect.centerx < target_x:
                    self.velocity_x = WALK_SPEED * 0.7
                    self.direction = 1
                else:
                    self.velocity_x = -WALK_SPEED * 0.7
                    self.direction = -1
            else:
                # Small random movement when in center position
                self.rect.x += self.direction * 1.5
                if random.random() < 0.01:  # Occasionally change direction
                    self.direction *= -1
            
            # Random vertical movement - more controlled
            self.jump_timer += 1
            if self.jump_timer > 120:
                # Target middle height of court
                target_y = COURT_GROUND_Y * 0.6
                if abs(self.rect.centery - target_y) > 50:
                    if self.rect.centery > target_y:
                        self.velocity_y = -WALK_SPEED * 0.4
                    else:
                        self.velocity_y = WALK_SPEED * 0.4
                else:
                    self.velocity_y = random.choice([-WALK_SPEED, WALK_SPEED]) * 0.3
                self.jump_timer = 0
        
        # Let parent class handle standard movement physics
        super().update()
        
        # Ensure NPC stays on right side of net
        if self.rect.left < NET_X:
            self.rect.left = NET_X
            self.velocity_x = WALK_SPEED  # Move back to right side
            self.direction = 1  # Change direction if at net
    
    def unstick(self):
        """Reset NPC position if stuck"""
        # Move to center-right of court
        self.rect.x = NET_X + (COURT_RIGHT - NET_X) * 0.5
        self.rect.y = COURT_GROUND_Y - 100
        self.velocity_x = 0
        self.velocity_y = 0
        self.direction = random.choice([-1, 1])