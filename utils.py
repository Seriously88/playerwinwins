import pygame
from config import *

def draw_court(surface):
    """Draw a badminton court if the court image is not available"""
    # Draw court boundary
    pygame.draw.rect(surface, BLACK, (COURT_LEFT, 0, COURT_RIGHT - COURT_LEFT, COURT_GROUND_Y), 2)
    
    # Draw net
    pygame.draw.line(surface, BLACK, (NET_X, 0), (NET_X, COURT_GROUND_Y), 2)
    
    # Draw ground line
    pygame.draw.line(surface, BLACK, (COURT_LEFT, COURT_GROUND_Y), (COURT_RIGHT, COURT_GROUND_Y), 2)
    
    # Draw service areas
    pygame.draw.rect(surface, (200, 200, 200), (COURT_LEFT + 30, COURT_GROUND_Y - 200, NET_X - COURT_LEFT - 60, 100), 1)
    pygame.draw.rect(surface, (200, 200, 200), (NET_X + 30, COURT_GROUND_Y - 200, COURT_RIGHT - NET_X - 60, 100), 1)

def display_message(surface, message, position=None, size=36, color=BLACK):
    """Display a message on the screen"""
    if position is None:
        position = (WIDTH//2 - len(message)*5, HEIGHT//2)
        
    font = pygame.font.SysFont(None, size)
    text = font.render(message, True, color)
    surface.blit(text, position)
    
def check_win_condition(player_score, npc_score):
    """
    Check if a player has won the game based on official badminton rules
    - First to 21 points wins
    - If score is 20-20, side must win by 2 clear points
    - If score reaches 29-29, first to 30 wins
    """
    if player_score >= POINTS_TO_WIN and (player_score - npc_score >= MIN_POINT_DIFFERENCE or player_score == MAX_SCORE):
        return "Player"
    elif npc_score >= POINTS_TO_WIN and (npc_score - player_score >= MIN_POINT_DIFFERENCE or npc_score == MAX_SCORE):
        return "NPC"
    return None
