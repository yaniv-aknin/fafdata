import os
import time
import json
import tempfile
import pathlib
import functools
import flask
import requests

from .fetch import construct_url, yield_pages
from .transform import process_page
from .utils import parse_date, DEFAULT_TWO_DAYS_AGO, DEFAULT_ONE_DAY_AGO
from .load import get_client, load_table_from_iterable

DEFAULT_PAGE_SIZE=10
DEFAULT_FIRST_PAGE=1
DEFAULT_PER_PAGE_SLEEP=1

app = flask.Flask(__name__)

@app.route('/')
def index():
    return 'Use /scrape/<entity> to operate this tool'

# refuse 'GET' unless in debug mode because GET should be idempotent (but for debug it's easier to invoke)
@app.route('/scrape/games', methods=['POST', 'GET'] if app.debug else ['POST'])
def scrape_games():
    page_size = int(flask.request.args.get('page_size', DEFAULT_PAGE_SIZE))
    per_page_sleep = int(flask.request.args.get('per_page_sleep', DEFAULT_PER_PAGE_SLEEP))
    max_pages = int(flask.request.args.get('max_pages', 0)) or float('inf')
    start_date = parse_date(flask.request.args.get('start_date', DEFAULT_TWO_DAYS_AGO))
    end_date = parse_date(flask.request.args.get('end_date', DEFAULT_ONE_DAY_AGO))
    app.logger.info('invoked page_size=%d per_page_sleep=%d max_pages=%s start_date=%s end_date=%s',
                    page_size, per_page_sleep, max_pages, start_date, end_date)

    def generate(constructor, max_pages):
        for page in yield_pages(constructor, max_pages=max_pages):
            meta = page['meta']['page']
            app.logger.info('processing page %d of %d (%d rows)', meta['number'], meta['totalPages'], meta['totalRecords'])
            yield from process_page(page)
            time.sleep(per_page_sleep)

    # creating the client can fail if credentials aren't set up, so we intentionally do it early before doing any FAF API traffic
    client = get_client()
    constructor = functools.partial(construct_url, 'game', ['playerStats'], 'endTime', page_size, start_date, end_date)
    table_id = os.environ['BIGQUERY_GAME_TABLE_ID']
    job = load_table_from_iterable(client, table_id, generate(constructor, max_pages))
    job.result()
    return str((job.job_id, job.state))
