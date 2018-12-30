import json
import codecs
import re
from collections import defaultdict

source = 'SIRENE 12/2017'
no_dataset_id = True
query = [('shop', 'bakery')]
max_distance = 50
max_request_boxes = 3
master_tags = ('shop',)


def dataset(fileobj):

    source = json.load(codecs.getreader('utf-8-sig')(fileobj))
    data = []
    for el in source:
        lat = float(el['latitude'])
        lon = float(el['longitude'])
        tags = {
            'shop': 'bakery',
            'name_siren': el['NOMEN_LONG'].title(),
        }

        data.append(SourcePoint(el['SIREN'], lat, lon, tags))
    return data
