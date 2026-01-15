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
    # ОТЛАДКА
    print("=" * 80)
    print(f"time_min из GET: {request.GET.get('time_min')}")
    print(f"time_max из GET: {request.GET.get('time_max')}")

    print("=" * 80)
    print("DEBUG: Полные GET параметры:")
    for key, value in request.GET.items():
        print(f"  {key}: {repr(value)} (type: {type(value)})")
    print("=" * 80)
    print("DEBUG: Загружена ИСПРАВЛЕННАЯ версия index()")
    
    query = request.GET.get('q', '').strip()
    page = request.GET.get('page', 1)
    
    difficulty_list = request.GET.getlist('difficulty')
    print("=" * 50)
    print(f"DEBUG: Получены параметры сложности: {difficulty_list}")
    print(f"DEBUG: Все GET параметры: {dict(request.GET)}")

    # Параметры фильтров
    players_min = request.GET.get('players_min', '').strip()
    players_max = request.GET.get('players_max', '').strip()
    time_min = request.GET.get('time_min', '').strip()
    time_max = request.GET.get('time_max', '').strip()
    difficulty_list = request.GET.getlist('difficulty')  # список выбранных значений
    
    print(f"ФИЛЬТРЫ: игроки {players_min}-{players_max}, время {time_min}-{time_max}, сложность {difficulty_list}")
    
    # Начинаем с всех игр
    games_list = Game.objects.all()
    
    # ПРОСТОЙ ПОИСК ПО НАЗВАНИЮ
    if query:
        games_list = games_list.filter(title__icontains=query)
        print(f"После поиска '{query}': {games_list.count()} игр")
    
    # ФИЛЬТР ПО ИГРОКАМ - ИСПРАВЛЕННАЯ ЛОГИКА
    if players_min or players_max:
        try:
            if players_min:
                min_val = int(players_min)
                # Ищем игры, где максимальное количество игроков >= минимального запроса
                games_list = games_list.filter(max_players__gte=min_val)
                print(f"После фильтра игроков (min={min_val}): {games_list.count()} игр")
            
            if players_max:
                max_val = int(players_max)
                # Ищем игры, где минимальное количество игроков <= максимального запроса
                games_list = games_list.filter(min_players__lte=max_val)
                print(f"После фильтра игроков (max={max_val}): {games_list.count()} игр")
                
        except ValueError:
            print("Ошибка преобразования игроков в число")
            pass
    
      # ФИЛЬТР ПО ВРЕМЕНИ - ИСПРАВЛЕННАЯ ЛОГИКА
       # ФИЛЬТР ПО ВРЕМЕНИ - ИСПРАВЛЕННАЯ ЛОГИКА
    # ДОБАВЬТЕ ОТЛАДОЧНЫЙ ВЫВОД ПЕРВЫМ ДЕЛОМ
    print(f"DEBUG time_min={time_min}, time_max={time_max}")
     # ВРЕМЕННЫЙ ФИКС: если значение времени больше 180, но меньше 300, 
    # это может быть фронтендная ошибка
    if time_max and time_max.isdigit():
        time_max_int = int(time_max)
        if 200 <= time_max_int < 300:
            print(f"ПРЕДУПРЕЖДЕНИЕ: странное значение time_max={time_max_int}")
            # Вероятно, пользователь хотел ввести 200, но фронтенд меняет на 300
            # Здесь можно сделать логику исправления
    if time_min or time_max:
        # Обрабатываем случай, когда указаны ОБА значения (диапазон)
        if time_min and time_max:
            print(f"DEBUG: Оба значения, min={time_min}, max={time_max}")
            try:
                time_min_val = int(time_min)
                time_max_val = int(time_max)
                print(f"DEBUG: Преобразовано в int: min={time_min_val}, max={time_max_val}")
                
                if time_max_val >= 300:
                    # "300+" - ищем игры от time_min до бесконечности
                    games_list = games_list.filter(playtime__gte=time_min_val)
                    print(f"Время от {time_min_val} до 300+: {games_list.count()} игр")
                else:
                    # Нормальный диапазон
                    games_list = games_list.filter(
                        playtime__gte=time_min_val,
                        playtime__lte=time_max_val
                    )
                    print(f"Время от {time_min_val} до {time_max_val}: {games_list.count()} игр")
            except ValueError as e:
                print(f"DEBUG: Ошибка преобразования в int: {e}")
                pass
        else:
            # Обрабатываем одиночные фильтры
            print(f"DEBUG: Одиночный фильтр, min={time_min}, max={time_max}")
            
            if time_min:
                try:
                    time_min_val = int(time_min)
                    print(f"DEBUG: time_min преобразован в {time_min_val}")
                    # Если указан только минимальный порог, 
                    # ищем игры с временем >= указанного (например, "от 60 минут")
                    games_list = games_list.filter(playtime__gte=time_min_val)
                    print(f"Время ОТ {time_min_val} минут: {games_list.count()} игр")
                except ValueError as e:
                    print(f"DEBUG: Ошибка преобразования time_min: {e}")
                    pass
            
            if time_max:
                try:
                    time_max_val = int(time_max)
                    print(f"DEBUG: time_max преобразован в {time_max_val}")
                    if time_max_val >= 300:
                        # "300+" - НЕ фильтруем по максимуму вообще
                        print(f"Время ДО '300+' (максимум не ограничен)")
                    else:
                        # Если указан только максимальный порог,
                        # ищем игры с временем <= указанного (например, "до 120 минут")
                        games_list = games_list.filter(playtime__lte=time_max_val)
                        print(f"Время ДО {time_max_val} минут: {games_list.count()} игр")
                except ValueError as e:
                    print(f"DEBUG: Ошибка преобразования time_max: {e}")
                    pass
    
    # ФИЛЬТР ПО СЛОЖНОСТИ - ИСПРАВЛЕННАЯ ЛОГИКА
    print(f"ДО фильтра сложности: {games_list.count()} игр")
    print(f"Параметр difficulty из запроса: {difficulty_list}")
    
    if difficulty_list:
        try:
            # Преобразуем значения в целые числа
            difficulty_ids = []
            for d in difficulty_list:
                try:
                    difficulty_ids.append(int(d))
                except ValueError:
                    continue
            
            if difficulty_ids:
                print(f"Фильтр сложности: difficulty_rating IN {difficulty_ids}")
                games_list = games_list.filter(difficulty_rating__in=difficulty_ids)
                print(f"ПОСЛЕ фильтра сложности: {games_list.count()} игр")
                
                # Отладка: выведем первые 5 отфильтрованных игр
                for game in games_list[:5]:
                    print(f"  - '{game.title}': players={game.min_players}-{game.max_players}, time={game.playtime}, difficulty={game.difficulty_rating}")
            
        except Exception as e:
            print(f"Ошибка в фильтре сложности: {e}")
    
    # Сортировка
    games_list = games_list.order_by('title')
    
    # ОТЛАДКА: Проверим несколько игр
    print("=" * 50)
    print(f"Итоговое количество игр: {games_list.count()}")
    
    if games_list.count() > 0:
        print("Первые 10 игр после фильтрации:")
        for game in games_list[:10]:
            print(f"  - {game.title}: игроки={game.min_players}-{game.max_players}, время={game.playtime}, сложность={game.difficulty_rating}")
    else:
        print("Нет игр, соответствующих фильтрам!")
        # Покажем все игры для отладки
        all_games = Game.objects.all()[:10]
        print("Первые 10 игр в базе:")
        for game in all_games:
            print(f"  - {game.title}: игроки={game.min_players}-{game.max_players}, время={game.playtime}, сложность={game.difficulty_rating}")
    
    # Пагинация
    paginator = Paginator(games_list, 12)
    
    try:
        games = paginator.page(page)
    except PageNotAnInteger:
        games = paginator.page(1)
    except EmptyPage:
        games = paginator.page(paginator.num_pages)
    
    # Определяем, есть ли активные фильтры
    has_filters = bool(players_min or players_max or time_min or time_max or difficulty_list)
    
    # Контекст
    context = {
        'games': games,
        'query': query,
        'players_min': players_min,
        'players_max': players_max,
        'time_min': time_min,
        'time_max': time_max,
        'difficulty': ", ".join(difficulty_list) if difficulty_list else None,
        'has_filters': has_filters,
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
        Q(description__icontains=query) 
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