import json

source = "Île-de-France Mobilités 04/2019"
no_dataset_id = True
query = [('park_ride', 'yes')]
master_tags = ('amenity',)
max_distance = 800
max_request_boxes = 3
overpass_timeout = 550



def dataset(fileobj):
    import codecs
    source = json.load(codecs.getreader('utf-8-sig')(fileobj))
    #source = json.load(fileobj)
    data = []
    for el in source:

        lat = float(el['geometry']['coordinates'][1])
        lon = float(el['geometry']['coordinates'][0])
        tags = {
            'amenity': 'parking',
            'park_ride': 'yes',
            'capacity': el['fields']['nb_pl_pr'],
            'official_name': el['fields']['nom_pr']
        }

        data.append(SourcePoint(el['recordid'], lat, lon, tags))
    return data

# Example line of the source JSON:
# {
#     "datasetid": "parcs-relais-idf",
#     "recordid": "fe9680496370980cb966e3bca09793b443915fd8",
#     "fields": {
#         "www": "www.saint-quentin-en-yvelines.fr",
#         "nb_pl_elec": 0.0,
#         "nb_pl_pr": 219.0,
#         "moa_pr": "CASQY",
#         "nom_lda": "Saint-Quentin-en-Yvelines (Gare)",
#         "nom_comm": "Montigny-le-Bretonneux",
#         "nb_pl_2rm": 0.0,
#         "mes_date": "2014-03-24T01:00:00+01:00",
#         "mes_annee": 2014.0,
#         "nom_gare": "SAINT-QUENTIN-EN-YVELINES (SNCF)",
#         "nb_pl_cov": 0.0,
#         "label_pr": 1.0,
#         "gestion_pr": "Q-Park",
#         "nom_pr": "Jol Le Theule",
#         "struct_pr": "ouvrage",
#         "nom_zdl": "Saint-Quentin-en-Yvelines (Avenue des Prs)",
#         "id_ref_lda": 63812.0,
#         "id_pr": 35.0,
#         "geo_shape": {
#             "type": "MultiPoint",
#             "coordinates": [
#                 [2.0439044, 48.78620339998614, 0.0]
#             ]
#         },
#         "id_ref_zdl": 43249.0,
#         "nb_pl_pmr": 6.0,
#         "adres_pr": "10 Rue Jol le Theule, 78180 Montigny-le-Bretonneux",
#         "geo_point_2d": [48.78620339998614, 2.0439044],
#         "nb_pl_v": 0.0,
#         "insee_t": "78423"
#     },
#     "geometry": {
#         "type": "Point",
#         "coordinates": [2.0439044, 48.78620339998614]
#     },
#     "record_timestamp": "2019-02-19T16:15:48+01:00"
# }
