from backend.games.pacman import PacmanGame
from backend.games.snake import SnakeGame
from backend.games.minesweeper import MinesweeperGame
from backend.games.flappy import FlappyBirdGame
from backend.games.game2048 import Game2048
from backend.games.tetris import TetrisGame
from backend.games.checkers import CheckersGame
from backend.games.chess import ChessGame
from backend.games.space_invaders import SpaceInvadersGame
from backend.scores.score_manager import ScoreManager
import uuid


class GameManager:
    # для игры
    GAMES = {
        'pacman': PacmanGame,
        'snake': SnakeGame,
        'minesweeper': MinesweeperGame,
        'flappy': FlappyBirdGame,
        '2048': Game2048,
        'tetris': TetrisGame,
        'checkers': CheckersGame,
        'chess': ChessGame,
        'space_invaders': SpaceInvadersGame
    }
    MULTIPLAYER_GAMES = ['checkers', 'chess']
    
    def __init__(self):
        self._active_games = {}
        self._lobbies = {}
    
    def get_or_create_game(self, game_type: str, user_id: str):
        """Получить существующую игру или создать новую"""
        game_id = f"{game_type}_{user_id}"
        if game_id not in self._active_games:
            if game_type not in self.GAMES:
                raise ValueError(f"Unknown game type: {game_type}")
            GameClass = self.GAMES[game_type]
            self._active_games[game_id] = GameClass()
            print(f"[GameManager] Created new game: {game_id}")
        return self._active_games[game_id]
    
    def create_lobby(self, game_type: str, host_user_id: str, host_nickname: str):
        """создание лобби"""
        if game_type not in self.MULTIPLAYER_GAMES:
            raise ValueError(f"Game {game_type} is not multiplayer")
        lobby_id = str(uuid.uuid4())[:8].upper()
        GameClass = self.GAMES[game_type]
        game = GameClass()
        self._lobbies[lobby_id] = {
            'game_type': game_type,
            'host_user_id': host_user_id,
            'host_nickname': host_nickname,
            'guest_user_id': None,
            'guest_nickname': None,
            'game': game,
            'current_turn': 'white',
            'players': {
                'white': host_user_id,
                'black': None
            }
        }
        # сохраняем в активных играх для хоста
        game_id = f"{game_type}_{host_user_id}"
        self._active_games[game_id] = game
        print(f"[GameManager] Created lobby: {lobby_id} for {game_type}")
        return lobby_id
    
    def join_lobby(self, lobby_id: str, user_id: str, nickname: str):
        """подключиться к лобби"""
        if lobby_id not in self._lobbies:
            return False, "Лобби не найдено"
        lobby = self._lobbies[lobby_id]
        if lobby['guest_user_id'] is not None:
            return False, "Лобби уже заполнено"
        lobby['guest_user_id'] = user_id
        lobby['guest_nickname'] = nickname
        lobby['players']['black'] = user_id
        # сохранять игру для гостя
        game_id = f"{lobby['game_type']}_{user_id}"
        self._active_games[game_id] = lobby['game']
        print(f"[GameManager] User {nickname} joined lobby: {lobby_id}")
        return True, "Подключение успешно"
    
    def get_lobby_info(self, lobby_id: str):
        """получить данные о лобби"""
        if lobby_id not in self._lobbies:
            return None
        lobby = self._lobbies[lobby_id]
        return {
            'lobby_id': lobby_id,
            'game_type': lobby['game_type'],
            'host_nickname': lobby['host_nickname'],
            'guest_nickname': lobby['guest_nickname'],
            'current_turn': lobby['current_turn'],
            'is_full': lobby['guest_user_id'] is not None
        }
    
    def get_player_game(self, game_type: str, user_id: str):
        """Получить игру игрока"""
        game_id = f"{game_type}_{user_id}"
        # проверяем активные игры
        if game_id in self._active_games:
            return self._active_games[game_id]
        # проверяем лобби сколько там игроков
        for lobby_id, lobby in self._lobbies.items():
            if lobby['game_type'] == game_type:
                if lobby['host_user_id'] == user_id or lobby['guest_user_id'] == user_id:
                    self._active_games[game_id] = lobby['game']
                    return lobby['game']
        return None
    
    def make_move(self, game_type: str, user_id: str, from_pos: tuple, to_pos: tuple):
        """сделать ход в онлайне"""
        game = self.get_player_game(game_type, user_id)
        if not game:
            return False, "Игра не найдена"
        # поиск лобби
        lobby = None
        for l_id, l in self._lobbies.items():
            if l['game_type'] == game_type and l['game'] == game:
                lobby = l
                break
        if not lobby:
            return False, "Лобби не найдено"
        # даём игрокам тест
        if lobby['host_user_id'] == user_id:
            player_color = 'white'
        else:
            player_color = 'black'
        # проверка чей ход
        if lobby['current_turn'] != player_color:
            return False, "Сейчас не ваш ход"
        # сделать ход
        success, message = game.make_move(from_pos, to_pos, player_color)
        if success:
            # передача хода
            lobby['current_turn'] = 'black' if lobby['current_turn'] == 'white' else 'white'
        return success, message
    
    def remove_game(self, game_type: str, user_id: str):
        """удалить игру из кэша"""
        game_id = f"{game_type}_{user_id}"
        if game_id in self._active_games:
            del self._active_games[game_id]
            print(f"[GameManager] Removed game: {game_id}")
    
    def save_score_if_game_over(self, game_type: str, user_id: str, nickname: str, game):
        """cохранить результат если игра закончилась"""
        if game.game_over and hasattr(game, 'score'):
            won = getattr(game, 'won', False)
            try:
                ScoreManager.save_score(int(user_id), nickname, game_type, game.score, won)
                print(f"[GameManager] Saved score: {user_id} - {game.score}")
            except Exception as e:
                print(f"[GameManager] Error saving score: {e}")
            self.remove_game(game_type, user_id)
            return True
        return False
    
    @staticmethod
    def get_game_state(game):
        """проверяем состояние для отправки пакетов"""
        try:
            state = {
                'map_html': game.get_map_html(),
                'score': getattr(game, 'score', 0),
                'game_over': game.game_over,
                'won': getattr(game, 'won', False)
            }
            # для мультиплеерных игр добавляем дополнительную информацию
            if hasattr(game, 'get_board_state'):
                state['board_state'] = game.get_board_state()
            return state
        except Exception as e:
            print(f"[GameManager] Error getting game state: {e}")
            return {
                'map_html': '<div>Ошибка отображения игры</div>',
                'score': 0,
                'game_over': True,
                'won': False
            }
    
    def reset_game(self, game_type: str, user_id: str):
        """сброс игры"""
        self.remove_game(game_type, user_id)
        return self.get_or_create_game(game_type, user_id)