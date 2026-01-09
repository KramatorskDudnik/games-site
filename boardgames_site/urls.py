from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def home_redirect(request):
    """Перенаправление с главной на список игр"""
    return redirect('index')  # ← ИЗМЕНИЛИ на 'index'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('games/', include('games.urls')),
    path('', home_redirect, name='home'),
]
