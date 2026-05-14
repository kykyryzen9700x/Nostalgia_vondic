import hashlib
import secrets


def hash_password(password: str) -> str:
    #хэширование
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${pwd_hash.hex()}"


def verify_password(stored_password: str, provided_password: str) -> bool:
    #верификация пароля
    try:
        salt, pwd_hash = stored_password.split('$')
        test_hash = hashlib.pbkdf2_hmac('sha256', provided_password.encode(), salt.encode(), 100000).hex()
        return pwd_hash == test_hash
    except Exception:
        return False


def validate_email(email: str) -> bool:
    #проверка почты
    if not email:
        return False
    return '@' in email and '.' in email and len(email) > 5


def validate_password(password: str, min_length: int = 6) -> bool:
    #проверк пароля
    if not password:
        return False
    return len(password) >= min_length


def validate_nickname(nickname: str, min_length: int = 3) -> bool:
    #проверка пароля
    if not nickname:
        return False
    return len(nickname) >= min_length and nickname.isalnum()