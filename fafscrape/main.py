import json
import click

from .transform import transform_game, index_inclusions

@click.command()
@click.argument('input', type=click.File('r'))
@click.argument('output', type=click.File('w'), default='-')
def faf_dump_to_bigquery_jsonl(input, output):
    raw = json.load(input)
    inclusions = index_inclusions(raw['included'])
    for game in raw['data']:
        assert game['type'] == 'game'
        output.write(json.dumps(transform_game(game, inclusions)) + '\n')
