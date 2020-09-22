# Bus Angoulême

Faciliter la mise à jour des données OpenStreetMap à partir de fichiers tiers de qualité constitués et maintenus par des acteurs locaux.

* Septembre 2019 : [challenge MapRoulette](https://maproulette.org/challenge/8954)
* Mai 2020 : à venir

Puis, pour lancer la conflation: `conflate bus_stops.py -c results.json -i mobius.geojson --osm bus.osm`

résultats:

```
10:06:31 Read 2385 items from the dataset
10:06:31 Downloaded 1861 objects from OSM
10:06:32 Matched 1577 points
10:06:32 Removed 57 unmatched duplicates
10:06:32 Adding 751 unmatched dataset points
10:06:32 Deleted 284 and retagged 0 unmatched objects from OSM
10:06:32 Done
```

Le script `out.py` permet de ne conserver que certaines catégories de changements, pour faire des challenges MapRoulette.

Ne pas oublier de publier le jeu de données complet.

