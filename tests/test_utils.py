import os
import pathlib
import datetime
from click.testing import CliRunner

import fafscrape.utils as U

def test_parse_date():
    assert U.parse_date('1970-01-01') == datetime.date(1970, 1, 1)
    assert type(U.parse_date('-1')) == datetime.date

def test_format_dates():
    assert U.format_faf_date(datetime.date(1970, 1, 1)) == '1970-01-01T00:00:00Z'
    assert U.format_bigquery_datetime(datetime.datetime(1970, 1, 2, 3, 4, 5)) == '1970-01-02 03:04:05'

def test_faf_to_bigquery_datetime():
    assert U.faf_to_bigquery_datetime(None) is None
    assert U.faf_to_bigquery_datetime('1970-01-01T00:00:00Z') == '1970-01-01 00:00:00'

def test_is_dir_populated():
    path = pathlib.Path('.')
    runner = CliRunner()
    with runner.isolated_filesystem():
        assert not U.is_dir_populated(path)
        (path / 'foo').touch()
        assert U.is_dir_populated(path)

def test_decompressed():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('foo', 'w') as handle:
            handle.write('bar')
        with U.decompressed('foo') as handle:
            assert handle.read() == b'bar'
        os.system('gzip foo')
        with U.decompressed('foo.gz') as handle:
            assert handle.read() == b'bar'
