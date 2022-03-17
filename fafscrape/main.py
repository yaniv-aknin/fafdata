import sys
import pathlib
import datetime
import functools
import json
import click

from .transform import process_page
from .fetch import construct_url, API_BASE, ENTITY_TYPE_TO_DEFAULT_DATE_FIELD, yield_pages, write_json
from .utils import parse_date, is_dir_populated, decompressed

@click.command()
@click.argument('inputs', type=click.Path(exists=True, dir_okay=False), nargs=-1)
@click.argument('output', type=click.File('w'), nargs=1)
def transform_api_dump_to_jsonl(inputs, output):
    with click.progressbar(inputs, label='Transforming', file=sys.stderr) as bar:
        for input in bar:
            with decompressed(input) as handle:
                page = json.load(handle)
                for xform_entity in process_page(page):
                    output.write(json.dumps(xform_entity) + '\n')
        output.close()

def invocation_metadata(**kwargs):
    metadata = {
        'cmdline': sys.argv.copy(),
        'date': datetime.datetime.today().isoformat(),
    }
    metadata.update(**kwargs)
    return metadata

@click.command()
@click.argument('output', type=click.Path(writable=True, dir_okay=True, file_okay=False, path_type=pathlib.Path))
@click.argument('entity')
@click.option('--date-field', help='When specifying dates, which entity field should be used for comparison')
@click.option('--start-date', help='Query first date; %Y-%m-%d for specific day or "-N" for N days ago', default='-2')
@click.option('--end-date', help='Query last date; %Y-%m-%d for specific day or "-N" for N days ago', default='-1')
@click.option('--page-size', type=click.INT, default=10, help='How many entities per page')
@click.option('--start-page', type=click.INT, default=1, help='Which page to start at (i.e., resume)')
@click.option('--max-pages', type=click.INT, default=10, help='Stop download after this many pages')
@click.option('--include', multiple=True, help='Which related entities to include')
@click.option('--pretty-json/--no-pretty-json', default=True)
def extract_from_faf_api(output, entity, date_field, start_date, end_date, page_size, start_page, max_pages, include, pretty_json):
    max_pages = max_pages or float('inf')
    if is_dir_populated(output):
        click.confirm(f"{output} isn't empty. Do you want to continue?", abort=True)

    if date_field is None:
        if entity not in ENTITY_TYPE_TO_DEFAULT_DATE_FIELD:
            raise click.BadParameter(f'entity {entity} requires specifying a date field')
        date_field = ENTITY_TYPE_TO_DEFAULT_DATE_FIELD[entity]

    start_date_obj = parse_date(start_date)
    end_date_obj = parse_date(end_date)

    url_constructor = functools.partial(construct_url, entity, include, date_field, page_size, start_date_obj, end_date_obj)
    generator = yield_pages(url_constructor, start_page, max_pages=max_pages)

    with open(output/f'{entity}.metadata.json', 'w') as handle:
        metadata = invocation_metadata(start_date=start_date, end_date=end_date, date_field=date_field, max_pages=max_pages,
                                       sample_url=url_constructor(page_number=start_page))
        json.dump(metadata, handle, indent=4)

    first_page = next(generator)
    length = min(max_pages, first_page['meta']['page']['totalPages']) - start_page
    with click.progressbar(length=length, label='Scraping API', file=sys.stderr) as bar:
        write_json(output / f'{entity}{start_page:04d}.json', first_page, pretty_json)
        bar.update(1)
        for counter, page in enumerate(generator, start_page+1):
            write_json(output / f'{entity}{counter:04d}.json', page, pretty_json)
            bar.update(1)
