#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import re
import csv
import json
from params import navitia_API_key as TOKEN
from collections import Counter

#paramétrage
overpass_base_url = "http://overpass-api.de/api/interpreter"
navitia_API_key = TOKEN
navitia_base_url = "http://api.navitia.io/v1/coverage/fr-idf"

def get_navitia_info(code_type, code_value):
    navitia_info = {}
    appel_nav = requests.get(navitia_base_url + "/lines?filter=line.has_code({},{})".format(code_type, code_value), headers={'Authorization': navitia_API_key})
    if appel_nav.status_code != 200:
        print ("KO navitia")
    nb_result = appel_nav.json()['pagination']['total_result']
    if nb_result != 1:
        print ("/!\on a plusieurs lignes qui pourraient correspondre")
    navitia_info['network'] = appel_nav.json()['lines'][0]['network']['name']
    navitia_info['mode'] = appel_nav.json()['lines'][0]['commercial_mode']['name']
    navitia_info['color'] = appel_nav.json()['lines'][0]['color']
    return (navitia_info)

def create_navitia_csv():
    navitia_lines = []
    with open('../STIF-to-OSM/data/lignes.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['ref:FR:STIF:ExternalCode_Line']:
                navitia_line = get_navitia_info("source", row['ref:FR:STIF:ExternalCode_Line'])
                navitia_line['osm_id'] = row['@id']
                navitia_lines.append(navitia_line)

    headers = ['osm_id', 'mode', 'network', 'color']
    with open("collecte/analyse/relations_route_master.csv",'w') as f: #il manque un ptit navitia dans le nom quand même
        dw = csv.DictWriter(f, delimiter=',', fieldnames=headers)
        dw.writeheader()
        for row in navitia_lines:
            dw.writerow(row)

def extract_common_values_by_networks():
    with open('../STIF-to-OSM/data/lignes.csv', 'r') as f:
        reader = csv.DictReader(f)
        osm_lines = list(reader)
    with open('collecte/analyse/relations_route_master.csv', 'r') as f:
        reader = csv.DictReader(f)
        opendata_lines = list(reader)

    networks = {}
    operators = {}
    for a_navitia_line in opendata_lines:
        nav_network = networks.setdefault(a_navitia_line['network'], [])
        nav_operator = operators.setdefault(a_navitia_line['network'], [])
        osm_match = [a_line for a_line in osm_lines if a_line['@id'] == a_navitia_line['osm_id']]
        nav_network.append(osm_match[0]['network'])
        nav_operator.append(osm_match[0]['operator'])
    return {"networks" : networks, "operators" : operators}

def get_most_common_value(stat_info, tag, opendata_network):
    c = Counter(stat_info[tag + 's'][opendata_network])
    return c.most_common(1)[0][0]

def map_modes(opendata_mode):
    mapping = {"Bus": "bus", "RapidTransit":"train", "Tramway":"tram", "Metro":"subway"}
    return mapping[opendata_mode]

if __name__ == '__main__':

    get_navitia_info("source", "810:A")

    #create_navitia_csv()
    stats = extract_common_values_by_networks()
    # get_most_common_value(stats, "network", "Noctilien")
    # get_most_common_value(stats, "operator", "Noctilien")

    with open('collecte/analyse/relations_route_master.csv', 'r') as f:
        reader = csv.DictReader(f)
        opendata_lines = list(reader)

    errors = {}
    with open('../STIF-to-OSM/data/lignes.csv', 'r') as f:
        reader = csv.DictReader(f)
        for an_osm_line in reader :
            error = []
            if an_osm_line['ref:FR:STIF:ExternalCode_Line']:
                opendata_line = [a_line for a_line in opendata_lines if an_osm_line['@id'] == a_line['osm_id']][0]
            if not an_osm_line['network']:
                error.append("la ligne n'a pas de tag network. Valeur probable : " + get_most_common_value(stats, "network", opendata_line['network']))
            if not an_osm_line['operator']:
                error.append("la ligne n'a pas de tag operator. Valeur probable : " + get_most_common_value(stats, "operator", opendata_line['network']))
            if not an_osm_line['colour']:
                error.append("la ligne n'a pas de tag colour. Valeur probable : " + opendata_line['color'])
            if not an_osm_line['route_master']:
                error.append("la ligne n'a pas de tag route_master. Valeur probable : " + map_modes(opendata_line['mode']))

            if error:
                errors[an_osm_line['@id']] = error

    for elem in errors.items() :
        print(elem[0])
        for err in elem[1]:
            print (">> " + err)
