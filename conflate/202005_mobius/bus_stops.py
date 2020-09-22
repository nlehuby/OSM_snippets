import json

source = "local knowledge"
no_dataset_id = True
query = [('highway', 'bus_stop')]
duplicate_distance=2
max_distance = 10
overpass_timeout = 550
delete_unmatched = True



def dataset(fileobj):
    import codecs
    source = json.load(codecs.getreader('utf-8-sig')(fileobj))
    data = []
    for el in source['features']:
        lat = float(el['geometry']['coordinates'][1])
        lon = float(el['geometry']['coordinates'][0])
        unique_id="{}_{}-{}".format(el['properties']['name'], lat, lon)
        tags = {
            'highway': 'bus_stop',
            'public_transport': 'platform',
            'name': el['properties']['name']
        }

        data.append(SourcePoint(unique_id, lat, lon, tags))
    return data

# Example item in the source JSON:
  #  4   │     {
  #  5   │       "type": "Feature",
  #  6   │       "properties": {
  #  7   │         "desserte": "LR 04, LR 06",
  #  8   │         "id": null,
  #  9   │         "locality": "XAMBES (16330)",
  # 10   │         "reseaux": "LRVT",
  # 11   │         "wheelchair_boarding": 0,
  # 12   │         "name": "Xambes Mairie"
  # 13   │       },
  # 14   │       "geometry": {
  # 15   │         "type": "Point",
  # 16   │         "coordinates": [
  # 17   │           0.104746,
  # 18   │           45.825798
  # 19   │         ]
  # 20   │       }
  # 21   │     },
