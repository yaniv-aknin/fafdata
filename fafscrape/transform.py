import re

from .utils import faf_to_bigquery_datetime

DATE_REGEX = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')

def transform_attributes(entity):
    result = {'id': entity['id']}
    for key, value in entity['attributes'].items():
        if type(value) is str and DATE_REGEX.match(value):
            value = faf_to_bigquery_datetime(value)
        result[key] = value
    return result

def embed(relationship, inclusion, index):
    if inclusion['type'] not in index:
        return f'{relationship}.{inclusion["type"]}.id', inclusion['id']
    else:
        return f'{relationship}.{inclusion["type"]}', index[inclusion['type']][inclusion['id']]

def generic_transform(entity, embedding_index):
    result = transform_attributes(entity)
    for relationship, inclusion in entity['relationships'].items():
        inclusion = inclusion['data']
        if not inclusion:
            continue
        if type(inclusion) is list:
            related_type = inclusion[0]['type']
            result[f'{relationship}.{related_type}.id'] = list()
            for datum in inclusion:
                assert datum['type'] == related_type
                embedding_key, embedded_value = embed(relationship, datum, embedding_index)
                result.setdefault(embedding_key, []).append(embedded_value)
        else:
            related_type = inclusion['type']
            embedding_key, embedded_value = embed(relationship, inclusion, embedding_index)
            result[embedding_key] = embedded_value
    return result

def index_inclusions(page, types_to_index):
    if not types_to_index:
        return {}
    index = {inclusion_type: {} for inclusion_type in types_to_index}
    for entity in page['included']:
        if entity['type'] in types_to_index:
            index[entity['type']][entity['id']] = transform_attributes(entity)
    return index

def process_page(page, embed_inclusion_types=None):
    embedding_index = index_inclusions(page, embed_inclusion_types)
    for entity in page['data']:
        yield generic_transform(entity, embedding_index)
