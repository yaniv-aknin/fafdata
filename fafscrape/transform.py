from .utils import faf_to_bigquery_datetime

def index_inclusions(inclusions):
    result = {}
    for inclusion in inclusions:
        inclusion_type = inclusion['type']
        inclusion_id = inclusion['id']
        if inclusion_type not in result:
            result[inclusion_type] = {}
        result[inclusion_type][inclusion_id] = inclusion['attributes'].copy()
    return result

def get_included(inclusions, i_type, i_id):
    return inclusions[i_type][i_id].copy()

def transform_game(game, inclusions):
    result = game['attributes'].copy()
    result['endTime'] = faf_to_bigquery_datetime(result['endTime'])
    result['startTime'] = faf_to_bigquery_datetime(result['startTime'])
    result['id'] = game['id']
    result['featuredMod'] = game['relationships']['featuredMod']['data']['id']
    result['playerStats'] = []
    ps_refs = game['relationships'].get('playerStats', {'data': []})
    for ref in ps_refs['data']:
        player_stats = get_included(inclusions, 'gamePlayerStats', ref['id'])
        player_stats['scoreTime'] = faf_to_bigquery_datetime(player_stats['scoreTime'])
        result['playerStats'].append(player_stats)
    return result

