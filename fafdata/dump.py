import base64
import json

from .parse import TICK_SIZE_IN_MILLISECONDS

def byte_as_base64(obj):
    if type(obj) is bytes:
        return base64.encodebytes(obj).decode()
    raise TypeError(obj)

def index_players(parsed):
    player_name_to_id = {}
    for player_id, player_data in parsed['binary']['armies'].items():
        if not player_data['Human']:
            continue
        player_name_to_id[player_data['PlayerName']] = player_id 
    return player_name_to_id

def is_dropped_by_regex(doc, column_to_pattern):
    for column, pattern in column_to_pattern.items():
        if not pattern.match(doc[column]):
            return True
    return False

def extract_jsonpaths(doc, column_to_jsonpath):
    result = {}
    for column, (jsonpath, is_single) in column_to_jsonpath.items():
        matches = jsonpath.find(doc)
        if is_single:
            m, = matches
            result[column] = m.value
        else:
            result[column] = [m.value for m in matches]
    return result

def yield_commands(parsed):
    uid = str(parsed['json']['uid'])

    player_name_to_id = index_players(parsed)

    yield {'id': uid, 'type': 'metadata', 'offset_ms': None, 'player': None,
           'payload': {'json': parsed['json'], 'binary': parsed['binary']}}

    for command in parsed['commands']:
        result = {'id': uid,
                  'type': command.pop('type'),
                  'offset_ms': command.pop('offset_ms'),
                  'player': command.pop('player')}
        result['payload'] = command
        yield result

    for offset, (player, msg_type, msg) in parsed['remaining']['messages'].items():
        yield {'id': uid, 'type': f'message:{msg_type}', 'payload': msg,
               'offset_ms': offset*TICK_SIZE_IN_MILLISECONDS,
               # not sure why player name isn't always in this index;
               # I think observers might cause this, since they aren't an army
               # but leave some mark in the reply binary
               'player': player_name_to_id.get(player)}

def process_commands(parsed, filters, jsonpaths, flatten):
    for cmd in yield_commands(parsed):
        if is_dropped_by_regex(cmd, filters):
            continue
        payload = cmd.pop('payload')
        if jsonpaths:
            payload = extract_jsonpaths(payload, jsonpaths)
        if flatten:
            cmd.update(payload)
        else:
            cmd['payload'] = json.dumps(payload, default=byte_as_base64)
        yield cmd
