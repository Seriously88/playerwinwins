from game_engine import BadmintonGame
from intro_sequence import IntroSequence

if __name__ == "__main__":
    # Show intro sequence first
    intro = IntroSequence()
    if intro.run():
        # Start the main game only if intro sequence completes successfully
        game = BadmintonGame()
        game.run()
    else:
        print("Game closed during intro sequence")