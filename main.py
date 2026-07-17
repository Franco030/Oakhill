import sys
from src.core.Game import Game

if __name__ == "__main__":
    game = Game(sys.argv)
    game.run()