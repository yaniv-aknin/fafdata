import pytest
import json

import testutils
from fafscrape.transform import index_inclusions

def test_index_inclusions(api_dump):
    inclusions = index_inclusions(api_dump['included'])
    assert 'gamePlayerStats' in inclusions
    assert 'player' in inclusions
    assert '28030408' in inclusions['gamePlayerStats']

@pytest.fixture
def api_dump():
    replay = testutils.testdata / 'dump.json'
    with open(replay) as handle:
        return json.load(handle)
