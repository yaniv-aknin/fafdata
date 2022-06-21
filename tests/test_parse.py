from fafdata.parse import byte_as_base64, load_replay, yield_commands, index_players

import conftest
import pytest

def test_byte_as_base64():
    assert byte_as_base64(b'\xde\xad\xbe\xef') == '3q2+7w==\n'

def test_load_replay():
    replay_path = str(conftest.testdata / 'replay.pickle.gz')
    from_pickle = load_replay(replay_path)
    assert 'json' in from_pickle
    replay_path = str(conftest.testdata / 'replay.v2.fafreplay')
    from_replay = load_replay(replay_path)
    assert 'json' in from_replay
    # this line might end up being brittle; we're essentially checking the parser
    # and associated command-offseting logic doesn't change. I think the brittleness
    # is worth it because there's a lot of legacy being carried around to ensure
    # compatibility with previously parsed and cached replays
    assert from_pickle == from_replay
    replay_path = str(conftest.testdata / 'replay.v1.fafreplay')
    old_replay = load_replay(replay_path)
    assert old_replay['json']['uid'] == 460

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
