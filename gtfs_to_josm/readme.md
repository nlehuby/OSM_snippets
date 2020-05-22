# GTFS to JOSM

Ce script prend un GTFS en entrée et fabrique un geojson pour chaque séquence d'arrêt qui peut ensuite être utilisé dans JOSM pour cartographier la ligne.
Voir aussi [GTFS geo](https://github.com/nlehuby/gtfs_geo) qui industrialise cette transformation (cli / web).

Si des shapes de bonne qualité sont fournies, on peut tenter un mapmatching et récupérer dans JOSM les chemins OSM à ajouter dans les relations.

Des résultats de ce script sont visibles ici :
* [réseau de Limoges](https://github.com/nlehuby/jubilant-octo-broccoli/blob/master/Limoges/readme.md)
* [réseau IDF Pays Fertois](https://github.com/nlehuby/jubilant-octo-broccoli/blob/master/PaysFertois/readme.md) (avec mapmatching)
