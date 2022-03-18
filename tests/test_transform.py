from fafscrape.transform import generic_transform

def test_transform_game(games_json):
    raw_game = games_json['data'][0]
    xform_game = generic_transform(raw_game)
    assert xform_game['name'] == 'GreatGrapes Vs Pistachios'
    assert xform_game['endTime'] == '2021-04-28 04:39:55'
    assert xform_game['featuredMod.featuredMod.id'] == '6'
    assert len(xform_game['playerStats.gamePlayerStats.id']) == 2
    assert xform_game['playerStats.gamePlayerStats.id'][0] == '28030408'

def test_transform_many_games(games_json):
    for raw_game in games_json['data']:
        xform_game = generic_transform(raw_game)
        assert 'name' in xform_game
