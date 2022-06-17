import os
import copy
from click.testing import CliRunner
import responses

import conftest
import json

from fafscrape.main import extract_from_faf_api, transform_api_dump_to_jsonl

def read_jsonl(path, num_lines):
    with open(path) as handle:
        return [json.loads(handle.readline()) for x in range(num_lines)]

def test_transform_api_dump_to_jsonl_game():
    dump_path = conftest.testdata / 'games.json'
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.mkdir('output')
        result = runner.invoke(transform_api_dump_to_jsonl, [str(dump_path), 'output'])
        assert result.exit_code == 0
        xformed, = read_jsonl('output/xformed.jsonl', 1)
        assert xformed['id'] == '14395974'
        assert xformed['mapVersion.mapVersion.id'] == '18852'

def test_transform_api_dump_to_jsonl_game_deduped():
    dump_path = conftest.testdata / 'games.json'
    games = json.load(open(dump_path))
    games['data'].insert(1, copy.deepcopy(games['data'][0]))
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.mkdir('output')
        json.dump(games, open('games_duplicate.json', 'w'))
        result = runner.invoke(transform_api_dump_to_jsonl, ['games_duplicate.json', 'output'])
        assert result.exit_code == 0
        g1, g2, = read_jsonl('output/xformed.jsonl', 2)
        assert g1['id'] != g2['id']
    with runner.isolated_filesystem():
        os.mkdir('output')
        json.dump(games, open('games_duplicate.json', 'w'))
        result = runner.invoke(transform_api_dump_to_jsonl, ['--dedup-on-field', '', 'games_duplicate.json', 'output'])
        assert result.exit_code == 0
        g1, g2, = read_jsonl('output/xformed.jsonl', 2)
        assert g1['id'] == g2['id']

def test_transform_api_dump_to_jsonl_game_gzipped():
    dump_path = conftest.testdata / 'games.json'
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.mkdir('output')
        os.system(f'cp {dump_path} . && gzip games.json')
        result = runner.invoke(transform_api_dump_to_jsonl, ['games.json.gz', 'output'])
        assert result.exit_code == 0

def test_transform_api_dump_to_jsonl_game_partitioned():
    dump_path = conftest.testdata / 'games.json'
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.mkdir('output')
        result = runner.invoke(transform_api_dump_to_jsonl, ['--partition-strategy', 'year_month', str(dump_path), 'output'])
        assert result.exit_code == 0
        xformed, = read_jsonl('output/dt=2012-01-01/2012-12-01.jsonl', 1)
        assert xformed['id'] == '459322'

def test_transform_api_dump_to_jsonl_player():
    dump_path = conftest.testdata / 'players.json'
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.mkdir('output')
        result = runner.invoke(transform_api_dump_to_jsonl, [str(dump_path), 'output'])
        assert result.exit_code == 0
        xformed, = read_jsonl('output/xformed.jsonl', 1)
        assert xformed['id'] == '368434'

@responses.activate
def test_extract_from_faf_api(games_json):
    url = ('https://api.faforever.com/data/game?page%5Bsize%5D=10&page%5Bnumber%5D=1&page%5Btotals%5D=&'
           'filter=startTime%3Dge%3D1970-01-01T00%3A00%3A00Z%3BstartTime%3Dle%3D1970-01-01T00%3A00%3A00Z&sort=startTime')
    responses.add(method='GET', url=url, json=games_json)
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.mkdir('output')
        result = runner.invoke(extract_from_faf_api, ['output', 'game', '--start-date=1970-01-01', '--end-date=1970-01-01', '--max-pages=1'])
        assert result.exit_code == 0
        assert set(os.listdir('output')) == {'game.metadata.json', 'game0001.json'}

@responses.activate
def test_extract_from_faf_api_date_field(games_json):
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.mkdir('output')
        result = runner.invoke(extract_from_faf_api, ['output', 'foo', '--start-date=1970-01-01', '--end-date=1970-01-01', '--max-pages=1'])
        # should fail because the unknown entity 'foo' requires setting --date-field
        assert result.exit_code == 2
        url = ('https://api.faforever.com/data/foo?page%5Bsize%5D=10&page%5Bnumber%5D=1&page%5Btotals%5D=&'
               'filter=bar%3Dge%3D1970-01-01T00%3A00%3A00Z%3Bbar%3Dle%3D1970-01-01T00%3A00%3A00Z&sort=bar')
        responses.add(method='GET', url=url, json=games_json)
        result = runner.invoke(extract_from_faf_api, ['output', 'foo', '--start-date=1970-01-01', '--end-date=1970-01-01', '--max-pages=1', '--date-field=bar'])
        # now succeeds because --date-field is specified
        assert result.exit_code == 0
