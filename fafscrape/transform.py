import re

from .utils import faf_to_bigquery_datetime

DATE_REGEX = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')

def generic_transform(entity):
    result = {}
    for key, value in entity['attributes'].items():
        if type(value) is str and DATE_REGEX.match(value):
            value = faf_to_bigquery_datetime(value)
        result[key] = value
    result['id'] = entity['id']
    for relationship, data in entity['relationships'].items():
        data = data['data']
        if not data:
            continue
        if type(data) is list:
            related_type = data[0]['type']
            result[f'{relationship}.{related_type}.id'] = list()
            for datum in data:
                assert datum['type'] == related_type
                result[f'{relationship}.{related_type}.id'].append(datum['id'])
        else:
            related_type = data['type']
            result[f'{relationship}.{related_type}.id'] = data['id']
    return result

def process_page(page):
    for entity in page['data']:
        yield generic_transform(entity)
