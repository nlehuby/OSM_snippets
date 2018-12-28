# Des cinémas

installer osm_conflate: `pipenv install && pipenv shell`

## Paris

Données à télécharger : https://cinema-public.opendatasoft.com/explore/dataset/cinemas-a-parisparisdata/export/

Puis, pour lancer la conflation: `conflate cinema_paris_json.py -c results_cinema_paris.json -i cinemas-paris.json --osm cinema.osm`

résultats:

```
17:44:17 Dataset points duplicate each other: 6f3d75df3c23ef5ecdae3ac55614f873cf672963 and 3f3b7fc223c96e2a44b436986f2e2d5437daf7cd
17:44:17 Found 1 duplicates in the dataset
17:44:17 Read 86 items from the dataset
17:44:18 Downloaded 95 objects from OSM
17:44:18 Matched 79 points
17:44:18 Removed 1 unmatched duplicates
17:44:18 Adding 6 unmatched dataset points
17:44:18 Deleted 0 and retagged 0 unmatched objects from OSM
17:44:18 Done

```
# Autres sources à explorer

* https://cinema-public.opendatasoft.com/explore/dataset/salle_de_cinema_ile-de-francedatailedefrance/api/
* https://cinema-public.opendatasoft.com/explore/dataset/cnc-donnees-cartographies-2017/table/

