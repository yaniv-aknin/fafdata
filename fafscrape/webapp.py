import json
import functools
import flask
import requests

from .fetch import construct_url, yield_pages
from .transform import process_games_page
from .utils import parse_date

DEFAULT_PAGE_SIZE=10
DEFAULT_TWO_DAYS_AGO='-2'
DEFAULT_FIRST_PAGE=1
DEFAULT_PER_PAGE_SLEEP=1

app = flask.Flask(__name__)

@app.route('/')
def index():
    return 'Use /scrape/<entity> to operate this tool'

@app.route('/scrape/games', methods=['POST', 'GET'] if app.debug else ['POST'])
def scrape_games():
    def generate(constructor, max_pages):
        for page in yield_pages(constructor, max_pages=max_pages):
            for game in process_games_page(page):
                yield (json.dumps(game) + '\n')
    page_size = int(flask.request.args.get('page_size', DEFAULT_PAGE_SIZE))
    per_page_sleep = int(flask.request.args.get('per_page_sleep', DEFAULT_PER_PAGE_SLEEP))
    max_pages = int(flask.request.args.get('max_pages', 0)) or float('inf')
    start_date = parse_date(flask.request.args.get('start_date', DEFAULT_TWO_DAYS_AGO))
    constructor = functools.partial(construct_url, 'game', ['playerStats'], 'endTime', start_date, page_size)
    return app.response_class(generate(constructor, max_pages), mimetype='application/jsonl+json')
