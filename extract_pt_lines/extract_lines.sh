#!/bin/bash

set -ev

# install osm-transit-extractor
#wget https://github.com/CanalTP/osm-transit-extractor/releases/download/v0.1.0/osm_transit_extractor_v0.1.0-x86_64-linux.zip
#unzip osm_transit_extractor_v0.1.0-x86_64-linux.zip

# install xsv
#wget https://github.com/BurntSushi/xsv/releases/download/0.13.0/xsv-0.13.0-x86_64-unknown-linux-musl.tar.gz
#tar -zxvf xsv-0.13.0-x86_64-unknown-linux-musl.tar.gz

wget http://download.geofabrik.de/europe/france-latest.osm.pbf --no-verbose --output-document=data.osm.pbf 2>&1

osm_transit_extractor -i data.osm.pbf

cat osm-transit-extractor_lines.csv|xsv select 1-8 |xsv search -s shape '^$' -v > lines_from_osm.csv
