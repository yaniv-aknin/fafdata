import datetime

DEFAULT_TWO_DAYS_AGO='-2'
DEFAULT_ONE_DAY_AGO='-1'

def parse_date(date_string):
    if date_string.startswith('-'):
        days = int(date_string[1:])
        return datetime.date.today() - datetime.timedelta(days=days)
    return datetime.datetime.strptime(date_string, '%Y-%m-%d')

def format_faf_date(date):
    "Given a %Y-%m-%d day (or None), emit the datetime format used by FAF (RFC 3339), at midnight UTC"
    return datetime.datetime.combine(date, datetime.time()).isoformat(timespec='seconds') + 'Z'

def format_bigquery_datetime(datetime_obj):
    "Given a datetime obj, emit the datetime format used by BigQuery JSON imports (assumes UTC)"
    return datetime_obj.strftime('%Y-%m-%d %H:%M:%S')

def faf_to_bigquery_datetime(datetime_string):
    if datetime_string is None:
        return None
    assert datetime_string[-1] == 'Z'
    return format_bigquery_datetime(datetime.datetime.fromisoformat(datetime_string[:-1]))
