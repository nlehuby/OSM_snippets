import json

source = "Centre national du cinéma et de l'image animée (CNC) 12/2018"
no_dataset_id = True
query = [('amenity', 'cinema')]
master_tags = ('amenity',)
max_distance = 500
max_request_boxes = 3
overpass_timeout = 550



def dataset(fileobj):
    import codecs
    source = json.load(codecs.getreader('utf-8-sig')(fileobj))
    #source = json.load(fileobj)
    data = []
    for el in source:
        if not 'coordonnees' in el['fields']:
            continue

        lat = float(el['fields']['coordonnees'][0])
        lon = float(el['fields']['coordonnees'][1])
        tags = {
            'amenity': 'cinema',
            #TODO : use "art_et_essai" field ?
            'official_name': el['fields']['nom_etablissement'],
        }

        data.append(SourcePoint(el['recordid'], lat, lon, tags))
    return data

#https://cinema-public.opendatasoft.com/explore/dataset/cinemas-a-parisparisdata/information/
# Example line of the source JSON:
#
# {
#     "datasetid": "cinemas-a-parisparisdata",
#     "recordid": "611ac42fadc7d0d66b0d13813aeb0b41ca6b5057",
#     "fields": {
#         "ecrans": 2,
#         "fauteuils": "200",
#         "ndegauto": 8374,
#         "arrondissement": 75005,
#         "art_et_essai": "A",
#         "adresse": "23 RUE DES ECOLES",
#         "nom_etablissement": "LE DESPERADO 1",
#         "coordonnees": [48.848384, 2.348973]
#     },
#     "geometry": {
#         "type": "Point",
#         "coordinates": [2.348973, 48.848384]
#     },
#     "record_timestamp": "2016-08-27T18:20:45+02:00"
# }
