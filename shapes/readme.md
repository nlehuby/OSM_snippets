#Script d'extraction du tracé de ligne / parcours / circulation de bus à partir des données OSM



##TODO

* vérifier comment est réalisée la fusion des chemins par le module shapely :
  * quel comportement pour les chemins à l'envers (quand les noeuds ne sont tracés pas dans le sens de circulation de la ligne) ?
  * quel comportement lorsqu'il y a un trou dans les données OSM ?
  * quel comportement pour un rond-point (ou une route) non découpée ? est-ce qu'on a un multilinestring ?

* faire une interface propre pour avoir la sortie en WKT / Geojson et au format shapes.txt du GTFS
* tester et vérifier sur une plus grande variété de relations OSM
