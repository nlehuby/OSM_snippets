# Des parcs relais

installer osm_conflate: `pipenv install && pipenv shell`

Données à télécharger : https://opendata.stif.info/explore/dataset/parcs-relais-idf/information/

Puis, pour lancer la conflation: `conflate park_ride_idf_json.py -c resultats.json -i parcs-relais-idf.json  --osm park_ride.osm`

résultats:

```
17:34:54 Read 46 items from the dataset
17:35:04 Downloaded 31 objects from OSM
17:35:04 Matched 14 points
17:35:04 Adding 32 unmatched dataset points
17:35:04 Deleted 0 and retagged 0 unmatched objects from OSM
17:35:04 Done

```
