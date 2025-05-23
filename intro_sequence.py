import pygame
import cv2
import numpy as np
from config import WIDTH, HEIGHT

class IntroSequence:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Badminton Smash Game - Intro")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Load instruction scene
        try:
            self.instruction_scene = pygame.image.load('assests/instruction and tips.png')
            self.instruction_scene = pygame.transform.scale(self.instruction_scene, (WIDTH, HEIGHT))
        except Exception as e:
            print(f"Error loading instruction scene: {e}")
            self.instruction_scene = None
            
        # Button properties
        self.start_button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT - 100, 200, 50)
        self.start_button_color = (0, 255, 255)  # Cyan
        self.start_button_hover_color = (0, 200, 255)
        self.button_font = pygame.font.SysFont(None, 36)
        self.start_button_text = self.button_font.render("Start Game", True, (0, 0, 0))
        self.start_button_text_rect = self.start_button_text.get_rect(center=self.start_button_rect.center)

    def play_video(self):
        # Open the video file
        video = cv2.VideoCapture('assests/transitionscene.mp4')
        
        if not video.isOpened():
            print("Error loading video file")
            return False
            
        while True:
            ret, frame = video.read()
            
            if not ret:
                break
                
            # Convert frame from BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (WIDTH, HEIGHT))
            
            # Convert to pygame surface - remove rotation and fix orientation
            frame = np.swapaxes(frame, 0, 1)
            frame = pygame.surfarray.make_surface(frame)
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    video.release()
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        video.release()
                        return True
            
            # Display frame
            self.screen.blit(frame, (0, 0))
            pygame.display.flip()
            self.clock.tick(30)
            
        video.release()
        return True

    def show_instructions(self):
        showing_instructions = True
        
        while showing_instructions and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return False
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        if self.start_button_rect.collidepoint(event.pos):
                            return True
                            
            # Draw instruction scene
            if self.instruction_scene:
                self.screen.blit(self.instruction_scene, (0, 0))
            else:
                self.screen.fill((0, 0, 0))
            
            # Draw start button with hover effect
            mouse_pos = pygame.mouse.get_pos()
            button_color = self.start_button_hover_color if self.start_button_rect.collidepoint(mouse_pos) else self.start_button_color
            pygame.draw.rect(self.screen, button_color, self.start_button_rect, border_radius=10)
            self.screen.blit(self.start_button_text, self.start_button_text_rect)
            
            pygame.display.flip()
            self.clock.tick(60)
            
        return False

    def run(self):
        # Play intro video first
        if not self.play_video():
            return False
            
        # Show instruction scene
        if not self.show_instructions():
            return False
            
        return True 