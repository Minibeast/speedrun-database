import datetime
from .models import Run, Category, Game
import os

PARENT_URL = os.environ.get("PARENT_URL")

def pb_rules(run : Run) -> bool:
    if run.game.abbreviation == "sm64":
        runs = Run.objects.filter(category=run.category)
        n64_found = False
        for x in runs:
            if x.subcategory == "N64":
                n64_found = True
        if not n64_found:
            return True
        return "N64" in run.subcategory
    else:
        return True


def date_format(year : int, month : int, day : int) -> datetime.datetime:
    month = str(month)
    month = month.zfill(2)
    day = str(day)
    day = day.zfill(2)
    return datetime.datetime.fromisoformat(f"{year}-{month}-{day}")


def compare_time(time_1 : datetime.time, time_2 : datetime.time) -> bool:
    time_1_s = int(time_1.hour) * 3600
    time_2_s = int(time_2.hour) * 3600
    time_1_s += int(time_1.minute) * 60
    time_2_s += int(time_2.minute) * 60
    time_1_s += int(time_1.second)
    time_2_s += int(time_2.second)
    time_1_s += float(f".{time_1.microsecond}")
    time_2_s += float(f".{time_2.microsecond}")
    return time_1_s < time_2_s


def get_embed_url(url : str) -> dict:
    if url is None:
        return None
    if "youtube" in url or "youtu.be" in url:
        video_id = url[-11:]
        return {'url': f"https://www.youtube-nocookie.com/embed/{video_id}", 'type': 'youtube', 'id': video_id}
    elif "twitch" in url:
        video_id = url.split("/")[4]
        return {'url': f"https://player.twitch.tv/?video={video_id}&parent={PARENT_URL}&autoplay=false", 'type': 'twitch', 'id': video_id}
    else:
        return url


def get_personal_best(category : Category) -> list:
    if category.is_multiplayer:
        times = []
        for z in Run.objects.filter(category=category).order_by("time"):
            found = False
            for a in times:
                if a['players'] == z.players:
                    found = True
                    if compare_time(z.time, a['run'].time) and pb_rules(z):
                        a['run'] = z
            if not found:
                times.append({
                    'players': z.players,
                    'run': z
                })
        output = []
        for x in times:
            output.append(x['run'])
        return output
    else:
        best_time = None
        for z in Run.objects.filter(category=category):
            if best_time is None or (compare_time(z.time, best_time.time) and pb_rules(z)):
                best_time = z
        
        return [best_time]


def is_pb(run: Run) -> list:
    category = run.category
    pb_list = get_personal_best(category)
    for x in pb_list:
        if run.players == x.players:
            if run.time == x.time and pb_rules(run):
                return [True, x.url_id]
            else:
                return [False, x.url_id]
    return [False, ""]


def check_valid_change(category : Category, check : int = 1) -> bool:
    if check == 1:
        runs = Run.objects.filter(category=category, subcategory=None)
        return runs.count() == 0
    elif check == 2:
        runs = Run.objects.filter(category=category, players=None)
        return runs.count() == 0


def convert_run(run : Run) -> dict:
    if run is None:
        return None
    
    timestring = datetime.time.strftime(run.time, '%H:%M:%S')
    datestring = date_format(run.date.year, run.date.month, run.date.day)

    if run.players is None or len(run.players) == 0 or not run.category.is_multiplayer:
        players = None
    else:
        players = ""
        for x in run.players.split(","):
            players += x + ", "
        
        if len(players) > 0:
            players = players[:-2]
    
    video = []
    yt_player = {
        'exists': False,
        'video': None
    }
    if run.video:
        for x in run.video.split(" "):
            temp_video = get_embed_url(x)
            video.append(temp_video)
            if temp_video['type'] == 'youtube':
                yt_player['exists'] = True
                yt_player['video'] = temp_video
                yt_player['offset'] = run.offset
    
    return {
        'url_id': run.url_id,
        'game_abv': run.game.abbreviation,
        'game_name': run.game.name,
        'category_name': run.category.name,
        'use_game_time': run.game.use_game_time,
        'category_abv': run.category.abbreviation,
        'timestring': timestring,
        'video': video,
        'hasvideo': len(video) > 0,
        'subcategory': run.subcategory,
        'platform': run.platform,
        'date': datestring.strftime("%b %d, %Y"),
        'rssdate': datestring.strftime('%a, %d %b %Y'),
        'demos': run.demos,
        'splits': generate_preview_splits(run),
        'players': players,
        'yt_player_embed': yt_player
    }


