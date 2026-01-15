# games/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # ← используем index, а не index_with_pagination
    path('autocomplete/', views.autocomplete, name='autocomplete'),
    path('game/<int:game_id>/', views.game_detail, name='game_detail'),
    path('debug-search/', views.debug_search, name='debug_search'),
    path('test-search/', views.test_search, name='test_search'),  # если нужно
]