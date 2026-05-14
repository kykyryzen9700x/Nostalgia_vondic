import hashlib
import secrets
from backend.database.models import (
    get_user_by_email, get_user_by_id, get_user_by_nickname,
    create_user, update_user_nickname, update_user_password,
    email_exists, nickname_exists
)
from backend.auth.security import hash_password, verify_password


class UserManager:
    #работа с профилем
    @staticmethod
    def authenticate(email: str, password: str):
        #аутентификация
        user = get_user_by_email(email)
        if user and verify_password(user['password'], password):
            return {
                'id': user['id'],
                'nickname': user['nickname'],
                'email': email
            }
        return None

    @staticmethod
    def register(email: str, password: str, nickname: str = None):
        #регистрация
        if email_exists(email):
            return False, None, "Email уже зарегистрирован"
        
        if nickname and nickname_exists(nickname):
            return False, None, "Никнейм уже занят"
        
        if not nickname:
            nickname = f"user_{hashlib.md5(email.encode()).hexdigest()[:8]}"
        
        while nickname_exists(nickname):
            nickname = f"{nickname}_{secrets.token_hex(2)}"
        
        hashed_pw = hash_password(password)
        user_id = create_user(email, hashed_pw, nickname)
        
        return True, user_id, None
    
    @staticmethod
    def change_nickname(user_id: int, new_nickname: str):
        #смена ника
        if nickname_exists(new_nickname, exclude_user_id=user_id):
            return False, "Никнейм уже занят"
        if update_user_nickname(user_id, new_nickname):
            return True, "Никнейм успешно изменён"
        return False, "Ошибка при смене никнейма"
    
    @staticmethod
    def change_password(user_id: int, old_password: str, new_password: str):
        #смена пароля
        user = get_user_by_id(user_id)
        if not user:
            return False, "Пользователь не найден"
        if not verify_password(user['password'], old_password):
            return False, "Неверный текущий пароль"
        new_hashed = hash_password(new_password)
        if update_user_password(user_id, new_hashed):
            return True, "Пароль успешно изменён"
        return False, "Ошибка при смене пароля"
    
    @staticmethod
    def get_user_info(user_id: int):
        #просмотр информации
        user = get_user_by_id(user_id)
        if user:
            return dict(user)
        return None