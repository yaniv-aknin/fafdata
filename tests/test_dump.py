from fafdata.parse import load_replay
from fafdata.dump import byte_as_base64, yield_commands, index_players

import conftest
import pytest

@pytest.fixture
def parsed_pickle():
    replay_path = str(conftest.testdata / 'replay.pickle.gz')
    return load_replay(replay_path)

def test_index_players(parsed_pickle):
    index = index_players(parsed_pickle)
    assert index == {'cizei': 1, 'teolicy': 0}

def test_yield_commands(parsed_pickle):
    commands = yield_commands(parsed_pickle)
    cmd = next(commands)
    assert cmd['id'] == '12519949'
    assert set(cmd.keys()) == {'payload', 'offset_ms', 'player', 'type', 'id'}
    assert 'json' in cmd['payload']
    cmd = next(commands)
    assert cmd['type'] == 'resume'
    cmd = list(commands)[-1]
    assert cmd['type'] == 'message:all'
    assert cmd['payload'] == 'Oh yeah :)_'

def test_byte_as_base64():
    assert byte_as_base64(b'\xde\xad\xbe\xef') == '3q2+7w==\n'
