# games/models.py - ПРАВИЛЬНАЯ ВЕРСИЯ
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Game(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    min_players = models.IntegerField(verbose_name="Минимальное количество игроков")
    max_players = models.IntegerField(verbose_name="Максимальное количество игроков")
    playtime_minutes = models.IntegerField(verbose_name="Время игры (минуты)")
    difficulty = models.IntegerField(
        verbose_name="Сложность",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True,
        null=True
    )
    categories = models.CharField(max_length=200, verbose_name="Категории", blank=True)  # ← CharField!
    rules_link = models.URLField(verbose_name="Ссылка на правила", blank=True)
    video_link = models.URLField(verbose_name="Видео", blank=True)
    
    def __str__(self):
        return self.title
    
    def get_formatted_playtime(self):
        """Возвращает отформатированное время игры"""
        if not self.playtime_minutes:
            return ""
        
        hours = self.playtime_minutes // 60
        minutes = self.playtime_minutes % 60
        
        if hours > 0 and minutes > 0:
            return f"{hours}ч {minutes}мин"
        elif hours > 0:
            return f"{hours}ч"
        else:
            return f"{minutes}мин"
    
    def get_players_display(self):
        """Возвращает отформатированное количество игроков"""
        if not self.min_players:
            return ""
        
        if self.max_players and self.max_players != self.min_players:
            return f"{self.min_players}-{self.max_players}"
        else:
            return str(self.min_players)


class GameImage(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='game_images/', blank=True, null=True)
    url = models.URLField(blank=True)
    caption = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return f"Изображение для {self.game.title}"