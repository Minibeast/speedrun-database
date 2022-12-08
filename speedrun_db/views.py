from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, Http404

from .models import Run, Game, Category

from .func import get_games_index, convert_run, is_pb, generate_comparison, get_personal_best, compare_run

def index(request):
    run_output = get_games_index(get_pb=True)
    return render(request, 'index.html', {'runs': run_output})


def get_games(request):
    games = get_games_index(display_checks=False)
    return render(request, 'games.html', {'games': games})


def get_run(request, run_id):
    run = get_object_or_404(Run, url_id=run_id)

    context = {'run': convert_run(run), 'is_pb': is_pb(run)}
    return render(request, 'run.html', context)


def get_splits(request, run_id):
    run = get_object_or_404(Run, url_id=run_id)

    if run.splits is None:
        raise PermissionDenied
    
    splits = generate_comparison(run)
    response = HttpResponse(splits, headers={
        'Content-Type': 'application/octet-stream',
        'Content-Disposition': f'attachment; filename={run.url_id}.lss'
    })
    return response


def get_game(request, game_abv):
    game = get_object_or_404(Game, abbreviation=game_abv.lower())

    obj = {
        'abv': game.abbreviation,
        'name': game.name,
        'categories': []
    }

    for category in Category.objects.filter(held_game=game).order_by('order_by'):
        best_times = get_personal_best(category)
        times = []
        for run in best_times:
            if run is not None:
                times.append(convert_run(run))
        
        obj['categories'].append({
            'order_by': category.order_by,
            'name': category.name,
            'abv':  category.abbreviation,
            'personal_best': times
        })

    return render(request, 'game.html', {'game': obj})


def get_category(request, game_abv, category_abv):
    game = get_object_or_404(Game, abbreviation=game_abv.lower())
    category = get_object_or_404(Category, held_game=game, abbreviation=category_abv.lower())

    best_times = get_personal_best(category)
    times = []
    for run in best_times:
        if run is not None:
            times.append(convert_run(run))
    
    obj = {
        'game': {
            'name': game.name,
            'abv': game.abbreviation
        },
        'category': {
            'name': category.name,
            'abv':  category.abbreviation,
            'filter': category.subcategory_filter
        },
        'personal_best': times
    }

    runs = Run.objects.filter(category=category).order_by('-date', 'time')

    list_of_pbs = []
    for x in obj['personal_best']:
        list_of_pbs.append(x['url_id'])
    if category.subcategory_filter:
        temp = {}
        for x in runs:
            if x.url_id not in list_of_pbs:
                if x.subcategory in temp:
                    temp[x.subcategory].append(convert_run(x))
                else:
                    temp.update({str(x.subcategory): []})
                    temp[x.subcategory].append(convert_run(x))
        
        obj['run_history'] = temp
    else:
        temp = []
        for x in runs:
            if x.url_id not in list_of_pbs:
                temp.append(convert_run(x))
        obj['run_history'] = temp

    return render(request, 'category.html', {'data': obj})


def category_minute_barriers(request, game_abv, category_abv):
    game = get_object_or_404(Game, abbreviation=game_abv.lower())
    category = get_object_or_404(Category, held_game=game, abbreviation=category_abv.lower())

    obj = {
        'game': {
            'name': game.name,
            'abv': game.abbreviation
        },
        'category': {
            'name': category.name,
            'abv':  category.abbreviation,
            'filter': category.subcategory_filter
        }
    }

    runs = Run.objects.filter(category=category).order_by('date', '-time')
    run_list = []
    if category.subcategory_filter:
        temp = {}
        for x in runs:
            if x.subcategory in temp:
                if x.time.minute not in temp[x.subcategory]['queried_barriers']:
                    run_list.append(x)
                    temp[x.subcategory]['queried_barriers'].append(x.time.minute)
            else:
                temp.update({str(x.subcategory): {}})
                temp[x.subcategory]['queried_barriers'] = [x.time.minute]
                run_list.append(x)
    else:
        queried_barriers = []
        for x in runs:
            if x.time.minute not in queried_barriers:
                run_list.append(x)
                queried_barriers.append(x.time.minute)
    
    run_list.reverse()
    if category.subcategory_filter:
        temp = {}
        for x in run_list:
            if x.subcategory in temp:
                temp[x.subcategory].append(convert_run(x))
            else:
                temp.update({str(x.subcategory): []})
                temp[x.subcategory].append(convert_run(x))
        
        obj['run_history'] = temp
    else:
        temp = []
        for x in run_list:
            temp.append(convert_run(x))
        obj['run_history'] = temp

    return render(request, 'barriers.html', {'data': obj})


def get_pb(request, game_abv, category_abv):
    game = get_object_or_404(Game, abbreviation=game_abv.lower())
    category = get_object_or_404(Category, held_game=game, abbreviation=category_abv.lower())

    best_times = get_personal_best(category)
    if len(best_times) == 0 or best_times[0] is None:
        raise Http404
    else:
        return redirect('speedrun_db:run', run_id=best_times[0].url_id)


def make_comparison(request, run_id):
    run = get_object_or_404(Run, url_id=run_id)
    run_obj = convert_run(run)

    if run_obj['splits'] is None:
        raise Http404
    
    runs = Run.objects.filter(category=run.category).order_by('-date', 'time')
    if run.category.subcategory_filter:
        temp = {}
        for x in runs:
            if x.url_id != run.url_id and x.splits:
                if x.subcategory in temp:
                    temp[x.subcategory].append(convert_run(x))
                else:
                    temp.update({str(x.subcategory): []})
                    temp[x.subcategory].append(convert_run(x))
        
        run_history = temp
    else:
        temp = []
        for x in runs:
            if x.url_id != run.url_id and x.splits:
                temp.append(convert_run(x))
        run_history = temp
    
    context = {'game': run.game, 'category': run.category, 'run': convert_run(run), 'run_history': run_history, 'category_filter': run.category.subcategory_filter}
    return render(request, 'make_comparison.html', context)


def comparison(request, run1_id, run2_id):
    run1 = get_object_or_404(Run, url_id=run1_id)
    run2 = get_object_or_404(Run, url_id=run2_id)

    comparison = compare_run(run1, run2)
    if not comparison:
        # TODO: Replace with proper HTTP error
        raise Http404

    runs = [convert_run(run1), convert_run(run2)]
    load_yt_js = False
    for run in runs:
        if run['yt_player_embed']['exists']:
            load_yt_js = True
            break
    
    context = {
        'runs': [convert_run(run1), convert_run(run2)],
        'splits_comparison': comparison,
        'load_yt_js': load_yt_js
    }

    return render(request, 'compare_run.html', context)