def get_games_index(get_pb : bool = False, display_checks : bool = True) -> list:
    run_output = []
    for row in Game.objects.order_by('order_by'):
        if row.show_on_home is False and display_checks:
            continue
        name = row.name
        abv = row.abbreviation

        obj = {
            'name': name,
            'abv': abv,
            'categories': []
        }

        for y in Category.objects.filter(held_game=row).order_by('order_by'):
            if y.show_on_home is False and display_checks:
                continue

            times = []
            if get_pb:
                best_times = get_personal_best(y)
                for run in best_times:
                    if run is None:
                        continue
                    times.append(convert_run(run))

                if len(times) == 0 and display_checks:
                    continue
            
            obj['categories'].append({
                'name': y.name,
                'abv': y.abbreviation,
                'personal_best': times
            })

        run_output.append(obj)
    return run_output


def generate_preview_splits(run: Run) -> list:
    if not run.splits:
        return None

    split_lines = str(run.splits).split("|")
    data_list = []
    for x in split_lines:
        temp = []
        for y in x.split(","):
            temp.append(y)
        data_list.append(temp)
    
    splits = []
    last_seconds = 0
    total_time = datetime.datetime.combine(datetime.date.today(), datetime.time())
    for x in data_list:
        time = convert_time(x[1])
        seconds = (time.hour * 60 + time.minute) * 60 + time.second
        obj = {
            'name': x[0],
            'time': str(x[1])[:-2],
            'full_time': x[1],
            'time_obj': time,
            'seconds': seconds,
            'last_seconds': last_seconds
        }
        last_seconds = seconds

        segment_datetime = datetime.datetime.combine(datetime.date.today(), obj['time_obj']) - total_time
        obj['segment_time_obj'] = (datetime.datetime.min + segment_datetime).time()
        obj['segment_time'] = datetime.datetime.strftime((datetime.datetime.min + segment_datetime), "%H:%M:%S.%f")[:-5]
        total_time += segment_datetime

        if "." not in obj['time']:
            obj['time'] = obj['full_time']
        splits.append(obj)
    return splits


def generate_comparison(run: Run) -> str:
    if run.splits is None:
        return None

    splits = generate_preview_splits(run)
    timingmethod = "RealTime" if run.game.use_game_time else "GameTime"

    output = f"""<?xml version="1.0" encoding="UTF-8"?>
<Run version="1.7.0">
    <GameIcon />
    <GameName>{run.game.name}</GameName>
    <CategoryName>{run.category.name}</CategoryName>
    <Metadata>
        <Run id="" />
        <Platform usesEmulator="False">
        </Platform>
        <Region>
        </Region>
        <Variables />
    </Metadata>
    <Offset>00:00:00</Offset>
    <AttemptCount>0</AttemptCount>
    <AttemptHistory />
    <Segments>
    """

    for x in splits:
        output += f"""<Segment>
            <Name>{x['name']}</Name>
            <Icon />
            <SplitTimes>
            <SplitTime name="Personal Best">
                <{timingmethod}>{x['full_time'].zfill(7)}</{timingmethod}>
            </SplitTime>
            </SplitTimes>
            <BestSegmentTime />
            <SegmentHistory />
        </Segment>
        """
    output += """</Segments>
    <AutoSplitterSettings />
</Run>
    """
    return output


def convert_time(time : str) -> datetime.time:
    dt_obj = datetime.datetime.strptime(time, "%H:%M:%S.%f")
    return datetime.time(hour=dt_obj.hour, minute=dt_obj.minute, second=dt_obj.second, microsecond=dt_obj.microsecond)


def compare_run(run1 : Run, run2 : Run) -> dict:
    splits1 = generate_preview_splits(run1)
    splits2 = generate_preview_splits(run2)

    if splits1 is None or splits2 is None:
        return None

    if len(splits1) != len(splits2):
        return None

    i = 0
    while i < len(splits1):
        if splits1[i]['name'].lower() != splits2[i]['name'].lower():
            return None
        i+=1

    i = 0
    splits_db = []
    while i < len(splits1):
        splits_db.append({
            "split_info_1": splits1[i],
            "split_info_2": splits2[i],
            "is_gold": compare_time(splits1[i]['segment_time_obj'], splits2[i]['segment_time_obj'])})   
        i+=1

    return splits_db
