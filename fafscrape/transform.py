import re
import json

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
        return f'{relationship}_{inclusion["type"]}_id', inclusion['id']
    else:
        return f'{relationship}_{inclusion["type"]}', index[inclusion['type']][inclusion['id']]

def generic_transform(entity, embedding_index):
    result = transform_attributes(entity)
    for relationship, inclusion in entity['relationships'].items():
        inclusion = inclusion['data']
        if not inclusion:
            continue
        if type(inclusion) is list:
            related_type = inclusion[0]['type']
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

class PartitionedWriter:
    """A class meant to sequentially write to many files in unguaranteed order.

    The heart of the class is the `write(datum)`. PartitionedWriter will apply a user-provided
    function to identify the right path from this datum, encode the datum with a user-provided
    encoding function, and append the result to the right path (possibly opening the file or
    using a cached file descriptor maintained in an LRU)."""
    def __init__(self, get_path_for_datum, encoder=json.dumps, max_file_descriptors=50, write_suffix='\n', dedup_key=None):
        self.get_path = get_path_for_datum
        self.encoder = encoder
        self.max_file_descriptors = max_file_descriptors
        self.write_suffix = write_suffix
        self.dedup_key = dedup_key
        self.handles = {}
        self.seen = set()
    def get_handle(self, path):
        if path not in self.handles:
            if len(self.handles) == self.max_file_descriptors:
                self.handles.pop(next(iter(self.handles))).close()
            if not path.parent.exists():
                path.parent.mkdir(parents=True)
            self.handles[path] = open(path, 'a')
        return self.handles[path]
    def is_duplicate(self, datum):
        if not self.dedup_key:
            return False
        key = self.dedup_key(datum)
        if key in self.seen:
            return True
        self.seen.add(key)
        return False
    def write(self, datum):
        if self.is_duplicate(datum):
            return
        path = self.get_path(datum)
        handle = self.get_handle(path)
        # what's better - concatenating the strings or calling write twice?
        # I saw <1% difference benchmarking writes of a 3K JSON 500K times using CPython 3.10.4
        handle.write(self.encoder(datum) + self.write_suffix)
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        while self.handles:
            self.handles.popitem()[1].close()
