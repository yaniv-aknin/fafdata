import io
import json
from google.cloud import bigquery

def get_client():
    return bigquery.Client()

# This is a bit of a hack. I had spurious errors using `load_table_from_json()`, with the job failing like so:
#  '400 Provided Schema does not match Table fafalytics:faf.games. Field id has changed type from STRING to INTEGER'
# I was unable to reproduce reliably, but it never happened from CLI `bq load`, only `load_table_from_json()`.
# Some debugging found that `load_table_from_json()` behaves differently from other `load_table_from_*()`:
# * `load_table_from_json()` auto-enables schema detection when no schema is given; see code:
# https://github.com/googleapis/python-bigquery/commit/d160be1b4408cd3346843c99e3ddf5d8e297f940#diff-fc3199dcfb64ea8758d31d37f30dc25c4885b1c21b03812fbc0f1914f48763f3R1637-R1638
# * Other `load_table_from_*()` simply leave schema auto-detection unset unless explicitly requested.
# I can confirm the failing jobs always had schema auto-detection enabled, and that commenting out the auto-enable
# code made the problem go away in my experiments. But absent a reliable reproduction, I didn't think it's worth reporting
# a bug, and just hacked the following instead.
# My best repro is here: https://gist.github.com/yaniv-aknin/22fee0e09ee14dd2d53ea44cbf670cd0
def load_table_from_iterable(client, table_id, iterable):
    data_str = u"\n".join(json.dumps(item) for item in iterable)
    data_file = io.BytesIO(data_str.encode())
    job_config = bigquery.LoadJobConfig(source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON, write_disposition='WRITE_APPEND')
    job = client.load_table_from_file(data_file, table_id, job_config=job_config)
    return job.result()
