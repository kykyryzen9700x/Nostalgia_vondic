from backend.games.pacman import PacmanGame
from backend.games.snake import SnakeGame
from backend.games.minesweeper import MinesweeperGame
from backend.games.flappy import FlappyBirdGame
from backend.games.game2048 import Game2048
from backend.games.tetris import TetrisGame
from backend.games.checkers import CheckersGame
from backend.games.chess import ChessGame
from backend.games.space_invaders import SpaceInvadersGame
from backend.games.game_manager import GameManager
from backend.games.game_routes import game_bp


__all__ = [
    'PacmanGame', 
    'SnakeGame', 
    'MinesweeperGame',
    'FlappyBirdGame', 
    'Game2048', 
    'TetrisGame',
    'CheckersGame',
    'ChessGame',
    'SpaceInvadersGame',
    'GameManager', 
    'game_bp'
]