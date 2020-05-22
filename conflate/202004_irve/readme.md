# IRVE


cat opendata_stations.csv |xsv search -v -s id_station '^$' > opendata_station_with_id.csv

(on a besoin d'un id unique pour utiliser l'outil, même si c'est pas une clef de correspondance avec OSM)

`conflate IRVE.py -c resultats_sans_ref.json -i opendata_station_with_id.csv  --osm irve.osm`

sans param duplicate_distance, et avec une distance de 100 :

11:52:10 Dataset points duplicate each other: FR*M13*P13056*003MARTIGUES - Avenue Louis Sammut and FR*M13*P13056*001MARTIGUES - Avenue Louis Sammut - Parking Stade Turcan
11:52:10 Dataset points are too similar: FR*M29*P29019*004BREST - Rue Des Mouettes 1 and FR*M29*P29019*005BREST - Rue Des Mouettes 2
11:52:10 Dataset points are too similar: FR*A22*P06083*003MENTON - Quai De Monléon (Borne 1) and FR*A22*P06083*004MENTON - Quai De Monléon ( Borne 2)
11:52:10 Dataset points duplicate each other: FR*S34*P34163*002MONTARNAUD - Parking Covoiturage D619 and FR*S34*P34163*001MONTARNAUD - Parking Covoiturage D619
11:52:10 Dataset points duplicate each other: FR*S34*P34300*002SERVIAN - Parking Covoiturage and FR*S34*P34300*001SERVIAN - Parking Covoiturage
11:52:11 Found 184 duplicates in the dataset
11:52:11 Read 4745 items from the dataset
11:52:11 Downloaded 5761 objects from OSM
11:52:14 Matched 1759 points
11:52:14 Removed 171 unmatched duplicates
11:52:14 Adding 2815 unmatched dataset points
11:52:14 Deleted 0 and retagged 4002 unmatched objects from OSM
11:52:14 Done
