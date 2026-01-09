# boardgames_site/settings/local.py
from .base import *

# Настройки для разработки
DEBUG = True
SECRET_KEY = 'ваш-секретный-ключ-для-разработки'  # можно оставить простой

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Безопасность для разработки
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0