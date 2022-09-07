import contextlib
import subprocess
import datetime
import pathlib

def parse_date(date_string):
    if date_string.startswith('-'):
        days = int(date_string[1:])
        return datetime.date.today() - datetime.timedelta(days=days)
    return datetime.datetime.strptime(date_string, '%Y-%m-%d').date()

def format_faf_date(date):
    "Given a %Y-%m-%d day, emit the datetime format used by FAF (RFC 3339), at midnight UTC"
    return datetime.datetime.combine(date, datetime.time()).isoformat(timespec='seconds') + 'Z'

def format_bigquery_datetime(datetime_obj):
    "Given a datetime obj, emit the datetime format used by BigQuery JSON imports (assumes UTC)"
    return datetime_obj.strftime('%Y-%m-%d %H:%M:%S')

def faf_to_bigquery_datetime(datetime_string):
    if datetime_string is None:
        return None
    assert datetime_string[-1] == 'Z'
    return format_bigquery_datetime(datetime.datetime.fromisoformat(datetime_string[:-1]))

def is_dir_populated(pathlib_path):
    return any(pathlib_path.iterdir())

@contextlib.contextmanager
def decompressed(path):
    if path.endswith('gz'):
        with subprocess.Popen(['zcat', path], stdout=subprocess.PIPE) as proc:
            yield proc.stdout
    elif path.endswith('zstd') or path.endswith('zst'):
        with subprocess.Popen(['zstdcat', path], stdout=subprocess.PIPE) as proc:
            yield proc.stdout
    else:
        with open(path, 'rb') as handle:
            yield handle

@contextlib.contextmanager
def compressed(path):
    with open(path, 'wb') as handle:
        if path.endswith('.gz'):
            with subprocess.Popen('gzip', stdin=subprocess.PIPE, stdout=handle) as proc:
                yield proc.stdin
        elif path.endswith('zstd') or path.endswith('zst'):
            with subprocess.Popen('zstd', stdin=subprocess.PIPE, stdout=handle) as proc:
                yield proc.stdin
        else:
            yield handle
