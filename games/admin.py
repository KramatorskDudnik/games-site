# games/admin.py
from django.contrib import admin
from .models import Game, GameImage

class GameImageInline(admin.TabularInline):
    model = GameImage
    extra = 1

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'min_players', 'max_players', 'playtime_minutes', 'difficulty')
    list_filter = ('categories', 'difficulty')
    search_fields = ('title', 'description')
    inlines = [GameImageInline]

@admin.register(GameImage)
class GameImageAdmin(admin.ModelAdmin):
    list_display = ('game', 'caption')
    list_filter = ('game',)