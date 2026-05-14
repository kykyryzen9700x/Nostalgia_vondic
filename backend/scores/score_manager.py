from backend.database.db_manager import get_db


class ScoreManager:
    #работа с рекордами
    @staticmethod
    def save_score(user_id: int, nickname: str, game_type: str, score: int, won: bool = False):
        #сохранение рекордов
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO scores (user_id, nickname, game_type, score, won)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, nickname, game_type, score, won))
                return True
        except Exception as e:
            print(f"[Score Error] {e}")
            return False
    
    @staticmethod
    def get_top_scores(game_type: str = None, limit: int = 10):
        #сбор топов
        with get_db() as conn:
            cursor = conn.cursor()
            if game_type:
                cursor.execute('''
                    SELECT nickname, score, game_type, won, played_at
                    FROM scores
                    WHERE game_type = ?
                    ORDER BY score DESC
                    LIMIT ?
                ''', (game_type, limit))
            else:
                cursor.execute('''
                    SELECT nickname, score, game_type, won, played_at
                    FROM scores
                    ORDER BY score DESC
                    LIMIT ?
                ''', (limit,))
            return cursor.fetchall()
    
    @staticmethod
    def get_user_scores(user_id: int, limit: int = 20):
        #получение рекордов
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT game_type, score, won, played_at
                FROM scores
                WHERE user_id = ?
                ORDER BY played_at DESC
                LIMIT ?
            ''', (user_id, limit))
            return cursor.fetchall()
    
    @staticmethod
    def get_best_score(user_id: int, game_type: str):
        #сбор рекордов для каждой игры
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT MAX(score) as best_score
                FROM scores
                WHERE user_id = ? AND game_type = ?
            ''', (user_id, game_type))
            result = cursor.fetchone()
            return result['best_score'] if result else 0