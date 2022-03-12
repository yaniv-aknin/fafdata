import pytest
import json

import testutils
from fafscrape.transform import index_inclusions, transform_game

def test_index_inclusions(api_dump):
    inclusions = index_inclusions(api_dump['included'])
    assert 'gamePlayerStats' in inclusions
    assert 'player' in inclusions
    assert '28030408' in inclusions['gamePlayerStats']

def test_transform_game(api_dump):
    inclusions = index_inclusions(api_dump['included'])
    raw_game = api_dump['data'][0]
    xform_game = transform_game(raw_game, inclusions)
    assert xform_game['name'] == 'GreatGrapes Vs Pistachios'
    assert xform_game['featuredModId'] == '6'
    assert len(xform_game['playerStats']) == 2
    assert xform_game['playerStats'][0]['playerId'] == '405147'

def test_transform_games(api_dump):
    inclusions = index_inclusions(api_dump['included'])
    for raw_game in api_dump['data']:
        xform_game = transform_game(raw_game, inclusions)
        assert 'id' in xform_game

@pytest.fixture
def api_dump():
    replay = testutils.testdata / 'dump.json'
    with open(replay) as handle:
        return json.load(handle)
