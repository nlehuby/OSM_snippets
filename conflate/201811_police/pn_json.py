import json

source = "data.gouv.fr:Ministère de l'Intérieur 11/2018"
no_dataset_id = True
query = [('amenity', 'police')]
max_distance = 300
max_request_boxes = 3
master_tags = ('operator',)
overpass_timeout = 550



def dataset(fileobj):
    import codecs
    source = json.load(codecs.getreader('utf-8-sig')(fileobj))
    #source = json.load(fileobj)
    data = []
    for el in source:
        lat = float(el['geocodage_y_GPS'])
        lon = float(el['geocodage_x_GPS'])
        tags = {
            'amenity': 'police',
            'operator': 'Police nationale',
            'police:FR': 'police',
            'phone': el['telephone'],
            'official_name': el['service'],
        }

        data.append(SourcePoint(el['adresse_geographique'], lat, lon, tags))
    return data


# Example line of the source JSON:
#
# {
#     "code_postal": "01000",
#     "code_commune_insee": "01053",
#     "geocodage_y": "6569852.464",
#     "adresse_geographique": "4 Rue des Remparts 01000 BOURG EN BRESSE",
#     "commune": "BOURG EN BRESSE",
#     "service": "Commissariat de police de Bourg en Bresse",
#     "departement": "01",
#     "voie": "4 Rue des Remparts",
#     "geocodage_x_GPS": "5.22517643",
#     "geocodage_y_GPS": "46.20676468",
#     "telephone": "+33 4 74 47 20 20",
#     "geocodage_x": "871543.203",
#     "geocodage_epsg": "2154"
# },
