

source = "Opendata IRVE de diverses sources"
query = [('amenity', 'charging_station')]
max_distance = 100
#duplicate_distance = 4
max_request_boxes = 300
overpass_timeout = 850

no_dataset_id = True

#no_dataset_id = False
#dataset_id = "EU:EVSE"

delete_unmatched = False
tag_unmatched = {
    'opendata:conflation': "pas trouvé dans l'open data",
}


def dataset(fileobj):
    import codecs
    import csv

    data = []

    reader = csv.DictReader(codecs.getreader('utf-8-sig')(fileobj), delimiter=',')
    for row in reader:
        lat = float(row['Ylatitude'])
        lon = float(row['Xlongitude'])
        tags = {
		'amenity': 'charging_station',
		'motorcar': 'yes'
	    }
        tags['opendata:operator'] = row['n_operateur']
        tags['opendata:network'] = row['n_enseigne']
        tags['opendata:owner'] = row['n_amenageur']
        tags['opendata:capacity'] = row['nbre_pdc']

        tags['opendata:socket:type2_combo'] = row['nb_combo_grouped']
        tags['opendata:socket:type2'] = row['nb_T2_grouped']
        tags['opendata:socket:chademo'] = row['nb_chademo_grouped']
        tags['opendata:socket:typee'] = row['nb_EF_grouped']
        tags['opendata:socket:typee'] = row['nb_EF_grouped']
        tags['opendata:socket:type3c'] = row['nb_T3c_grouped']

        tags['opendata:source'] = row['source_grouped']
        tags['opendata:ref:EU:EVSE'] = row['id_station']
        tags['opendata:name'] = row['n_station']

	# TODO - fee, opening_hours


        data.append(SourcePoint(row['id_station'] + row['n_station'], lat, lon, tags))
    return data

# Input file extract
#n_amenageur,n_operateur,n_enseigne,id_station,n_station,ad_station,code_insee,Xlongitude,Ylatitude,nbre_pdc,source_grouped,acces_recharge_grouped,accessibilité_grouped,nb_prises_grouped,prises_grouped,nb_T2_grouped,nb_T3c_grouped,nb_EF_grouped,nb_chademo_grouped,nb_combo_grouped
#Aix-Marseille-Provence,Bouygues Énergies et Services,MAMP,FR*M13*P13001*015,AIX-EN-PROVENCE - Route De Sisteron,Route De Sisteron 13100 AIX-EN-PROVENCE,13001,5.459641,43.556239,0,https://www.data.gouv.fr/fr/datasets/infrastructures-de-recharge-pour-vehicules-electriques-metropole-aix-marseille-provence/#resource-e61812cd-6727-438c-8df5-c9971f5b679b,payant,24h/24 7j/7,4,"['EF - T2', 'EF - T2']",2,0,2,0,0
