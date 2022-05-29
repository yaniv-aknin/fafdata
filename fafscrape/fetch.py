import json
import datetime
import requests
import urlobject

from .utils import format_faf_date

API_BASE = urlobject.URLObject('https://api.faforever.com')

ENTITY_TYPE_TO_DEFAULT_DATE_FIELD = {
    'game': 'endTime',
    'player': 'createTime',
}

def construct_url(entity, include, date_field, page_size, start_date, end_date, page_number=1, sort='ASC', filters=(), api_base=API_BASE):
    url = api_base.with_path(f'/data/{entity}')
    url = url.add_query_param('page[size]', page_size)
    url = url.add_query_param('page[number]', page_number)
    url = url.add_query_param('page[totals]', '')
    filters = list(filters)
    start_date = format_faf_date(start_date)
    filters.append(f'{date_field}=ge={start_date}')
    end_date = format_faf_date(end_date)
    filters.append(f'{date_field}=le={end_date}')
    url = url.add_query_param('filter', ';'.join(filters))
    if include:
        url = url.add_query_param('include', ','.join(include))
    url = url.add_query_param('sort', f'-{date_field}' if sort == 'DESC' else f'{date_field}')
    return url

def fetch_page(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def yield_pages(url_constructor, start_page=1, max_pages=float('inf')):
    current_page = start_page
    page = fetch_page(url_constructor(page_number=current_page))
    yield page
    max_pages = min(max_pages, page['meta']['page']['totalPages'])
    while current_page < max_pages:
        current_page += 1
        yield fetch_page(url_constructor(page_number=current_page))

def write_json(path, doc, pretty):
    with open(path, 'w') as handle:
        json.dump(doc, handle, indent=(4 if pretty else None))
