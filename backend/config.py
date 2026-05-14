import os
import secrets


class Config:
    #основные значения
    #токен
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(32))
    #созданиебд
    DATABASE = 'users.db'
    #скорости
    SNAKE_SPEED = 150
    PACMAN_SPEED = 200
    #значения
    MAX_SCORES_PER_PAGE = 10
    MIN_PASSWORD_LENGTH = 6
    MIN_NICKNAME_LENGTH = 3
    #пути
    TEMPLATES_FOLDER = 'templates'
    STATIC_FOLDER = 'static'
    #отладка
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    OAUTH_CLIENT_ID = '990cac37-355c-466e-9fa3-b044d56d2191'
    OAUTH_CLIENT_SECRET = 'd51f2425-7a7d-4423-8ff2-bf5a2a6dbabe12cce7b841c54376b62c55a957f7e086'
    OAUTH_REDIRECT_URI = 'http://localhost:8080/oauth/callback'
    OAUTH_AUTHORIZE_URL = 'https://vondic.knopusmedia.ru/oauth/authorize'
    OAUTH_TOKEN_URL = 'https://vondic.knopusmedia.ru/oauth/token'
    OAUTH_USERINFO_URL = 'https://vondic.knopusmedia.ru/oauth/userinfo'

    BOT_TOKEN = 'Rvwa2_GWKjQ2ifGtUFXBwu78dqKHW9k-buQrYAzi56c'
    BOT_BASE_URL = 'https://vondic.knopusmedia.ru'
    ADMIN_CHAT_ID = '5cf17a45-2907-4819-bd28-a1d28470999a'
    BOT_ID = 'ec77f86b-1c57-400d-a5e8-948be0a6f22f'


config = Config()
