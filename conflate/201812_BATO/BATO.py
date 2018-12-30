

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
    import csv

    data = []

    reader = csv.DictReader(codecs.getreader('utf-8-sig')(fileobj), delimiter=',')
    for row in reader:
        lat = float(row['latitude'])
        lon = float(row['longitude'])
        if row['transport_mode'] == '1':
            tags = {
                'railway': 'station',
                'station': 'subway'
            }
        elif row['transport_mode'] == '0':
            tags = {
                'railway': 'tram_stop'
            }
        elif row['transport_mode'] == '2':
            tags = {
                'railway': 'station'
            }
        elif row['transport_mode'] == '3':
            tags = {
                'highway': 'bus_stop'
            }
        else :
            tags={}
        tags['official_name'] = row['stop_name']

        data.append(SourcePoint(row['source'] + row['stop_id'] + row['transport_mode'], lat, lon, tags))
    return data

# Input file extract
# source,stop_id,latitude,longitude,stop_name,transport_mode
# opendata_GTFS_fr-nw-ORE,5001,48.121295,-1.710943,J.F. Kennedy,1
# opendata_GTFS_fr-nw-ORE,5002,48.121197,-1.703882,Villejean-Université,1
# opendata_GTFS_fr-nw-ORE,5003,48.121535,-1.693350,Pontchaillou,1
# opendata_GTFS_fr-nw-ORE,5004,48.118050,-1.687529,Anatole France,1
