import pickle
import base64
import json

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

def load_replay(path_to_load):
    with decompressed(path_to_load) as handle:
        if '.pickle' in path_to_load:
            return pickle.load(handle)
        if '.fafreplay' in path_to_load:
            return fully_parse_replay(handle)
    raise NotImplementedError("can't load this filetype")
