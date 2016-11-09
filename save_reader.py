import base64
import zlib
from slpp import slpp as lua
import os
import json
# root = '/Users/chester/Documents/Klei/DoNotStarveTogether/client_save'
# root = '/Volumes/NO NAME/helper/save/161106_180518/client_save'
# lua_exp = decompressed[7:]
# data = lua.decode(lua_exp)

def load_saveindex(root, use_cache=False):
    current = None
    if use_cache:
        current = load_cache(root)
        if current:
            return current

    s = read_file(root+'/saveindex')
    data = lua.decode(s[18:])
    if data:
        for slot in data['slots']:
            if slot.get('session_id'):
                session_dir = os.path.join(root, 'session', slot['session_id'])
                tmp = load_session(session_dir)
                if tmp:
                    ot = tmp['summary']['title']
                    tmp['summary']['title'] = '{}\t{}'.format(ot, slot['server']['name'])
                    if not current:
                        current = tmp
                    elif current['time']<tmp['time']:
                        current = tmp
    dump_cache(current, root)
    return current

def load_player_history(root):
    decode(root+'/player_history')

def load_session(session_dir):
    if not os.path.exists(session_dir):
        return
    files = []
    dirs = []
    for f in os.listdir(session_dir):
        if os.path.isfile(os.path.join(session_dir, f)):
            files.append(f)
        else:
            dirs.append(f)
    files = [f for f in files if f.isdigit()]
    files.sort()
    if len(files) == 0:
        return
    ws_path = os.path.join(session_dir, files[-1])
    world = load_world_session(ws_path)
    # players = world.get('snapshot', {}).get('players', [])
    # if len(players)==0:
    #     return
    # dirs = [f for f in dirs if f[:-1] in players]
    users = []
    for user in dirs:
        us_path = os.path.join(session_dir, user, files[-1])
        if not os.path.exists(us_path):
            return
        tmp = load_user_session(us_path)
        if tmp:
            users.append(tmp)
    summary = summary_for_session(world, users)
    return {
        'world':world,
        'users':users,
        'summary':summary,
        'time':os.path.getmtime(ws_path)
    }

def read_file(path):
    f = open(path, 'rb')
    content = f.read()
    f.close()
    return content

def write_file(content, path):
    f = open(path, 'w+')
    to_write = ''
    if isinstance(content, dict):
        to_write = json.dumps(content)
    else:
        to_write = content
    f.write(to_write)
    f.close()

def dump_cache(session, path):
    if session:
        cache_path = os.path.join(path, 'cache')
        write_file(session, cache_path)
    else:
        clear_cache(path)

def load_cache(path):
    cache_path = os.path.join(path, 'cache')
    cache = None
    if os.path.exists(cache_path):
        content = read_file(cache_path)
        try:
            cache = json.loads(content)
        except:
            pass
    return cache

def clear_cache(path):
    cache_path = os.path.join(path, 'cache')
    if os.path.exists(cache_path):
        os.remove(cache_path)

def extract_table(content):
    s = content.find('{')
    if s<0:
        return ''
    content = content[s:]
    n = 0
    for i, c in enumerate(content):
        if c == '{':
            n += 1
        elif c == '}':
            n -= 1
            if n==0:
                break
    return content[:i+1]

def decode(path):
    raw = read_file(path)
    decoded = base64.b64decode(raw[11:])
    decompressed = zlib.decompress(decoded[16:])
    return decompressed

def load_world_session(path):
    s = read_file(path)
    data = lua.decode(s[7:])
    return data

def load_user_session(path):
    s = read_file(path)
    s = extract_table(s)
    data = lua.decode(s)
    return data

def summary_for_session(world, users):
    if not world.get('world_network') or not world['world_network'].get('persistdata') or not world['world_network']['persistdata'].get('clock'):
        return {
            'days': 0,
            'title': ''
        }
    clock = world['world_network']['persistdata']['clock']
    str_day = '{} of Day {}'.format(clock['phase'], clock['cycles'])
    seasons = world['world_network']['persistdata']['seasons']
    str_season = '{} ({}/{})'.format(seasons['season'], seasons['elapseddaysinseason'], seasons['elapseddaysinseason']+seasons['remainingdaysinseason'])
    str_user = ', '.join(['{} ({}{})'.format(user['prefab'], user['age'], user['data'].get('is_ghost', False) and ', DEAD' or '') for user in users])
    line = '{}\t{}\t{}'.format(str_day, str_season, str_user)
    return {
        'days':clock['cycles'],
        'title': line
    }

# decode(root+'/client_save/player_history')
# decode(root+'/client_save/morgue')
# decode(root+'/profile')

# root = '/Users/chester/Documents/Klei/DoNotStarveTogether/client_save'
# current = load_saveindex(root)
