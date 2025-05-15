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
        # Reset horizontal velocity
        self.velocity_x = 0
        
        # Left/Right movement
        if keys[pygame.K_LEFT]:
            self.velocity_x = -SPRINT_SPEED if keys[pygame.K_LSHIFT] else -WALK_SPEED
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            self.velocity_x = SPRINT_SPEED if keys[pygame.K_LSHIFT] else WALK_SPEED
            self.facing_right = True

        # Jump (only when on ground)
        if keys[pygame.K_UP] and self.on_ground:
            self.velocity_y = JUMP_STRENGTH
            self.on_ground = False
        
        # Crouch
        if keys[pygame.K_DOWN] and self.on_ground:
                self.is_crouching = True
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
        
        if self.racket_rect.colliderect(shuttle_rect):
            # Calculate hit position relative to racket center (for angle)
            hit_position = (shuttle.x - self.racket_rect.centerx) / (self.racket_rect.width / 2)
            
            # Determine which side of the net the player is on
            is_player_left = self.rect.centerx < NET_X
            
            # Calculate minimum speed needed to cross the net based on distance
            distance_to_net = abs(NET_X - self.rect.centerx)
            min_speed = max(6, distance_to_net / 60)  # Ensure at least speed 6
            
            # Calculate new velocities based on swing type
            if self.swing_type == "normal":
                # Normal hit - good balance of speed and height
                speed = max(8 * self.swing_power, min_speed)
                shuttle.vx = speed * (1 if self.facing_right else -1)
                
                # Ensure enough height to clear the net
                min_height = max(-8, -distance_to_net / 30)
                shuttle.vy = min_height + random.uniform(-1, 1)
                
            elif self.swing_type == "smash":
                # Smash - fast and downward trajectory
                speed = max(12 * self.swing_power, min_speed * 1.5)
                shuttle.vx = speed * (1 if self.facing_right else -1)
                
                # Ensure enough initial upward velocity to clear the net
                net_distance_factor = distance_to_net / 300  # Higher value for closer distances
                shuttle.vy = -4 - net_distance_factor + random.uniform(-1, 1)
                
            elif self.swing_type == "drop":
                # Drop shot - short, high arc that falls quickly
                speed = max(4 * self.swing_power, min_speed * 0.8)  # Less speed but ensure it crosses
                shuttle.vx = speed * (1 if self.facing_right else -1)
                
                # Higher arc for drop shots to ensure it clears the net
                shuttle.vy = -10 - (distance_to_net / 60) + random.uniform(-1, 1)
                shuttle.gravity_multiplier = 1.5  # Falls faster
            
            # Add extra height if very close to the net to ensure it crosses
            if abs(NET_X - self.rect.centerx) < 100:
                shuttle.vy -= 2  # More upward velocity
            
            # End the swing
            self.is_swinging = False
            
            # Reset gravity multiplier for non-drop shots
            if self.swing_type != "drop":
                shuttle.gravity_multiplier = 1.0
                
            return True
            
        return False

    def update(self):
        # Apply gravity when not on ground
        if not self.on_ground:
            self.velocity_y += GRAVITY
        
        # Apply horizontal movement
        self.rect.x += self.velocity_x
        
        # Apply vertical movement with gravity
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
            self.velocity_y = 0
            
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
        
        # AI behavior settings
        self.difficulty = 0.7  # 0.0 to 1.0
        self.reaction_time = int(60 * (1.0 - self.difficulty))  # Frames to react
        self.accuracy = self.difficulty  # How accurately NPC aims shots
        
        # Tracking state
        self.is_tracking = False
        self.in_hit_position = False
        self.ready_to_hit = False
        self.hit_window_counter = 0
        self.position_strategy = "balanced"  # "offensive", "defensive", or "balanced"
        
        # Player tracking
        self.player_last_x = 0
        self.player_last_y = 0
        self.player_velocity_x = 0
        self.player_velocity_y = 0
        self.player_positions = []  # Store recent player positions
        self.max_player_positions = 10
        self.player_position_timer = 0
        self.strategy_timer = 180

    def track_shuttlecock(self, shuttle, player=None):
        """AI logic to track and respond to shuttlecock, considers player position when available"""
        # Reset tracking flag
        self.is_tracking = True
        
        # Reset hit preparation flags if shuttle is not moving toward NPC's side
        if not (shuttle.vx > 0 and shuttle.x > NET_X):
            self.in_hit_position = False
            self.ready_to_hit = False
            self.hit_window_counter = 0
        
        # If player object is provided, track their position and movement
        if player:
            # Calculate player velocity based on position change
            if self.player_last_x != 0:  # Not first frame
                self.player_velocity_x = player.rect.centerx - self.player_last_x
                self.player_velocity_y = player.rect.centery - self.player_last_y
            
            # Update last known position
            self.player_last_x = player.rect.centerx
            self.player_last_y = player.rect.centery
            
            # Record player position less frequently to reduce calculations
            self.player_position_timer += 1
            if self.player_position_timer >= 10:  # Reduced frequency (was 5)
                self.player_positions.append((player.rect.centerx, player.rect.centery))
                if len(self.player_positions) > self.max_player_positions:
                    self.player_positions.pop(0)  # Remove oldest position
                self.player_position_timer = 0
            
            # Update strategy less frequently
            self.strategy_timer -= 1
            if self.strategy_timer <= 0:
                # Simplified strategy update
                if player.rect.centerx < NET_X * 0.6:
                    self.position_strategy = "offensive"
                else:
                    self.position_strategy = "defensive"
                self.strategy_timer = 300  # Longer interval between updates (was 180)
        
        # Determine if shuttlecock is moving toward NPC
        if shuttle.vx > 0 and shuttle.x > NET_X:
            # Simplified prediction logic to reduce calculations
            # Basic target calculation - move toward shuttlecock
            target_x = shuttle.x + (shuttle.vx * 0.5)
            
            # Constrain to right half of court
            target_x = max(NET_X + 10, min(target_x, COURT_RIGHT - 50))
            
            # Determine if NPC should move horizontally
            if abs(self.rect.centerx - target_x) > 40:
                # Move toward target position
                if self.rect.centerx < target_x:
                    self.velocity_x = WALK_SPEED
                    self.facing_right = True
                else:
                    self.velocity_x = -WALK_SPEED
                    self.facing_right = False
                
                # Mark that we are not yet in position
                self.in_hit_position = False
            else:
                # We're in horizontal hitting position, slow down/stop
                self.velocity_x = 0
                self.in_hit_position = True
            
            # Simplified jumping logic
            # Jump if shuttle is high and we're on ground
            if shuttle.y < self.rect.top + 80 and self.on_ground and random.random() < 0.3:
                self.velocity_y = JUMP_STRENGTH
                self.on_ground = False
                
            # Check if we're in a good position to hit
            if self.in_hit_position:
                self.ready_to_hit = True
            
            # Simplified hit decision
            if self.is_in_hitting_range(shuttle):
                shot_type = "normal"
                if not self.on_ground:
                    shot_type = "smash"
                elif random.random() < 0.2:
                    shot_type = "drop"
                
                self.swing_racket(shot_type)
        else:
            # If shuttle is not coming toward us, simplified player tracking
            self.track_player_simple()
            self.is_tracking = False
    
    def track_player_simple(self):
        """Simplified player tracking to reduce lag"""
        # Default positions based on strategy
        if self.position_strategy == "offensive":
            target_x = NET_X + 150
        else:
            target_x = COURT_RIGHT - 150
        
        # Move toward target position
        if abs(self.rect.centerx - target_x) > 50:
            # Move toward target
            if self.rect.centerx < target_x:
                self.velocity_x = WALK_SPEED * 0.7
                self.facing_right = True
            else:
                self.velocity_x = -WALK_SPEED * 0.7
                self.facing_right = False
        else:
            # Stand still with occasional small movements
            if random.random() < 0.03:
                self.direction *= -1
                self.facing_right = (self.direction > 0)
            self.velocity_x = 0
        
        # Occasionally jump
        if random.random() < 0.003 and self.on_ground:
            self.velocity_y = JUMP_STRENGTH
            self.on_ground = False
    
    def is_in_hitting_range(self, shuttle):
        """Determine if the shuttlecock is in the ideal position to be hit"""
        # Horizontal distance check (more important with side-view movement)
        x_distance = abs(shuttle.x - (self.rect.centerx + (30 if self.facing_right else -30)))
        
        # Vertical position check relative to racket position
        racket_y = self.rect.centery - 20  # Approximate racket position
        y_distance = abs(shuttle.y - racket_y)
        
        # Height check - expanded to account for limited vertical movement
        height_good = shuttle.y > self.rect.top - 30 and shuttle.y < self.rect.bottom + 30
        
        # Check if we're in a good position to hit
        return x_distance < 50 and y_distance < 60 and height_good
    
    def update(self):
        # Decrement timers
        if self.decision_timer > 0:
            self.decision_timer -= 1
        
        # Default movement if not tracking shuttlecock
        if not self.is_tracking:
            # Reset hit flags when not tracking
            self.in_hit_position = False
            self.ready_to_hit = False
            self.hit_window_counter = 0
            
            # Move back and forth in right half of court based on strategy
            if self.position_strategy == "offensive":
                # Stay closer to the net
                target_x = NET_X + 150
            elif self.position_strategy == "defensive":
                # Stay back
                target_x = COURT_RIGHT - 150
            else:
                # Center position
                target_x = NET_X + (COURT_RIGHT - NET_X) / 2
            
            # Move toward the strategic position
            if abs(self.rect.centerx - target_x) > 50:
                if self.rect.centerx < target_x:
                    self.velocity_x = WALK_SPEED * 0.7
                    self.direction = 1
                    self.facing_right = True
                else:
                    self.velocity_x = -WALK_SPEED * 0.7
                    self.direction = -1
                    self.facing_right = False
            else:
                # Small side-to-side movement to look more natural
                self.rect.x += self.direction * 1
                if random.random() < 0.01:  # Occasionally change direction
                    self.direction *= -1
                    self.facing_right = (self.direction > 0)
            
            # Random jumps when idle
            if random.random() < 0.005 and self.on_ground:
                self.velocity_y = JUMP_STRENGTH
                self.on_ground = False
        
        # Let parent class handle standard movement physics
        super().update()
        
        # Ensure NPC stays on right side of net
        if self.rect.left < NET_X:
            self.rect.left = NET_X
            self.velocity_x = WALK_SPEED  # Move back to right side
            self.direction = 1  # Change direction if at net