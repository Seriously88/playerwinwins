import pygame
import os

class PlayerAnimation:
    def __init__(self):
        # Animation properties
        self.frame_width = 32
        self.frame_height = 32
        self.scale_factor = 2  # Scale sprites to be larger
        self.current_frame = 0
        self.animation_speed = 0.15  # How fast to cycle through frames
        self.animation_timer = 0
        self.current_animation = "idle"
        
        # Load all animation frames
        self.frames = []
        self.load_animation_frames()
        
        # Define animation sequences
        self.animations = {
            "idle": {"start": 0, "end": 5, "loop": True},
            "run": {"start": 6, "end": 13, "loop": True},
            "jump": {"start": 14, "end": 17, "loop": False},
            "swing": {"start": 18, "end": 23, "loop": False},
            "smash": {"start": 24, "end": 29, "loop": False},
            "crouch": {"start": 30, "end": 35, "loop": True}
        }
        
        # Animation state
        self.is_animation_finished = False
        
        # Print debug info
        print(f"PlayerAnimation initialized with {len(self.frames)} frames")
        print(f"Animation sequences: {list(self.animations.keys())}")
    
    def load_animation_frames(self):
        """Load all animation frames from the player_animation_improved directory"""
        self.frames = []
        animation_dir = "assests/player_animation_improved"
        
        # Check if directory exists
        if not os.path.exists(animation_dir):
            print(f"Warning: Animation directory '{animation_dir}' does not exist!")
            # Fall back to original directory if improved doesn't exist
            animation_dir = "assests/player_animation"
            if not os.path.exists(animation_dir):
                print(f"Warning: Fallback animation directory '{animation_dir}' does not exist either!")
                return
        
        # Get all PNG files in the animation directory
        frame_files = [f for f in os.listdir(animation_dir) if f.endswith('.png')]
        frame_files.sort()  # Ensure correct order
        
        print(f"Found {len(frame_files)} animation frames in {animation_dir}")
        
        for frame_file in frame_files:
            try:
                # Load the image with alpha channel
                frame_path = os.path.join(animation_dir, frame_file)
                frame = pygame.image.load(frame_path).convert_alpha()
                
                # Scale the image
                scaled_width = self.frame_width * self.scale_factor
                scaled_height = self.frame_height * self.scale_factor
                frame = pygame.transform.scale(frame, (scaled_width, scaled_height))
                
                self.frames.append(frame)
            except pygame.error as e:
                print(f"Error loading animation frame {frame_file}: {e}")
    
    def set_animation(self, animation_name):
        """Set the current animation if it's not already playing"""
        if animation_name not in self.animations:
            print(f"Warning: Animation '{animation_name}' not found! Using 'idle' instead.")
            animation_name = "idle"
            
        if self.current_animation != animation_name:
            self.current_animation = animation_name
            self.current_frame = self.animations[animation_name]["start"]
            self.is_animation_finished = False
    
    def update(self, dt):
        """Update the animation frame based on elapsed time"""
        if not self.frames:
            return
            
        animation = self.animations[self.current_animation]
        
        # Update animation timer
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame += 1
            
            # Check if we've reached the end of the animation
            if self.current_frame > animation["end"]:
                if animation["loop"]:
                    # Loop back to start
                    self.current_frame = animation["start"]
                else:
                    # Stay on last frame
                    self.current_frame = animation["end"]
                    self.is_animation_finished = True
    
    def get_current_frame(self):
        """Get the current animation frame surface"""
        if not self.frames:
            return None
            
        # Ensure frame index is valid
        frame_index = max(0, min(self.current_frame, len(self.frames) - 1))
        return self.frames[frame_index]
    
    def draw(self, surface, x, y, flip_x=False):
        """Draw the current animation frame at the specified position"""
        frame = self.get_current_frame()
        if frame:
            if flip_x:
                frame = pygame.transform.flip(frame, True, False)
            
            # Center the sprite on the player's position
            draw_x = x - (self.frame_width * self.scale_factor) // 2
            draw_y = y - (self.frame_height * self.scale_factor)
            
            surface.blit(frame, (draw_x, draw_y))
        else:
            # Draw a placeholder rectangle if no frame is available
            placeholder_rect = pygame.Rect(
                x - (self.frame_width * self.scale_factor) // 2,
                y - (self.frame_height * self.scale_factor),
                self.frame_width * self.scale_factor,
                self.frame_height * self.scale_factor
            )
            pygame.draw.rect(surface, (255, 0, 255), placeholder_rect)  # Magenta for visibility
            
            # Draw debug text
            font = pygame.font.SysFont(None, 24)
            text = font.render(f"No frame: {self.current_animation}", True, (255, 255, 255))
            surface.blit(text, (x - text.get_width() // 2, y - self.frame_height * self.scale_factor - 20))
    
    def is_finished(self):
        """Check if a non-looping animation has finished"""
        return self.is_animation_finished 