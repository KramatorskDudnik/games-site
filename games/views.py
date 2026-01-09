# views.py
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Game
import json

def test_search(request):
    """Тестовая страница для проверки поиска"""
    query = request.GET.get('q', '')
    
    html = f"""
    <html>
    <body>
        <h1>Тест поиска</h1>
        <form method="GET">
            <input type="text" name="q" value="{query}">
            <button type="submit">Тест</button>
        </form>
    """
    
    if query:
        # Тест разных вариантов поиска
        html += f"<h2>Запрос: '{query}'</h2>"
        
        # 1. icontains
        games_icontains = Game.objects.filter(title__icontains=query)
        html += f"<h3>icontains: {games_icontains.count()} игр</h3>"
        for g in games_icontains[:5]:
            html += f"<p>- {g.title}</p>"
        
        # 2. istartswith
        games_istartswith = Game.objects.filter(title__istartswith=query)
        html += f"<h3>istartswith: {games_istartswith.count()} игр</h3>"
        for g in games_istartswith[:5]:
            html += f"<p>- {g.title}</p>"
        
        # 3. iexact
        games_iexact = Game.objects.filter(title__iexact=query)
        html += f"<h3>iexact: {games_iexact.count()} игр</h3>"
        for g in games_iexact:
            html += f"<p>- {g.title}</p>"
        
        # 4. Поиск по любому регистру вручную
        html += f"<h3>Все игры с буквой '{query[0]}' в названии:</h3>"
        all_games = Game.objects.all()
        matched = []
        for g in all_games:
            if query.lower() in g.title.lower():
                matched.append(g)
        
        html += f"<p>Найдено вручную: {len(matched)}</p>"
        for g in matched[:10]:
            html += f"<p>- {g.title}</p>"
    
    html += "</body></html>"
    return HttpResponse(html)

def index(request):
    """Главная страница со списком игр и фильтрами"""
    query = request.GET.get('q', '').strip().lower()
    page = request.GET.get('page', 1)
    
    # Параметры фильтров
    players_min = request.GET.get('players_min', '').strip()
    players_max = request.GET.get('players_max', '').strip()
    time_min = request.GET.get('time_min', '').strip()
    time_max = request.GET.get('time_max', '').strip()
    difficulty = request.GET.get('difficulty', '').strip()
    
    print("=" * 50)
    print(f"ФИЛЬТРЫ: игроки {players_min}-{players_max}, время {time_min}-{time_max}, сложность {difficulty}")
    
    # Начинаем с всех игр
    games_list = Game.objects.all()
    
    # Поиск по названию (если есть)
    if query:
        matched_ids = []
        for game in games_list:
            if query in ' '.join(game.title.split()).lower():
                matched_ids.append(game.id)
        games_list = Game.objects.filter(id__in=matched_ids)
    
    # ФИЛЬТР ПО ИГРОКАМ - ИСПРАВЛЕННАЯ ЛОГИКА
    if players_min or players_max:
        try:
            min_val = int(players_min) if players_min else 1
            max_val = int(players_max) if players_max else 20
            
            # Игра подходит если: 
            # - её минимальное количество игроков <= указанному максимуму
            # - её максимальное количество игроков >= указанному минимуму
            # Пример: пользователь хочет 3-5 игроков
            # Игра 2-6 игроков подходит: 2 <= 5 И 6 >= 3
            # Игра 3-8 игроков подходит: 3 <= 5 И 8 >= 3
            # Игра 6-8 игроков НЕ подходит: 6 <= 5 (ЛОЖЬ)
            
            games_list = games_list.filter(
                min_players__lte=max_val,  # min_players <= указанный максимум
                max_players__gte=min_val   # max_players >= указанный минимум
            )
            
            # Дополнительно: если указаны оба значения, проверяем что игра
            # подходит для всего диапазона
            if players_min and players_max:
                # Для сложных случаев можно добавить:
                # Игра должна подходить хотя бы для одного значения в диапазоне
                # Но базовая логика выше уже охватывает это
                pass
                
        except ValueError:
            pass
    
    # ФИЛЬТР ПО ВРЕМЕНИ (оставляем как было)
    if time_min:
        try:
            games_list = games_list.filter(playtime_minutes__gte=int(time_min))
        except ValueError:
            pass
    
    if time_max:
        try:
            games_list = games_list.filter(playtime_minutes__lte=int(time_max))
        except ValueError:
            pass
    
    # ФИЛЬТР ПО СЛОЖНОСТИ (оставляем как было)
    if difficulty:
        try:
            games_list = games_list.filter(difficulty=int(difficulty))
        except ValueError:
            pass
    
    # Сортировка
    games_list = games_list.order_by('title')
    
    # Отладочная информация
    print(f"Найдено игр после фильтров: {games_list.count()}")
    if games_list.count() < 10:
        for game in games_list:
            print(f"  - {game.title}: {game.min_players}-{game.max_players} игроков")
    
    # Пагинация
    paginator = Paginator(games_list, 12)
    
    try:
        games = paginator.page(page)
    except PageNotAnInteger:
        games = paginator.page(1)
    except EmptyPage:
        games = paginator.page(paginator.num_pages)
    
    # Контекст
    context = {
        'games': games,
        'query': query,
        'players_min': players_min,
        'players_max': players_max,
        'time_min': time_min,
        'time_max': time_max,
        'difficulty': difficulty,
        'has_filters': any([players_min, players_max, time_min, time_max, difficulty]),
    }
    
    return render(request, 'index.html', context)
