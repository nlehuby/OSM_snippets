# Arrêts de transports

on partira des données extraites par le projet BATO : https://github.com/BATO-FR/bato_collecte/tree/23365a17fbf9690810620c26dabdd6664971ede8

on les sépare par mode transports :
`cat BATO_GTFS.csv|xsv partition --filename BATO_gtfs_{}.csv transport_mode .`

il faut adapter le profil en précisant les tags OSM à utiliser pour chaque mode.

Puis, pour lancer la conflation: `conflate BATO.py -c results.json -i BATO_gtfs_3.csv --osm bus.osm` ou `conflate BATO.py -c results.json -i BATO_gtfs_1.csv --osm subway.osm`

# TODO
Pour le moment, la requête overpass ne passe pas dès que la volumétrie est un peu grosse (donc pas sur les bus par exemple).
Il est donc nécessaire de découper le fichier à nouveau (xsv partition sur la source par exemple) ou de trouver un meilleur moyen pour télécharger les données OSM.
