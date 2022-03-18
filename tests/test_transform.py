import pytest
import json

from fafscrape.transform import index_inclusions, transform_game

def test_index_inclusions(games_json):
    inclusions = index_inclusions(games_json['included'])
    assert 'gamePlayerStats' in inclusions
    assert 'player' in inclusions
    assert '28030408' in inclusions['gamePlayerStats']

def test_transform_game(games_json):
    inclusions = index_inclusions(games_json['included'])
    raw_game = games_json['data'][0]
    xform_game = transform_game(raw_game, inclusions)
    assert xform_game['name'] == 'GreatGrapes Vs Pistachios'
    assert xform_game['featuredModId'] == '6'
    assert len(xform_game['playerStats']) == 2
    assert xform_game['playerStats'][0]['playerId'] == '405147'

def test_transform_many_games(games_json):
    inclusions = index_inclusions(games_json['included'])
    for raw_game in games_json['data']:
        xform_game = transform_game(raw_game, inclusions)
        assert 'id' in xform_game

def test_transform_null_endtime(games_json):
    inclusions = index_inclusions(games_json['included'])
    raw_game = games_json['data'][-2] # kinda ugly to reference offset like this
    xform_game = transform_game(raw_game, inclusions)
    assert xform_game['endTime'] is None
