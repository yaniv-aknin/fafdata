import pathlib
import datetime
import functools
import json
import click

from .transform import transform_game, index_inclusions
from .fetch import construct_url, API_BASE, ENTITY_TYPE_TO_DEFAULT_DATE_FIELD, yield_pages, write_json
from .utils import parse_date

@click.command()
@click.argument('inputs', type=click.File('r', lazy=True), nargs=-1)
@click.argument('output', type=click.File('w'), nargs=1)
def faf_dump_to_bigquery_jsonl(inputs, output):
    with click.progressbar(inputs, label='Transforming') as bar:
        for input in bar:
            raw = json.load(input)
            inclusions = index_inclusions(raw['included'])
            for game in raw['data']:
                assert game['type'] == 'game'
                output.write(json.dumps(transform_game(game, inclusions)) + '\n')
            input.close()
        output.close()


@click.command()
@click.argument('output', type=click.Path(writable=True, dir_okay=True, file_okay=False, path_type=pathlib.Path))
@click.argument('entity')
@click.option('--date-field', help='When specifying dates, which entity field should be used for comparison')
@click.option('--start-date', type=click.DateTime(formats=["%Y-%m-%d"]))
@click.option('--page-size', type=click.INT, default=10, help='How many entities per page')
@click.option('--max-pages', type=click.INT, default=10, help='Stop download after this many pages')
@click.option('--include', multiple=True, help='Which related entities to include')
@click.option('--pretty-json/--no-pretty-json', default=True)
def scrape_faf_api(output, entity, date_field, start_date, page_size, max_pages, include, pretty_json):
    if date_field is None:
        if entity not in ENTITY_TYPE_TO_DEFAULT_DATE_FIELD:
            raise click.BadParameter(f'entity {entity} requires specifying a date field')
        date_field = ENTITY_TYPE_TO_DEFAULT_DATE_FIELD[entity]

    if type(start_date) is datetime.datetime:
        start_date = start_date.date() # there is no builtin click.Date(), so just chop off time
    else:
        start_date = parse_date('-1') # chooses "yesterday"

    url_constructor = functools.partial(construct_url, entity, include, date_field, start_date, page_size)
    generator = yield_pages(url_constructor, max_pages=max_pages)

    first_page = next(generator)
    length = min(max_pages, first_page['meta']['page']['totalPages'])
    with click.progressbar(length=length, label='Scraping API') as bar:
        write_json(output / 'dump0001.json', first_page, pretty_json)
        bar.update(1)
        for counter, page in enumerate(generator, 2):
            write_json(output / f'dump{counter:04d}.json', page, pretty_json)
            bar.update(counter)
