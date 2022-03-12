import datetime

def format_faf_date(date_string=None):
    "Given a %Y-%m-%d day (or None), emit the datetime format used by FAF (RFC 3339), at midnight UTC"
    if date_string is None:
        date = datetime.date.today()
    else:
        date = datetime.datetime.strptime(date_string, '%Y-%m-%d')
    return datetime.datetime.combine(date, datetime.time()).isoformat(timespec='seconds') + 'Z'

def format_bigquery_datetime(datetime_obj):
    "Given a datetime obj, emit the datetime format used by BigQuery JSON imports (assumes UTC)"
    return datetime_obj.strftime('%Y-%m-%d %H:%M:%S')

def faf_to_bigquery_datetime(datetime_string):
    if datetime_string is None:
        return None
    assert datetime_string[-1] == 'Z'
    return format_bigquery_datetime(datetime.datetime.fromisoformat(datetime_string[:-1]))
