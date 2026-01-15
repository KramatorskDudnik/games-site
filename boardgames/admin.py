from django.contrib import admin
from .models import Game, GameImage

class GameImageInline(admin.TabularInline):
    model = GameImage
    extra = 1  # Количество пустых форм для добавления фото

class GameAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty_rating', 'min_players', 'max_players', 'playtime']
    list_filter = ['difficulty_rating']
    search_fields = ['title', 'description']
    inlines = [GameImageInline]  # Чтобы добавлять фото прямо в форме игры

admin.site.register(Game, GameAdmin)