import os
import pickle
import copy
from click.testing import CliRunner
import responses

import conftest
import json
import contextlib

from fafdata.main import extract_from_faf_api, transform_api_dump_to_jsonl, parse_replays_to_pickle, dump_replay_commands_to_jsonl
from fafdata.utils import decompressed

def read_jsonl(path, num_lines):
    with decompressed(path) as handle:
        return [json.loads(handle.readline()) for x in range(num_lines)]

@contextlib.contextmanager
def isolated_file(filename=None, pre_cmd=None):
    path = str(conftest.testdata / filename) if filename else '/dev/null'
    runner = CliRunner()
    with runner.isolated_filesystem():
        if pre_cmd:
            os.system(pre_cmd.format(path=path))
        yield runner, path

def test_parse_replays_to_pickle():
    with isolated_file('replay.v2.fafreplay', 'cp {path} .') as (runner, path):
        result = runner.invoke(parse_replays_to_pickle, ['./replay.v2.fafreplay'])
        assert result.exit_code == 0
        with decompressed('./replay.v2.pickle.zstd') as handle:
            data = pickle.load(handle)
            assert 'json' in data

def test_parse_replays_to_pickle_errors():
    dd_cmd = 'dd if=/dev/urandom of=invalid.fafreplay bs=1k count=16'
    with isolated_file('replay.v2.fafreplay', dd_cmd) as (runner, path):
        result = runner.invoke(parse_replays_to_pickle, ['./invalid.fafreplay', '--no-ignore-errors'])
        assert result.exit_code == 1
        result = runner.invoke(parse_replays_to_pickle, ['./invalid.fafreplay', '--ignore-errors'])
        assert result.exit_code == 0

def test_dump_replay_commands_to_jsonl():
    with isolated_file('replay.v2.fafreplay', 'cp {path} .') as (runner, path):
        result = runner.invoke(dump_replay_commands_to_jsonl, ['out.jsonl', './replay.v2.fafreplay'])
        assert result.exit_code == 0
        assert read_jsonl('out.jsonl', 1)[0]['id'] == '12519949'

def test_dump_replay_commands_to_jsonl_regex():
    with isolated_file('replay.v2.fafreplay', 'cp {path} .') as (runner, path):
        result = runner.invoke(dump_replay_commands_to_jsonl, ['out.jsonl', './replay.v2.fafreplay', '--regex', 'type/message'])
        assert result.exit_code == 0
        assert read_jsonl('out.jsonl', 1)[0]['type'] == 'message:notify'

def test_dump_replay_commands_to_jsonl_jsonpath():
    with isolated_file('replay.v2.fafreplay', 'cp {path} .') as (runner, path):
        result = runner.invoke(dump_replay_commands_to_jsonl, ['out.jsonl', './replay.v2.fafreplay', '--jsonpath', 'foo/json.uid'])
        assert result.exit_code == 0
        assert json.loads(read_jsonl('out.jsonl', 1)[0]['payload']) == {"foo": [12519949]}

def test_dump_replay_commands_to_jsonl_jsonpath_single_value():
    with isolated_file('replay.v2.fafreplay', 'cp {path} .') as (runner, path):
        result = runner.invoke(dump_replay_commands_to_jsonl, [
            'out.jsonl', './replay.v2.fafreplay', '--jsonpath', 'foo@/json.uid', '--regex', 'type/metadata'])
        assert result.exit_code == 0
        assert json.loads(read_jsonl('out.jsonl', 1)[0]['payload']) == {"foo": 12519949}

def test_dump_replay_commands_to_jsonl_compressed():
    with isolated_file('replay.v2.fafreplay', 'cp {path} .') as (runner, path):
        result = runner.invoke(dump_replay_commands_to_jsonl, ['out.jsonl.gz', './replay.v2.fafreplay'])
        assert result.exit_code == 0
        assert read_jsonl('out.jsonl.gz', 1)[0]['id'] == '12519949'
        GZ_MAGIC = b'\x1f\x8b'
        assert open('out.jsonl.gz', 'rb').read(2) == GZ_MAGIC

def test_dump_replay_commands_to_jsonl_directory():
    with isolated_file('replay.v2.fafreplay', 'mkdir foo ; cp {path} foo') as (runner, path):
        result = runner.invoke(dump_replay_commands_to_jsonl, ['out.jsonl', 'foo'])
        assert result.exit_code == 0
        assert read_jsonl('out.jsonl', 1)[0]['id'] == '12519949'

