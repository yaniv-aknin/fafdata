import json
import functools
import flask
import requests

from .fetch import construct_url, yield_pages
from .transform import process_games_page
from .utils import parse_date, DEFAULT_TWO_DAYS_AGO, DEFAULT_ONE_DAY_AGO

DEFAULT_PAGE_SIZE=10
DEFAULT_FIRST_PAGE=1
DEFAULT_PER_PAGE_SLEEP=1

app = flask.Flask(__name__)

@app.route('/')
def index():
    return 'Use /scrape/<entity> to operate this tool'

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
            for game in process_games_page(page):
                yield (json.dumps(game) + '\n')
    constructor = functools.partial(construct_url, 'game', ['playerStats'], 'endTime', page_size, start_date, end_date)
    body = generate(constructor, max_pages)
    if app.debug:
        body = "".join(body)
    return app.response_class(body, mimetype='application/jsonl+json')
