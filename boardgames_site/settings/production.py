from .base import *
from decouple import config
import os

# Настройки для продакшена
DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY')

# Разрешаем все хосты для Render
ALLOWED_HOSTS = ['*']

# Настройки безопасности для продакшена
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Для облачных хостингов (Render)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Статические файды
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# База данных - используем SQLite для начала
# Если позже добавите PostgreSQL на Render, добавьте:
# import dj_database_url
# DATABASE_URL = config('DATABASE_URL', default=None)
# if DATABASE_URL:
#     DATABASES = {
#         'default': dj_database_url.config(default=DATABASE_URL)
#     }
