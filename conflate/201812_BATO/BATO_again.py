

source = "Opendata transport de diverses sources"
no_dataset_id = True
#query = [('station', 'subway')] #transport_mode = 1
#query = [('railway', 'tram_stop')] #transport_mode = 0
#query = [('railway', 'station', 'halt')] #transport_mode = 2
query = [('highway', 'bus_stop')] #transport_mode = 3
max_distance = 800
max_request_boxes = 300
overpass_timeout = 850

def dataset(fileobj):
    import codecs
    import json

    source = json.load(codecs.getreader('utf-8-sig')(fileobj))
    data = []
    for el in source['features']:
        lat = el['geometry']['coordinates'][1]
        lon = el['geometry']['coordinates'][0]
        tags = {
                'highway': 'bus_stop'
            }
        tags['official_name'] = el['properties']['tags.official_name']

        data.append(SourcePoint(el['properties']['ref_id'], lat, lon, tags))
    return data

