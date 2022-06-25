from fafdata.parse import load_replay

import conftest

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
