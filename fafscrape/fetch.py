import datetime
import requests
import urlobject

from .utils import format_faf_date

API_BASE = urlobject.URLObject('https://api.faforever.com')

def construct_url(entity, include, date_field, start_date, page_size, page_number=1, sort='ASC', api_base=API_BASE):
    start_date = format_faf_date(start_date or datetime.date.today())
    url = api_base.with_path(f'/data/{entity}')
    url = url.add_query_param('page[size]', page_size)
    url = url.add_query_param('page[number]', page_number)
    url = url.add_query_param('page[totals]', '')
    url = url.add_query_param('filter', f'{date_field}=ge={start_date}')
    url = url.add_query_param('include', ','.join(include))
    url = url.add_query_param('sort', f'-{date_field}' if sort == 'DESC' else f'{date_field}')
    return url

def yield_pages(url_constructor, start_page=1, max_pages=float('inf')):
    current_page = start_page
    page = requests.get(url_constructor(page_number=current_page)).json()
    yield page
    max_pages = min(max_pages, page['meta']['page']['totalPages'])
    while current_page < max_pages:
        current_page += 1
        yield requests.get(url_constructor(page_number=current_page)).json()
