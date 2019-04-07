# Arrêts de transports

on partira des données extraites par le projet BATO : https://github.com/BATO-FR/bato_collecte/tree/23365a17fbf9690810620c26dabdd6664971ede8

on les sépare par mode transports :
`cat BATO_GTFS.csv|xsv partition --filename BATO_gtfs_{}.csv transport_mode .`

il faut adapter le profil en précisant les tags OSM à utiliser pour chaque mode.

Puis, pour lancer la conflation: `conflate BATO.py -c results.json -i BATO_gtfs_3.csv --osm bus.osm` ou `conflate BATO.py -c results.json -i BATO_gtfs_1.csv --osm subway.osm`

# TODO
Pour le moment, la requête overpass ne passe pas dès que la volumétrie est un peu grosse (donc pas sur les bus par exemple).
Il est donc nécessaire de découper le fichier à nouveau (xsv partition sur la source par exemple) ou de trouver un meilleur moyen pour télécharger les données OSM.

conflate BATO.py -c results.json -i BATO_gtfs_idf_3.csv --osm bus.osm
20:44:07 Dataset points duplicate each other: opendata_GTFS_fr-idf-OIFStopPoint:8760012:800:N1543 and opendata_GTFS_fr-idf-OIFStopPoint:8760012:800:N1503
20:44:07 Dataset points duplicate each other: opendata_GTFS_fr-idf-OIFStopPoint:8760657:800:N1543 and opendata_GTFS_fr-idf-OIFStopPoint:76:2473
20:44:07 Dataset points duplicate each other: opendata_GTFS_fr-idf-OIFStopPoint:8760657:800:N1543 and opendata_GTFS_fr-idf-OIFStopPoint:76:2483
20:44:07 Dataset points duplicate each other: opendata_GTFS_fr-idf-OIFStopPoint:8760656:800:N1543 and opendata_GTFS_fr-idf-OIFStopPoint:76:6683
20:44:07 Dataset points duplicate each other: opendata_GTFS_fr-idf-OIFStopPoint:8760656:800:N1543 and opendata_GTFS_fr-idf-OIFStopPoint:76:6673
20:44:21 Found 19809 duplicates in the dataset
20:44:21 Read 40005 items from the dataset
20:44:43 Downloaded 31191 objects from OSM
20:54:10 Matched 29990 points
20:54:10 Removed 6988 unmatched duplicates
20:54:10 Adding 3027 unmatched dataset points
20:54:10 Deleted 0 and retagged 0 unmatched objects from OSM
20:54:12 Done


out_new.py permet de garder que les éléments à créer dans OSM

BATO_again.py est un profil conflate pour faire une deuxième conflation du résultats avec OSM (car il reste des doublons d'opendata proposés comme à ajouter dans OSM alors qu'ils existent déjà)

puis, pour exploiter ça, on peut importer le fichier dans maproulette (il faut le nettoyer encore un peu pour retirer les tags inutiles) en expliquant bien dans le challenge d'utiliser les imageries à disposition pour vérifier la présence de l'arrêt.
