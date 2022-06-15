from fafscrape.transform import generic_transform, index_inclusions

def test_index_inclusions_empty(games_json):
    index = index_inclusions(games_json, ())
    assert not index

def test_index_inclusions(games_json):
    index = index_inclusions(games_json, ['player'])
    assert index['player']['248159']['login'] == 'Pistachios'

def test_transform_game(games_json):
    raw_game = games_json['data'][0]
    xform_game = generic_transform(raw_game, {})
    assert xform_game['name'] == 'GreatGrapes Vs Pistachios'
    assert xform_game['endTime'] == '2021-04-28 04:39:55'
    assert xform_game['featuredMod.featuredMod.id'] == '6'
    assert len(xform_game['playerStats.gamePlayerStats.id']) == 2
    assert xform_game['playerStats.gamePlayerStats.id'][0] == '28030408'

def test_transform_many_games(games_json):
    for raw_game in games_json['data']:
        xform_game = generic_transform(raw_game, {})
        assert 'name' in xform_game

def test_transform_game_with_embedded_inclusions(games_json):
    index = index_inclusions(games_json, ['player'])
    raw_game = games_json['data'][0]
    xform_game = generic_transform(raw_game, index)
    assert xform_game['name'] == 'GreatGrapes Vs Pistachios'
    assert xform_game['host.player']['login'] == 'GreatGrapes'

    index = index_inclusions(games_json, ['gamePlayerStats'])
    raw_game = games_json['data'][0]
    xform_game = generic_transform(raw_game, index)
    assert xform_game['name'] == 'GreatGrapes Vs Pistachios'
    assert xform_game['host.player.id'] == '405147'
    assert xform_game['playerStats.gamePlayerStats'][0]['faction'] == 4
    assert xform_game['playerStats.gamePlayerStats'][0]['scoreTime'] == '2021-04-28 04:39:55'
