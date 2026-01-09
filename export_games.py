import os
import django
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "boardgames_site.settings")
django.setup()

from games.models import Game

# Экспортируем все игры
games = Game.objects.all()
data = []
for game in games:
    data.append({
        "model": "games.game",
        "pk": game.id,
        "fields": {
            "title": game.title,
            "description": game.description,
            "min_players": game.min_players,
            "max_players": game.max_players,
            "playtime_minutes": game.playtime_minutes,
            "complexity": game.complexity,
            "created_at": game.created_at.isoformat() if game.created_at else None,
            "updated_at": game.updated_at.isoformat() if game.updated_at else None,
        }
    })

# Сохраняем в файл с UTF-8
with open("games_fixture.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Экспортировано {len(data)} игр")
