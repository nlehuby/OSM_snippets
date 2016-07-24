osmosis --read-pbf ile_de_france.osm.pbf --tf accept-relations route=bus --used-way --used-node --write-pbf bus.osm.pbf

osmosis --read-pbf bus.osm.pbf --tf accept-relations type=route --used-way --used-node --write-pbf bus2.osm.pbf

osmconvert bus2.osm.pbf --csv="@id ref name to nb_stops network operator colour public_transport:version type route" --csv-separator=";" --csv-headline > bus.csv

cat bus.csv |xsv search -d ';' -s 11 bus > bus_routes.csv
