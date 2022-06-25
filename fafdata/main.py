import sys
import re
import os
import pathlib
import datetime
import functools
import json
import jsonpath_ng
import click
import pickle

from .transform import process_page, PartitionedWriter
from .fetch import construct_url, API_BASE, ENTITY_TYPE_TO_DEFAULT_DATE_FIELD, yield_pages, write_json
from .utils import parse_date, is_dir_populated, decompressed, compressed
from .parse import load_replay
from .dump import process_commands

def verify_empty(ctx, param, output_directory):
    if not output_directory.exists():
        output_directory.mkdir()
    if is_dir_populated(output_directory):
        click.confirm(f"{output_directory} isn't empty. Do you want to continue?", abort=True)
    return output_directory

@click.command()
@click.argument('inputs', type=click.Path(exists=True, dir_okay=False), nargs=-1)
@click.option('--ignore-errors/--no-ignore-errors', default=True)
@click.option('--in-suffix', default='.fafreplay')
@click.option('--out-suffix', default='.pickle.zstd')
def parse_replays_to_pickle(inputs, ignore_errors, in_suffix, out_suffix):
    for inpath in inputs:
        if not(inpath.endswith(in_suffix)):
            continue
        outpath = inpath.replace(in_suffix, out_suffix)
        if os.path.exists(outpath):
            continue
        try:
            parsed = load_replay(inpath)
        except (Exception if ignore_errors else ()):
            continue
        with compressed(outpath) as handle:
            pickle.dump(parsed, handle)

def parse_regexes(regex_specs):
    result = {}
    for spec in regex_specs:
        column, _, regex = spec.partition('/')
        result[column] = re.compile(regex)
    return result

def parse_jsonpaths(jsonpath_specs):
    result = {}
    for spec in jsonpath_specs:
        column, _, jsonpath = spec.partition('/')
        expr = jsonpath_ng.parse(jsonpath)
        if column.endswith('@'):
            result[column[:-1]] = expr, True
        else:
            result[column] = expr, False
    return result

@click.command()
@click.argument('inputs', type=click.Path(exists=True, dir_okay=True, path_type=pathlib.Path), nargs=-1)
@click.argument('output', type=click.Path(dir_okay=False), nargs=1)
@click.option('--regex', multiple=True)
@click.option('--jsonpath', multiple=True)
def dump_replay_commands_to_jsonl(inputs, output, regex, jsonpath):
    column_to_pattern = parse_regexes(regex)
    column_to_jsonpath = parse_jsonpaths(jsonpath)
    inputs = list(inputs)
    with compressed(output) as outhandle:
        while inputs:
            inpath = inputs.pop()
            if inpath.is_dir():
                inputs.extend(inpath.iterdir())
                continue
            parsed = load_replay(str(inpath))
            for cmd in process_commands(parsed, column_to_pattern, column_to_jsonpath):
                outhandle.write(json.dumps(cmd).encode()+b'\n')

partition_strategies = {}
def partition_by(f):
    partition_strategies[f.__name__] = f
    return f

@partition_by
def single_file(base, datum):
    return base / 'xformed.jsonl'

@partition_by
def year_month(base, datum):
    return base / f'dt={datum["startTime"][:4]}-01-01' / f'{datum["startTime"][:7]}-01.jsonl'

@click.command()
@click.argument('inputs', type=click.Path(exists=True, dir_okay=False), nargs=-1)
@click.argument('output', type=click.Path(writable=True, dir_okay=True, file_okay=False, path_type=pathlib.Path), callback=verify_empty)
@click.option('--embed-inclusion', multiple=True)
@click.option('--partition-strategy', type=click.Choice(partition_strategies), default=next(iter(partition_strategies)))
@click.option('--dedup-on-field', default='id')
def transform_api_dump_to_jsonl(inputs, output, embed_inclusion, partition_strategy, dedup_on_field):
    get_path_for_datum = functools.partial(partition_strategies[partition_strategy], output)
    dedup_key = None if not dedup_on_field else lambda x: x[dedup_on_field]
    with PartitionedWriter(get_path_for_datum, dedup_key=dedup_key) as writer:
        with click.progressbar(inputs, label='Transforming', file=sys.stderr) as bar:
            for input in bar:
                with decompressed(input) as inhandle:
                    page = json.load(inhandle)
                    for xform_entity in process_page(page, embed_inclusion):
                        writer.write(xform_entity)

def invocation_metadata(**kwargs):
    metadata = {
        'cmdline': sys.argv.copy(),
        'date': datetime.datetime.today().isoformat(),
    }
    metadata.update(**kwargs)
    return metadata

@click.command()
@click.argument('output', type=click.Path(writable=True, dir_okay=True, file_okay=False, path_type=pathlib.Path), callback=verify_empty)
@click.argument('entity')
@click.option('--date-field', help='When specifying dates, which entity field should be used for comparison')
@click.option('--start-date', help='Query first date; %Y-%m-%d for specific day or "-N" for N days ago', default='-2')
@click.option('--end-date', help='Query last date; %Y-%m-%d for specific day or "-N" for N days ago', default='-1')
@click.option('--page-size', type=click.INT, default=10, help='How many entities per page')
@click.option('--start-page', type=click.INT, default=1, help='Which page to start at (i.e., resume)')
@click.option('--max-pages', type=click.INT, default=10, help='Stop download after this many pages')
@click.option('--include', multiple=True, help='Which related entities to include')
@click.option('--filters', multiple=True, help='Extra filters to add')
@click.option('--pretty-json/--no-pretty-json', default=True)
def extract_from_faf_api(output, entity, date_field, start_date, end_date, page_size, start_page, max_pages, include, pretty_json, filters):
    max_pages = max_pages or float('inf')

    if date_field is None:
        if entity not in ENTITY_TYPE_TO_DEFAULT_DATE_FIELD:
            raise click.BadParameter(f'entity {entity} requires specifying a date field')
        date_field = ENTITY_TYPE_TO_DEFAULT_DATE_FIELD[entity]

    start_date_obj = parse_date(start_date)
    end_date_obj = parse_date(end_date)

    url_constructor = functools.partial(construct_url, entity, include, date_field, page_size, start_date_obj, end_date_obj, filters=filters)
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
