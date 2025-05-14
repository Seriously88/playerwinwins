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
        
        # AI behavior settings
        self.difficulty = 0.7  # 0.0 to 1.0
        self.reaction_time = int(60 * (1.0 - self.difficulty))  # Frames to react
        self.accuracy = self.difficulty  # How accurately NPC aims shots
        
        # Tracking state
        self.is_tracking = False
        self.shuttlecock_last_x = 0
        self.shuttlecock_last_y = 0
        self.player_last_x = 0
        self.player_last_y = 0
        self.player_velocity_x = 0
        self.player_velocity_y = 0
        
        # Player tracking history (to detect patterns)
        self.player_positions = []
        self.player_position_timer = 0
        self.max_player_positions = 30  # Store the last 30 positions (half a second at 60 FPS)
        
        # Strategy variables
        self.aim_for_corners = True  # Try to aim shots away from player
        self.position_strategy = "center"  # "center", "defensive", "offensive"
        self.strategy_timer = 0
        
        # Realistic hit variables
        self.in_hit_position = False
        self.hit_window = 20  # Frames in which NPC can hit the shuttlecock
        self.hit_window_counter = 0
        self.ready_to_hit = False
        
        # Load NPC image
        try:
            self.image = pygame.image.load(NPC_IMAGE)
            self.image = pygame.transform.scale(self.image, (40, 80))
        except Exception as e:
            print(f"Error loading NPC image: {e}")

    def track_shuttlecock(self, shuttle, player=None):
        """AI logic to track and respond to shuttlecock, considers player position when available"""
        # Reset vertical velocity
        self.velocity_y = 0
        
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
            
            # Record player position every few frames
            self.player_position_timer += 1
            if self.player_position_timer >= 5:  # Record every 5 frames
                self.player_positions.append((player.rect.centerx, player.rect.centery))
                if len(self.player_positions) > self.max_player_positions:
                    self.player_positions.pop(0)  # Remove oldest position
                self.player_position_timer = 0
            
            # Update strategy periodically
            self.strategy_timer -= 1
            if self.strategy_timer <= 0:
                self.update_strategy(player, shuttle)
                self.strategy_timer = 180  # Update strategy every 3 seconds
        
        # Check if shuttlecock is moving toward NPC's side of the court
        if shuttle.vx > 0 and shuttle.x > NET_X:
            self.is_tracking = True
            
            # Track shuttlecock's last position for trajectory prediction
            if abs(shuttle.x - self.shuttlecock_last_x) > 0:
                self.shuttlecock_last_x = shuttle.x
                self.shuttlecock_last_y = shuttle.y
            
            # Basic prediction of where shuttlecock will land
            time_to_ground = (COURT_GROUND_Y - shuttle.y) / (shuttle.vy + 0.001)  # Avoid division by zero
            predicted_x = shuttle.x + (shuttle.vx * time_to_ground)
            
            # Add some randomness/error based on difficulty
            error_margin = (1.0 - self.accuracy) * 100
            predicted_x += random.uniform(-error_margin, error_margin)
            
            # Constrain prediction to right side of court
            predicted_x = max(NET_X + 50, min(predicted_x, COURT_RIGHT - 50))
            
            # Set target position (modified by strategy)
            self.target_x = predicted_x
            self.adjust_target_for_strategy(shuttle)
            
            # Move toward target horizontally with faster speed if further away
            distance_to_target = abs(self.rect.centerx - self.target_x)
            if distance_to_target > 20:
                speed_multiplier = min(1.5, distance_to_target / 100)  # Faster if further away
                movement_speed = WALK_SPEED * speed_multiplier
                
                if self.rect.centerx < self.target_x:
                    self.velocity_x = movement_speed
                    self.facing_right = True
                else:
                    self.velocity_x = -movement_speed
                    self.facing_right = False
            else:
                self.velocity_x = 0
                # We're in position horizontally
                self.in_hit_position = True
            
            # Vertical movement based on shuttlecock height and predicted landing
            if shuttle.vy > 0:  # Shuttlecock is falling
                # Calculate ideal height to hit the shuttlecock
                ideal_hit_height = shuttle.y - 30  # Slightly above the shuttlecock
                
                # Move toward ideal height
                if abs(self.rect.top - ideal_hit_height) > 15:
                    if self.rect.top > ideal_hit_height:
                        self.velocity_y = -WALK_SPEED
                    else:
                        self.velocity_y = WALK_SPEED
                else:
                    self.velocity_y = 0
                    
                    # Check if we're in position both horizontally and vertically
                    if self.in_hit_position and abs(shuttle.x - self.rect.centerx) < 40:
                        self.ready_to_hit = True
                        
                    # If ready to hit, start counting down hit window
                    if self.ready_to_hit:
                        self.hit_window_counter += 1
                        
                        # Only attempt hit within the hit window
                        if self.hit_window_counter >= 5 and self.hit_window_counter <= self.hit_window:
                            # Check if in ideal hitting position
                            if self.is_in_hitting_range(shuttle):
                                # Choose shot type based on situation and player position
                                shot_type = self.choose_shot_type(shuttle)
                                self.swing_racket(shot_type)
                                self.decision_timer = self.reaction_time
                                # Don't stop tracking after hitting - continue to follow the game
                                self.ready_to_hit = False
                                self.hit_window_counter = 0
                                
                        # If we missed the hit window, reset
                        if self.hit_window_counter > self.hit_window:
                            self.ready_to_hit = False
                            self.hit_window_counter = 0
            else:  # Shuttlecock is rising
                # For rising shuttlecocks, just try to get into position
                target_y = min(shuttle.y - 30, COURT_GROUND_Y - 80)  # Don't go below ground level
                
                if abs(self.rect.centery - target_y) > 20:
                    vertical_speed = WALK_SPEED * 1.2
                    if self.rect.centery > target_y:
                        self.velocity_y = -vertical_speed
                    else:
                        self.velocity_y = vertical_speed
        else:
            # Not actively tracking shuttlecock - track player instead
            self.track_player()
    
    def track_player(self):
        """When not tracking shuttlecock, track and respond to player movement"""
        if self.player_last_x == 0:
            # No player data yet, stay in default position
            self.is_tracking = False
            self.velocity_x = 0
            return
            
        # Basic mirror positioning - stay opposite to player
        player_side_position = self.player_last_x / NET_X  # 0 to 1 position on player's side
        
        # Mirror the player position to the NPC side, with adjustments
        # If player is at 0.2 (left side of their court), NPC should be at 0.8 (right side of their court)
        mirror_position = 1.0 - player_side_position  # Mirror position
        
        # Convert to actual x coordinate on NPC's side
        target_x = NET_X + (mirror_position * (COURT_RIGHT - NET_X))
        
        # Add offset based on player's vertical position
        if self.player_last_y < COURT_GROUND_Y - 200:
            # Player is high up, prepare for potential smash by moving back
            target_x = max(target_x, NET_X + (COURT_RIGHT - NET_X) * 0.7)
        
        # Adjust based on player velocity - anticipate movement
        target_x += self.player_velocity_x * 2  # Predict where player will be
        
        # Ensure target is within NPC's court
        target_x = max(NET_X + 50, min(target_x, COURT_RIGHT - 50))
        
        # Move toward mirrored position
        distance_to_target = abs(self.rect.centerx - target_x)
        if distance_to_target > 30:
            # Move faster based on distance and player velocity
            speed_factor = min(1.0, distance_to_target / 200 + abs(self.player_velocity_x) / 10)
            movement_speed = WALK_SPEED * speed_factor
            
            if self.rect.centerx < target_x:
                self.velocity_x = movement_speed
                self.facing_right = True
            else:
                self.velocity_x = -movement_speed
                self.facing_right = False
        else:
            # Small side-to-side movement to look more natural
            self.velocity_x = self.direction * 1
            if random.random() < 0.01:  # Occasionally change direction
                self.direction *= -1
                self.facing_right = (self.direction > 0)
        
        # Vertical positioning - try to match player's height with offset
        target_y = self.player_last_y
        
        # If player is jumping or crouching, adjust accordingly
        if abs(self.player_velocity_y) > 2:
            # Player is moving vertically - follow their movement
            target_y += self.player_velocity_y
        
        # Constrain vertical position
        target_y = max(100, min(target_y, COURT_GROUND_Y - 80))
        
        # Move toward target height
        if abs(self.rect.centery - target_y) > 40:
            if self.rect.centery > target_y:
                self.velocity_y = -WALK_SPEED * 0.75
            else:
                self.velocity_y = WALK_SPEED * 0.75
    
    def is_in_hitting_range(self, shuttle):
        """Determine if the shuttlecock is in the ideal position to be hit"""
        # Horizontal distance check
        x_distance = abs(shuttle.x - (self.rect.centerx + (30 if self.facing_right else -30)))
        
        # Vertical position check - make sure the shuttlecock is at racket height
        racket_y = self.rect.centery - 20  # Approximate racket position
        y_distance = abs(shuttle.y - racket_y)
        
        # Height check - don't hit if too high or too low
        height_good = shuttle.y > self.rect.top and shuttle.y < self.rect.bottom
        
        # Check if we're in a good position to hit
        return x_distance < 40 and y_distance < 30 and height_good
    
    def update_strategy(self, player, shuttle):
        """Update the NPC's strategy based on game state and player patterns"""
        player_x = player.rect.centerx
        
        # Analyze player position patterns
        if len(self.player_positions) > 10:
            # Check if player tends to stay in certain areas
            left_count = sum(1 for x, _ in self.player_positions if x < NET_X * 0.3)
            center_count = sum(1 for x, _ in self.player_positions if NET_X * 0.3 <= x <= NET_X * 0.7)
            right_count = sum(1 for x, _ in self.player_positions if x > NET_X * 0.7)
            
            total = len(self.player_positions)
            left_percent = left_count / total
            center_percent = center_count / total
            right_percent = right_count / total
            
            # If player spends a lot of time in one area, target the opposite
            if left_percent > 0.6:
                self.position_strategy = "offensive"  # Player stays left, move close to net
            elif right_percent > 0.6:
                self.position_strategy = "defensive"  # Player stays right, move back
            else:
                # More dynamic positioning based on current position
                if player_x < NET_X * 0.6:  # Player is deep in their court
                    self.position_strategy = "offensive"  # Move closer to the net
                elif player_x > NET_X * 0.9:  # Player is near the net
                    self.position_strategy = "defensive"  # Move back to defend
                else:
                    self.position_strategy = "center"  # Stay in the center
        else:
            # Not enough position data yet, use current position
            if player_x < NET_X * 0.6:  # Player is deep in their court
                self.position_strategy = "offensive"  # Move closer to the net
            elif player_x > NET_X * 0.9:  # Player is near the net
                self.position_strategy = "defensive"  # Move back to defend
            else:
                self.position_strategy = "center"  # Stay in the center
        
        # Randomly decide whether to aim for corners
        self.aim_for_corners = random.random() < 0.7  # 70% chance to aim for corners
        
        # Adjust hit window based on difficulty
        self.hit_window = int(15 + 15 * (1 - self.difficulty))  # Harder difficulty = smaller hit window
    
    def adjust_target_for_strategy(self, shuttle):
        """Adjust target position based on current strategy"""
        if self.position_strategy == "offensive":
            # Move closer to the net when being offensive
            self.target_x = min(self.target_x, NET_X + 150)
        elif self.position_strategy == "defensive":
            # Stay farther back when being defensive
            self.target_x = max(self.target_x, COURT_RIGHT - 150)
        # Center strategy uses the default predicted position
    
    def should_attempt_hit(self, shuttle):
        """Determine if NPC should attempt to hit the shuttlecock"""
        # Basic distance check
        distance = abs(shuttle.x - self.rect.centerx)
        
        # Check if shuttlecock is at a reasonable height
        height_good = abs(shuttle.y - self.rect.centery) < 100
        
        # More likely to attempt hit if NPC is facing the right direction
        direction_good = (shuttle.x > self.rect.centerx and self.facing_right) or \
                        (shuttle.x < self.rect.centerx and not self.facing_right)
        
        return distance < 80 and (height_good or direction_good)
    
    def choose_shot_type(self, shuttle):
        """Choose the most strategic shot type based on situation"""
        # If player is not tracked, use default logic
        if self.player_last_x == 0:
            if not self.on_ground and shuttle.y < self.rect.centery:
                return "smash"
            elif shuttle.y > self.rect.centery and random.random() < 0.3:
                return "drop"
            else:
                return "normal"
        
        # Choose shot strategically based on player position
        player_near_net = self.player_last_x > NET_X * 0.8
        player_far_back = self.player_last_x < NET_X * 0.5
        
        if not self.on_ground and shuttle.y < self.rect.centery:
            # Good position for a smash
            return "smash"
        elif player_near_net and random.random() < 0.7:
            # If player is near the net, use a lob or smash to push them back
            return "normal" if random.random() < 0.5 else "smash"
        elif player_far_back and random.random() < 0.7:
            # If player is far back, use a drop shot
            return "drop"
        else:
            # Default to normal shots with occasional variation
            shot_choices = ["normal", "drop", "smash"]
            weights = [0.7, 0.15, 0.15]
            return random.choices(shot_choices, weights=weights)[0]
    
    def hit_shuttlecock(self, shuttle):
        """Override parent method to add strategic aiming"""
        if not super().hit_shuttlecock(shuttle):
            return False
        
        # Strategic aiming based on player position (modifies the shuttle velocity after hit)
        if self.player_last_x > 0 and self.aim_for_corners:
            # Player is being tracked, aim away from them
            player_y = self.player_last_y
            
            # Aim for the opposite corner from player
            if player_y < COURT_GROUND_Y - 200:  # Player is higher up
                # Aim for the bottom corner
                shuttle.vy = -5  # Lower arc
            else:
                # Aim for the top corner
                shuttle.vy = -10  # Higher arc
            
            # Add slight horizontal adjustment
            shuttle.vx += random.uniform(-1, 1)
        
        return True
    
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
            
            # Random vertical movement
            self.jump_timer += 1
            if self.jump_timer > 120:
                self.velocity_y = random.choice([-WALK_SPEED, WALK_SPEED]) * 0.5
                self.jump_timer = 0
        
        # Let parent class handle standard movement physics
        super().update()
        
        # Ensure NPC stays on right side of net
        if self.rect.left < NET_X:
            self.rect.left = NET_X
            self.velocity_x = WALK_SPEED  # Move back to right side
            self.direction = 1  # Change direction if at net