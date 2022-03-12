import json
import click

from .transform import transform_game, index_inclusions

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
