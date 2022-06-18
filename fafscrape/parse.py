import pickle
import json
import base64

import replay_parser.replay
import replay_parser.constants
import zlib
import zstd

TICK_SIZE_IN_MILLISECONDS = 100

from .utils import decompressed

def extract_v1(buf):
    decoded = base64.decodebytes(buf)
    decoded = decoded[4:] # skip 4 bytes of zlib stream length
    return zlib.decompress(decoded)

def extract_v2(buf):
    return zstd.decompress(buf)

def read_header_and_body(handle):
    ALL_COMMANDS = tuple(range(24))
    header = json.loads(handle.readline().decode())
    buf = handle.read()
    version = header.get('version', 1)
    if version == 1:
        extracted = extract_v1(buf)
    elif version == 2:
        extracted = extract_v2(buf)
    else:
        raise ValueError("unknown version %s" % version)
    body = replay_parser.replay.parse(extracted, store_body=True, parse_commands=ALL_COMMANDS)
    return header, body

def get_command_timeseries(body):
    "Given an iterable of raw replay commands, return higher level timestamped stream."
    offset_ms = 0
    result = []
    for atom in body:
        for player, commands in atom.items():
            for command, args in commands.items():
                if command == 'Advance':
                    offset_ms += TICK_SIZE_IN_MILLISECONDS * int(args['advance'])
                    continue
                if command in ('VerifyChecksum', 'SetCommandSource'):
                    continue
                assert 'offset_ms' not in args
                assert 'player' not in args
                args['offset_ms'] = offset_ms
                args['player'] = player
                result.append(args)
    return result

def fully_parse_replay(handle):
    header, body = read_header_and_body(handle)
    return {
        'json': header,
        'binary': body.pop('header'),
        'commands': get_command_timeseries(body.pop('body')),
        'remaining': body,
    }

def byte_as_base64(obj):
    if type(obj) is bytes:
        return base64.encodebytes(obj).decode()
    raise TypeError(obj)

def load_replay(path_to_load):
    with decompressed(path_to_load) as handle:
        if '.pickle' in path_to_load:
            return pickle.load(handle)
        if '.fafreplay' in path_to_load:
            return fully_parse_replay(handle)
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
