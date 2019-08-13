

source = "Opendata transport de diverses sources"
no_dataset_id = True
#query = [('station', 'subway')] #transport_mode = 1
#query = [('railway', 'tram_stop')] #transport_mode = 0
#query = [('railway', 'station', 'halt')] #transport_mode = 2
query = [('highway', 'bus_stop')] #transport_mode = 3
max_distance = 800
duplicate_distance = 400
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
        if row['transport_mode'] == 'metro':
            tags = {
                'railway': 'station',
                'station': 'subway'
            }
        elif row['transport_mode'] == 'tramway':
            tags = {
                'railway': 'tram_stop'
            }
        elif row['transport_mode'] == 'train':
            tags = {
                'railway': 'station'
            }
        elif row['transport_mode'] == 'bus':
            tags = {
                'highway': 'bus_stop'
            }
        else :
            tags={}
        tags['official_name'] = row['stop_name']

        data.append(SourcePoint(row['source'] + row['stop_id'] + row['transport_mode'], lat, lon, tags))
    return data

# Input file extract
#,source,stop_id,latitude,longitude,stop_name,transport_mode,geometry,index_right,nom
#124575,opendata_GTFS_fr-idf-OIF,StopPoint:41:6599,48.800383000000004,2.1280069999999998,Versailles Château - Rive Gauche Gare,bus,POINT (2.128007 48.800383),78,Yvelines
#119460,opendata_GTFS_fr-idf-OIF,StopPoint:25:123,48.654990000000005,1.8460310000000002,Grange Colombe,bus,POINT (1.846031 48.65499000000001),78,Yvelines
