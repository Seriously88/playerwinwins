import pygame
import os
import sys

# Initialize pygame
pygame.init()

# Set a video mode (required for pygame to work with images)
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Processing Sprite Sheet")

# Define colors
BLUE_BACKGROUND = (91, 127, 191)  # The blue background color in the sprite sheet
COLOR_THRESHOLD = 40  # Threshold for color matching

# Load the sprite sheet
sprite_sheet_path = "assests/Badminton Player Animation.jpeg"
try:
    sprite_sheet = pygame.image.load(sprite_sheet_path).convert()
except pygame.error as e:
    print(f"Error loading sprite sheet: {e}")
    sys.exit(1)

# Define sprite dimensions and positions
# Based on the sprite sheet layout, we'll define the positions of each animation frame
sprite_width = 32
sprite_height = 32

# Define rows and columns in the sprite sheet
rows = 8
cols = 6

# Create output directory if it doesn't exist
output_dir = "assests/player_animation"
os.makedirs(output_dir, exist_ok=True)

# Function to remove blue background from a surface
def remove_background(surface):
    # Create a copy of the surface with per-pixel alpha
    result = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    
    # Iterate through each pixel
    for y in range(surface.get_height()):
        for x in range(surface.get_width()):
            color = surface.get_at((x, y))
            
            # Check if the color is close to the blue background
            if (abs(color[0] - BLUE_BACKGROUND[0]) < COLOR_THRESHOLD and
                abs(color[1] - BLUE_BACKGROUND[1]) < COLOR_THRESHOLD and
                abs(color[2] - BLUE_BACKGROUND[2]) < COLOR_THRESHOLD):
                # Make this pixel transparent
                result.set_at((x, y), (0, 0, 0, 0))
            else:
                # Keep the original color
                result.set_at((x, y), color)
    
    return result

# Extract sprites from the sheet
print("Processing sprite sheet...")
frame_count = 0
animation_frames = []

for row in range(rows):
    for col in range(cols):
        # Skip empty cells (sprite sheet isn't fully populated)
        if row >= 7 and col >= 2:
            continue
            
        # Calculate position in the sprite sheet
        x = col * sprite_width
        y = row * sprite_height
        
        # Extract the sprite
        sprite_rect = pygame.Rect(x, y, sprite_width, sprite_height)
        sprite = sprite_sheet.subsurface(sprite_rect)
        
        # Remove blue background
        sprite_transparent = remove_background(sprite)
        
        # Save the sprite
        filename = f"{output_dir}/player_frame_{frame_count:03d}.png"
        pygame.image.save(sprite_transparent, filename)
        animation_frames.append(filename)
        
        frame_count += 1
        print(f"Saved frame {frame_count}: {filename}")

print(f"Processed {frame_count} animation frames")

# Create a simple animation metadata file
with open(f"{output_dir}/animation_data.txt", "w") as f:
    f.write(f"total_frames: {frame_count}\n")
    f.write("frame_width: 32\n")
    f.write("frame_height: 32\n")
    f.write("animations:\n")
    f.write("  idle: 0-5\n")
    f.write("  run: 6-13\n")
    f.write("  jump: 14-17\n")
    f.write("  swing: 18-23\n")
    f.write("  smash: 24-29\n")
    f.write("  crouch: 30-35\n")

print("Animation metadata created")
print("Sprite sheet processing complete!")

# Quit pygame
pygame.quit() 