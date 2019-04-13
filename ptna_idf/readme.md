Quelques bribes de codes pour initialiser PTNA à partir des données GTFS

Le fichier d'entrée est constitué en fusionnant le fichier routes.txt avec le fichier agency.txt ainsi qu'avec un fichier de mapping des modes GTFS vers ceux d'OSM.

> head bus_by_networks.csv 
route_short_name,osm_transport_mode,agency_name
F,bus,Pays de Meaux
G,bus,Pays de Meaux
J,bus,Pays de Meaux
I,bus,Pays de Meaux
Es,bus,Pays de Meaux

