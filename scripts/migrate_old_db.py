from speedrun_db.models import Game, Category, Run
from django.contrib.auth.models import User
import json
from speedrun_db.func import convert_time

runs_file = json.load(open("runs.json"))

user = User.objects.get(id=1)
id_counter = 2

for run in runs_file:
    game_id = run['game']
    if game_id == 9:
        game_id = 12
    elif game_id == 10:
        game_id = 9
    elif game_id == 11:
        game_id = 10
    elif game_id == 12:
        game_id = 11
    
    category_id = run['category']
    if category_id == 1:
        category_id = 2
    elif category_id == 2:
        category_id = 1
    
    run_obj = Run(url_id=run['url_id'], user=user, id=id_counter, date=run['date'])
    id_counter += 1

    if run['players']:
        run_obj.players = run['players']
    if run['platform']:
        run_obj.platform = run['platform']
    if run['video']:
        run_obj.video = run['video']
    if run['subcategory']:
        run_obj.subcategory = run['subcategory']
    if run['demos']:
        run_obj.demos = run['demos']
    if run['splits']:
        run_obj.splits = run['splits']
    
    game = Game.objects.get(id=game_id)
    category = Category.objects.get(id=category_id)
    
    run_obj.game = game
    run_obj.category = category

    run_obj.time = convert_time(run['time'])

    run_obj.save()
