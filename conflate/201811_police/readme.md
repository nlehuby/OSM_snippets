# Conflation des commissariats de police

Utilisé dans le cadre du [#ProjetOSMDuMois de novembre 2018](https://wiki.openstreetmap.org/wiki/FR:Project_of_the_month/Gendarmerie_nationale), pour créer un [challenge MapRoulette](https://maproulette.org/mr3/browse/challenges/3317)


Données à télécharger : https://www.data.gouv.fr/fr/datasets/liste-des-services-de-police-accueillant-du-public-avec-geolocalisation/

Pour reproduire 

* installer osm_conflate: `pipenv install && pipenv shell` 
* pré-traiter les données pour transformer le csv en json: `python in.py` 

Puis, pour lancer la conflation: `conflate pn_json.py -c results_pn.json -i pn.json --osm police.osm`

résultats:

```
12:03:16 Read 662 items from the dataset
12:04:41 Downloaded 12006 objects from OSM
12:04:41 Matched 585 points
12:04:41 Adding 77 unmatched dataset points
12:04:41 Deleted 0 and retagged 0 unmatched objects from OSM
12:04:41 Done
```

Le script `out.py` garde uniquement les éléments trouvés dans les deux jeux de données, et modifie un peu la structure pour pouvoir l'utiliser dans MapRoulette.

