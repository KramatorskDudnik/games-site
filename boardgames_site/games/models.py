from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Game(models.Model):
    # Основная информация
    title = models.CharField(max_length=200, verbose_name="Название игры")
    description = models.TextField(verbose_name="Описание")
  #  rules = models.TextField(verbose_name="Правила", blank=True)  # Может быть пустым
    
    # Сложность: число от 1 до 5
    difficulty_rating = models.PositiveIntegerField(
        verbose_name="Сложность (1-5)",
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Время партии в минутах
    playtime = models.PositiveIntegerField(
        verbose_name="Среднее время партии (мин)",
        help_text="В минутах",
        validators=[MinValueValidator(1)]
    )
    
    # Количество игроков
    min_players = models.PositiveIntegerField(
        verbose_name="Минимальное количество игроков",
        validators=[MinValueValidator(1)]
    )
    max_players = models.PositiveIntegerField(
        verbose_name="Максимальное количество игроков",
        validators=[MinValueValidator(1)]
    )
    
    # Ссылки на летсплеи (видео)
    letsplays = models.TextField(
        verbose_name="Ссылки на летсплеи (через запятую)",
        blank=True,
        help_text="Ссылки на YouTube или другие видео, разделенные запятой"
    )
    
    # Дополнительные поля
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Игра"
        verbose_name_plural = "Игры"

class GameImage(models.Model):
    """Модель для нескольких фотографий игры (карусель)"""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='game_images/', verbose_name="Фотография")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок отображения")
    
    class Meta:
        ordering = ['order']
        verbose_name = "Фотография игры"
        verbose_name_plural = "Фотографии игр"