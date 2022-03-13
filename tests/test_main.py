import os
from click.testing import CliRunner
import responses

import testutils
import pytest
import json

from fafscrape.main import extract_from_faf_api, transform_api_dump_to_jsonl

def read_jsonl(path, num_lines):
    with open(path) as handle:
        return [json.loads(handle.readline()) for x in range(num_lines)]

def test_transform_api_dump_to_jsonl_game():
    dump_path = testutils.testdata / 'dump.json'
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(transform_api_dump_to_jsonl, [str(dump_path), 'xformed.jsonl'])
        assert result.exit_code == 0
        xformed, = read_jsonl('xformed.jsonl', 1)
        assert xformed['id'] == '14395974'
        assert xformed['mapVersionId'] == '18852'

def test_transform_api_dump_to_jsonl_player():
    dump_path = testutils.testdata / 'players.json'
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(transform_api_dump_to_jsonl, [str(dump_path), 'xformed.jsonl'])
        assert result.exit_code == 0
        xformed, = read_jsonl('xformed.jsonl', 1)
        assert xformed['id'] == '368434'

@responses.activate
def test_extract_from_faf_api(api_dump):
    url = ('https://api.faforever.com/data/game?page%5Bsize%5D=10&page%5Bnumber%5D=1&page%5Btotals%5D=&'
           'filter=endTime%3Dge%3D1970-01-01T00%3A00%3A00Z%3BendTime%3Dle%3D1970-01-01T00%3A00%3A00Z&sort=endTime')
    responses.add(method='GET', url=url, json=api_dump)
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.mkdir('output')
        result = runner.invoke(extract_from_faf_api, ['output', 'game', '--start-date=1970-01-01', '--end-date=1970-01-01', '--max-pages=1'])
        assert result.exit_code == 0
        assert os.listdir('output') == ['game0001.json']

@responses.activate
def test_extract_from_faf_api_date_field(api_dump):
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.mkdir('output')
        result = runner.invoke(extract_from_faf_api, ['output', 'foo', '--start-date=1970-01-01', '--end-date=1970-01-01', '--max-pages=1'])
        # should fail because the unknown entity 'foo' requires setting --date-field
        assert result.exit_code == 2
        url = ('https://api.faforever.com/data/foo?page%5Bsize%5D=10&page%5Bnumber%5D=1&page%5Btotals%5D=&'
               'filter=bar%3Dge%3D1970-01-01T00%3A00%3A00Z%3Bbar%3Dle%3D1970-01-01T00%3A00%3A00Z&sort=bar')
        responses.add(method='GET', url=url, json=api_dump)
        result = runner.invoke(extract_from_faf_api, ['output', 'foo', '--start-date=1970-01-01', '--end-date=1970-01-01', '--max-pages=1', '--date-field=bar'])
        # now succeeds because --date-field is specified
        assert result.exit_code == 0

@pytest.fixture
def api_dump():
    replay = testutils.testdata / 'dump.json'
    with open(replay) as handle:
        return json.load(handle)
