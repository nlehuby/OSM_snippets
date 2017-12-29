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


# Example line of the source JSON:
#
# {
#   "place_id": "NVDS353-10019224",
#   "name": "Shell",
#   "category": "GAS_STATION",
#   "location": "54.978366,-1.57441",
#   "description": "",
#   "phone": 441912767084,
#   "address_street": "Shields Road",
#   "address_number": "308",
#   "address_city": "Newcastle-Upon-Tyne",
#   "address_zip": "NE6 2UU",
#   "address_country": "GB",
#   "website": "http://www.shell.co.uk/motorist/station-locator.html?id=10019224&modeselected=true",
#   "daily_hours": "MONDAY=00:00-23:59;TUESDAY=00:00-23:59;WEDNESDAY=00:00-23:59;THURSDAY=00:00-23:59;FRIDAY=00:00-23:59;SATURDAY=00:00-23:59;SUNDAY=00:00-23:59",
#   "brand": "Shell",
#   "is_deleted": false
# },
