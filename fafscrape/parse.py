import pickle
import json
import base64

TICK_SIZE_IN_MILLISECONDS = 100

from .utils import decompressed

def byte_as_base64(obj):
    if type(obj) is bytes:
        return base64.encodebytes(obj).decode()
    raise TypeError(obj)

def load_replay(path_to_load):
    with decompressed(path_to_load) as handle:
        if '.pickle' in path_to_load:
            return pickle.load(handle)
    raise NotImplementedError("can't load this filetype")

def index_players(parsed):
    player_name_to_id = {}
    for player_id, player_data in parsed['binary']['armies'].items():
        if not player_data['Human']:
            continue
        player_name_to_id[player_data['PlayerName']] = player_id 
    return player_name_to_id

def yield_commands(parsed):
    uid = str(parsed['json']['uid'])

    player_name_to_id = index_players(parsed)

    yield {'id': uid, 'type': 'metadata', 'offset_ms': None, 'player': None,
           'payload': json.dumps({'json': parsed['json'], 'binary': parsed['binary']})}

    for command in parsed['commands']:
        result = {'id': uid,
                  'type': command.pop('type'),
                  'offset_ms': command.pop('offset_ms'),
                  'player': command.pop('player')}
        result['payload'] = json.dumps(command, default=byte_as_base64)
        yield result

    for offset, (player, msg_type, msg) in parsed['remaining']['messages'].items():
        yield {'id': uid, 'type': f'message:{msg_type}', 'payload': msg,
               'offset_ms': offset*TICK_SIZE_IN_MILLISECONDS,
               # not sure why player name isn't always in this index;
               # I think observers might cause this, since they aren't an army
               # but leave some mark in the reply binary
               'player': player_name_to_id.get(player)}
