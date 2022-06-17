import os
from fafscrape.transform import generic_transform, index_inclusions, PartitionedWriter

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
    assert xform_game['featuredMod_featuredMod_id'] == '6'
    assert len(xform_game['playerStats_gamePlayerStats_id']) == 2
    assert xform_game['playerStats_gamePlayerStats_id'][0] == '28030408'

def test_transform_many_games(games_json):
    for raw_game in games_json['data']:
        xform_game = generic_transform(raw_game, {})
        assert 'name' in xform_game

def test_transform_game_with_embedded_inclusions(games_json):
    index = index_inclusions(games_json, ['player'])
    raw_game = games_json['data'][0]
    xform_game = generic_transform(raw_game, index)
    assert xform_game['name'] == 'GreatGrapes Vs Pistachios'
    assert xform_game['host_player']['login'] == 'GreatGrapes'

    index = index_inclusions(games_json, ['gamePlayerStats'])
    raw_game = games_json['data'][0]
    xform_game = generic_transform(raw_game, index)
    assert xform_game['name'] == 'GreatGrapes Vs Pistachios'
    assert xform_game['host_player_id'] == '405147'
    assert xform_game['playerStats_gamePlayerStats'][0]['faction'] == 4
    assert xform_game['playerStats_gamePlayerStats'][0]['scoreTime'] == '2021-04-28 04:39:55'
    assert xform_game['playerStats_gamePlayerStats'][0]['player_player_id'] == '405147'

def test_partitioned_writer_one_path(tmp_path):
    with PartitionedWriter(lambda x: tmp_path / "x.out") as pw:
        pw.write({"foo": "bar"})
        pw.write({"baz": "qux"})
    with open(tmp_path / "x.out") as handle:
        assert handle.read() == '{"foo": "bar"}\n{"baz": "qux"}\n'

def test_partitioned_writer_encoding(tmp_path):
    with PartitionedWriter(lambda x: tmp_path / "x.out", encoder=lambda x: x.upper(), write_suffix='X') as pw:
        pw.write('foo')
        pw.write('bar')
    with open(tmp_path / "x.out") as handle:
        assert handle.read() == 'FOOXBARX'

def test_partitioned_writer_two_paths(tmp_path):
    with PartitionedWriter(lambda x: tmp_path / f"{x['foo']}") as pw:
        pw.write({"foo": "bar"})
        pw.write({"foo": "baz"})
    with open(tmp_path / "bar") as handle:
        assert handle.read() == '{"foo": "bar"}\n'
    with open(tmp_path / "baz") as handle:
        assert handle.read() == '{"foo": "baz"}\n'

def test_partitioned_writer_many_paths(tmp_path):
    with PartitionedWriter(lambda x: tmp_path / f"{x['foo']}", max_file_descriptors=2) as pw:
        pw.write({"foo": "bar"})
        pw.write({"foo": "baz"})
        assert len(pw.handles) == 2
        pw.write({"foo": "qux"})
        assert len(pw.handles) == 2
    assert set(os.listdir(tmp_path)) == {'bar', 'baz', 'qux'}
