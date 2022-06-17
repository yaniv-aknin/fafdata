from fafscrape.parse import byte_as_base64, load_replay, yield_commands, index_players

import conftest
import pytest

def test_byte_as_base64():
    assert byte_as_base64(b'\xde\xad\xbe\xef') == '3q2+7w==\n'

def test_load_replay():
    replay_path = str(conftest.testdata / 'replay.pickle.gz')
    data = load_replay(replay_path)
    assert 'json' in data

@pytest.fixture
def parsed_replay():
    replay_path = str(conftest.testdata / 'replay.pickle.gz')
    return load_replay(replay_path)

def test_index_players(parsed_replay):
    index = index_players(parsed_replay)
    assert index == {'cizei': 1, 'teolicy': 0}

def test_yield_commands(parsed_replay):
    commands = yield_commands(parsed_replay)
    cmd = next(commands)
    assert cmd['id'] == '12519949'
    assert set(cmd.keys()) == {'payload', 'offset_ms', 'player', 'type', 'id'}
    assert 'json' in cmd['payload']
    cmd = next(commands)
    assert cmd['type'] == 'resume'
    cmd = list(commands)[-1]
    assert cmd['type'] == 'message:all'
    assert cmd['payload'] == 'Oh yeah :)_'
