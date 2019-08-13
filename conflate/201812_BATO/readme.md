# Arrêts de bus

L'objectif est d'extraire les arrêts présents dans des fichiers open data mais inexistants dans OpenStreetMap afin d'en faire un challenge maproulette.

on part des données open data extraites à l'aide du projet BATO (avec le détail des modes de transport) : https://github.com/nlehuby/bato_collecte/

on ne considère que les données issues des GTFS.

on les sépare par mode de transports : `xsv partition transport_mode data BATO_GTFS.csv`

on les regroupe par départements afin d'en faire des fichiers plus digestes (voir le notebook `partition_by_ddtm`)

on les sépare par département : `xsv partition --filename BATO_{}.csv nom . BATO_by_regions.csv`

puis on effectue la conflation département par département (voir le notebook ` conflate_by_dptm_plus_retraitement` )

Le fichier de sortie `results_final.json` peut être envoyé sur Maproulette.

# TODO

- retirer les arrêts de car TER qui sont vraiment top mal géolocalisés dans les données open data ?

# Volumétries
## Avril 2019
6 016 arrêts de bus à retrouver

https://maproulette.org/browse/challenges/4208

![image](https://pbs.twimg.com/media/EAbltTfUwAEV9NU?format=jpg&name=large)

Les résultats restent mitigés avec cette méthode : près de la moitié des objets proposés ne sont pas visibles sur l'imagerie aérienne ou sur Mapillary et ne peuvent donc être ajoutés.
