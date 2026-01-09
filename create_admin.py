import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boardgames_site.settings')

import django
django.setup()

from django.contrib.auth.models import User

# Создаем суперпользователя если нет
if not User.objects.filter(username='admin').exists():
    user = User.objects.create_superuser(
        username='admin',
        email='admin@games.com',
        password='Admin123!'  # ИЗМЕНИТЕ ЭТОТ ПАРОЛЬ!
    )
    print(f'Создан суперпользователь: {user.username}')
else:
    print('Суперпользователь уже существует')
    
# Проверим
print(f'Всего пользователей: {User.objects.count()}')
