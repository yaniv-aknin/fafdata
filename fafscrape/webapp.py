import flask
import datetime
import requests
import urlobject

from .utils import format_faf_date

app = flask.Flask(__name__)
API_BASE = urlobject.URLObject('https://api.faforever.com')
DEFAULT_PAGE_SIZE=10000

@app.route('/')
def index():
    return 'Use /scrape/<object> to operate this tool'

@app.route('/scrape/game')
def scrape_game():
    page_size = flask.request.args.to_dict().get('page_size', DEFAULT_PAGE_SIZE)
    if 'start_date' in flask.request.args:
        start_date = format_faf_date(parse_date(flask.request.args['start_date']))
    else:
        start_date = format_faf_date(datetime.date.today())
    url = (
        API_BASE
        .with_path('/data/game')
        .add_query_param('page[size]', page_size)
        .add_query_param('page[totals]', '')
        .add_query_param('filter', f'endTime=ge={start_date}')
        .add_query_param('include', 'playerStats')
    )
    response = requests.get(url)
    return response.json()
