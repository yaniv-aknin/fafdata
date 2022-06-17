import py
import pytest
import json

testdata = py.path.local(__file__).dirpath() / 'testdata'

def load_json(name):
    with open(testdata / name) as handle:
        return json.load(handle)

@pytest.fixture
def games_json():
    return load_json('games.json')

@pytest.fixture
def players_json():
    return load_json('players.json')

@pytest.fixture
def replay_pickle():
    return testdata / 'replay.pickle.gz'