def test_transform_api_dump_to_jsonl_game():
    with isolated_file('games.json') as (runner, path):
        result = runner.invoke(transform_api_dump_to_jsonl, ['out.jsonl', path])
        assert result.exit_code == 0
        xformed, = read_jsonl('out.jsonl', 1)
        assert xformed['id'] == '14395974'
        assert xformed['mapVersion_mapVersion_id'] == '18852'

def test_transform_api_dump_to_jsonl_game_deduped():
    with isolated_file('games.json') as (runner, path):
        games = json.load(open(path))
        games['data'].insert(1, copy.deepcopy(games['data'][0]))
        json.dump(games, open('games_duplicate.json', 'w'))
        result = runner.invoke(transform_api_dump_to_jsonl, ['out.jsonl', 'games_duplicate.json'])
        assert result.exit_code == 0
        g1, g2, = read_jsonl('out.jsonl', 2)
        assert g1['id'] != g2['id']
    with runner.isolated_filesystem():
        json.dump(games, open('games_duplicate.json', 'w'))
        result = runner.invoke(transform_api_dump_to_jsonl, ['out.jsonl', '--dedup-on-field', '', 'games_duplicate.json'])
        assert result.exit_code == 0
        g1, g2, = read_jsonl('out.jsonl', 2)
        assert g1['id'] == g2['id']

def test_transform_api_dump_to_jsonl_game_gzipped():
    with isolated_file('games.json') as (runner, path):
        os.system(f'cp {path} . && gzip games.json')
        result = runner.invoke(transform_api_dump_to_jsonl, ['out.jsonl', 'games.json.gz'])
        assert result.exit_code == 0

def test_transform_api_dump_to_jsonl_game_partitioned():
    with isolated_file('games.json') as (runner, path):
        result = runner.invoke(transform_api_dump_to_jsonl, ['--partition-strategy', 'year_month', 'output', path])
        assert result.exit_code == 0
        xformed, = read_jsonl('output/dt=2012-01-01/2012-12-01.jsonl', 1)
        assert xformed['id'] == '459322'

def test_transform_api_dump_to_jsonl_player():
    with isolated_file('players.json') as (runner, path):
        result = runner.invoke(transform_api_dump_to_jsonl, ['out.jsonl', path])
        assert result.exit_code == 0
        xformed, = read_jsonl('out.jsonl', 1)
        assert xformed['id'] == '368434'

@responses.activate
def test_extract_from_faf_api(games_json):
    url = ('https://api.faforever.com/data/game?page%5Bsize%5D=10&page%5Bnumber%5D=1&page%5Btotals%5D=&'
           'filter=startTime%3Dge%3D1970-01-01T00%3A00%3A00Z%3BstartTime%3Dle%3D1970-01-01T00%3A00%3A00Z&sort=startTime')
    responses.add(method='GET', url=url, json=games_json)
    with isolated_file(pre_cmd='mkdir output') as (runner, path):
        result = runner.invoke(extract_from_faf_api, ['output', 'game', '--start-date=1970-01-01', '--end-date=1970-01-01', '--max-pages=1'])
        assert result.exit_code == 0
        assert set(os.listdir('output')) == {'metadata.game.json', 'game0001.json'}

@responses.activate
def test_extract_from_faf_api_date_field(games_json):
    with isolated_file(pre_cmd='mkdir output') as (runner, path):
        result = runner.invoke(extract_from_faf_api, ['output', 'foo', '--start-date=1970-01-01', '--end-date=1970-01-01', '--max-pages=1'])
        # should fail because the unknown entity 'foo' requires setting --date-field
        assert result.exit_code == 2
        url = ('https://api.faforever.com/data/foo?page%5Bsize%5D=10&page%5Bnumber%5D=1&page%5Btotals%5D=&'
               'filter=bar%3Dge%3D1970-01-01T00%3A00%3A00Z%3Bbar%3Dle%3D1970-01-01T00%3A00%3A00Z&sort=bar')
        responses.add(method='GET', url=url, json=games_json)
        result = runner.invoke(extract_from_faf_api, ['output', 'foo', '--start-date=1970-01-01', '--end-date=1970-01-01', '--max-pages=1', '--date-field=bar'])
        # now succeeds because --date-field is specified
        assert result.exit_code == 0