def autocomplete(request):
    """
    Простой и надежный автодополнение
    """
    term = request.GET.get('term', '').strip().lower()
    
    print("=" * 50)
    print(f"AUTOCOMPLETE DEBUG: Получен термин '{term}'")
    
    if len(term) < 2:
        return JsonResponse([], safe=False)
    
    # РУЧНОЙ поиск
    all_games = Game.objects.all()
    matches = []
    
    for game in all_games:
        # Убираем переносы строк из названия
        clean_title = ' '.join(game.title.split()).lower()
        clean_term = ' '.join(term.split()).lower()
        
        if clean_term in clean_title:
            matches.append(game)
            print(f"  Совпадение: '{game.title}' -> очищено: '{clean_title}'")
        
        if len(matches) >= 10:
            break
    
    print(f"Всего совпадений: {len(matches)}")
    
    results = []
    for game in matches:
        results.append({
            'id': game.id,
            'label': game.title.replace('\n', ' ').replace('\r', ''),  # убираем переносы
            'value': game.title.replace('\n', ' ').replace('\r', ''),  # убираем переносы
        })
    
    return JsonResponse(results, safe=False)
def game_detail(request, game_id):
    """
    Детальная страница игры - УПРОЩЕННАЯ ВЕРСИЯ
    """
    game = get_object_or_404(Game, id=game_id)
    
    # Пока не ищем похожие игры, просто показываем детали
    context = {
        'game': game,
        # 'similar_games': [],  # временно убрали
    }
    return render(request, 'game_detail.html', context)


def advanced_search(request):
    """
    Расширенный поиск с фильтрами
    """
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '')
    min_players = request.GET.get('min_players', '')
    max_players = request.GET.get('max_players', '')
    
    # Начинаем с всех игр
    games = Game.objects.all()
    
    # Применяем фильтры, если они указаны
    if query:
        # Поиск по названию ИЛИ описанию (используем title вместо name)
        games = games.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query)
        )
    
    if category:
        games = games.filter(categories__icontains=category)
    
    if min_players:
        try:
            games = games.filter(min_players__gte=int(min_players))
        except ValueError:
            pass
    
    if max_players:
        try:
            games = games.filter(max_players__lte=int(max_players))
        except ValueError:
            pass
    
    # Собираем уникальные категории для фильтра
    all_categories = Game.objects.values_list('categories', flat=True).distinct()
    
    context = {
        'games': games.order_by('title'),
        'query': query,
        'category': category,
        'min_players': min_players,
        'max_players': max_players,
        'all_categories': all_categories,
    }
    
    return render(request, 'advanced_search.html', context)


