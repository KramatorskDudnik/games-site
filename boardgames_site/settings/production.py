# boardgames_site/settings/production.py
from .base import *
from decouple import config
import dj_database_url
import os

# Настройки для продакшена
DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY')

# Разрешаем все хосты для Render (потом замените на ваш домен)
ALLOWED_HOSTS = ['*']  # Временное решение для деплоя

# Настройки безопасности для продакшена
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 год
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Для облачных хостингов (Render)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ========== БАЗА ДАННЫХ ДЛЯ RENDER ==========
# Используем DATABASE_URL от Render, если он есть
DATABASE_URL = config('DATABASE_URL', default=None)
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True
        )
    }

# ========== СТАТИЧЕСКИЕ ФАЙЛЫ ДЛЯ RENDER ==========
# Настройки для WhiteNoise
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Middleware для WhiteNoise уже должен быть в base.py
# Убедитесь что в base.py есть: 'whitenoise.middleware.WhiteNoiseMiddleware'