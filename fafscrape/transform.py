from .utils import faf_to_bigquery_datetime

def index_inclusions(inclusions):
    result = {}
    for inclusion in inclusions:
        inclusion_type = inclusion['type']
        inclusion_id = inclusion['id']
        if inclusion_type not in result:
            result[inclusion_type] = {}
        result[inclusion_type][inclusion_id] = inclusion
    return result

def get_included(inclusions, i_type, i_id):
    return inclusions[i_type][i_id]

def transform_game(game, inclusions):
    result = game['attributes'].copy()
    result['endTime'] = faf_to_bigquery_datetime(result['endTime'])
    result['startTime'] = faf_to_bigquery_datetime(result['startTime'])
    result['id'] = game['id']
    result['featuredModId'] = game['relationships']['featuredMod']['data']['id']
    # the 'or' is a bit of a hack, mapVersion is sometimes (rarely) null; see e.g. game ID 459322
    result['mapVersionId'] = (game['relationships']['mapVersion']['data'] or {'id': None})['id']
    result['playerStats'] = []
    ps_refs = game['relationships'].get('playerStats', {'data': []})
    for ref in ps_refs['data']:
        player_stats = inclusions['gamePlayerStats'][ref['id']]
        record = player_stats['attributes'].copy()
        record['scoreTime'] = faf_to_bigquery_datetime(record['scoreTime'])
        record['playerId'] = player_stats['relationships']['player']['data']['id']
        result['playerStats'].append(record)
    return result