def search_suggestions(request):
    """
    Альтернативная версия автодополнения с более умным поиском
    """
    term = request.GET.get('term', '').strip().lower()
    
    if len(term) < 2:
        return JsonResponse([], safe=False)
    
    try:
        # 1. Сначала ищем по точному началу (регистронезависимо)
        exact_start = Game.objects.filter(title__istartswith=term)[:5]
        
        # 2. Если результатов мало, ищем по подстроке в любом месте названия
        if exact_start.count() < 5:
            contains = Game.objects.filter(title__icontains=term).exclude(
                id__in=[g.id for g in exact_start]
            )[:5 - exact_start.count()]
            results = list(exact_start) + list(contains)
        else:
            results = exact_start
        
        # Формируем ответ
        suggestions = []
        for game in results:
            # Подсвечиваем совпадение в названии (опционально)
            title_lower = game.title.lower()
            term_lower = term.lower()
            if term_lower in title_lower:
                idx = title_lower.find(term_lower)
                highlighted = (
                    game.title[:idx] +
                    '<strong>' + game.title[idx:idx+len(term)] + '</strong>' +
                    game.title[idx+len(term):]
                )
            else:
                highlighted = game.title
            
            suggestions.append({
                'id': game.id,
                'value': game.title,
                'label': highlighted,
                'name': game.title,
                'category': game.categories if hasattr(game, 'categories') else '',
            })
        
        return JsonResponse(suggestions, safe=False)
        
    except Exception as e:
        print(f"Ошибка в поиске подсказок: {e}")
        return JsonResponse([], safe=False)


# Утилитарные функции для работы с поиском

def normalize_search_term(term):
    """
    Нормализация поискового запроса:
    - Приведение к нижнему регистру
    - Удаление лишних пробелов
    """
    if not term:
        return ''
    
    normalized = term.strip().lower()
    return normalized


def get_popular_searches(limit=5):
    """
    Получение популярных поисковых запросов
    """
    popular_games = Game.objects.order_by('-views')[:limit] if hasattr(Game, 'views') else Game.objects.all()[:limit]
    return [game.title for game in popular_games]


# Если у вас есть другие поля для поиска, можно добавить эту функцию:
def multi_field_search(query):
    """
    Поиск по нескольким полям одновременно
    """
    if not query:
        return Game.objects.all()
    
    return Game.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(categories__icontains=query)
    ).distinct()
def index_with_pagination(request):
    """Тестовая версия с пагинацией"""
    query = request.GET.get('q', '').strip()
    page = request.GET.get('page', 1)
    
    if query:
        games_list = Game.objects.filter(title__icontains=query)
    else:
        games_list = Game.objects.all()
    
    games_list = games_list.order_by('title')
    
    # Пагинация
    paginator = Paginator(games_list, 12)
    
    try:
        games = paginator.page(page)
    except PageNotAnInteger:
        games = paginator.page(1)
    except EmptyPage:
        games = paginator.page(paginator.num_pages)
    
    print("=" * 50)
    print(f"Пагинация: Страница {games.number} из {paginator.num_pages}")
    print(f"Игр на странице: {len(games)}")
    
    context = {
        'games': games,
        'query': query,
    }
    return render(request, 'index.html', context)
def debug_search(request):
    """Функция для отладки поиска"""
    query = request.GET.get('q', '')
    
    # Проверяем, что приходит в запросе
    print("=" * 50)
    print(f"DEBUG SEARCH: Запрос получен")
    print(f"Raw query: {repr(request.GET.get('q', ''))}")
    print(f"Stripped: {repr(query)}")
    print(f"Length: {len(query)}")
    
    if query:
        # Тестируем разные методы поиска
        from django.db.models import Q
        
        # 1. Простой icontains
        results1 = Game.objects.filter(title__icontains=query)
        print(f"icontains найдено: {results1.count()}")
        
        # 2. Ручной поиск по всем играм
        all_games = list(Game.objects.all())
        manual_results = []
        for game in all_games:
            if query.lower() in game.title.lower():
                manual_results.append(game)
        
        print(f"Ручной поиск найдено: {len(manual_results)}")
        
        # Показываем первые 5 результатов каждого метода
        if results1:
            print("icontains результаты:")
            for i, game in enumerate(results1[:5], 1):
                print(f"  {i}. {game.title} (id: {game.id})")
        
        if manual_results:
            print("Ручной поиск результаты:")
            for i, game in enumerate(manual_results[:5], 1):
                print(f"  {i}. {game.title} (id: {game.id})")
    
    return HttpResponse(f"""
    <html>
    <body>
        <h1>Debug Search</h1>
        <p>Запрос: '{query}'</p>
        <p>Смотрите вывод в консоли Django</p>
        <a href="/">На главную</a>
    </body>
    </html>
    """)