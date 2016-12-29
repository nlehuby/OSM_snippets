#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import re
import csv
import json
import xmltodict
import datetime
from params import navitia_API_key as TOKEN
from collections import Counter
from copy import deepcopy

#paramétrage
navitia_API_key = TOKEN
navitia_base_url = "http://api.navitia.io/v1/coverage/fr-idf"

def get_opendata_info(code_type, code_value):
    navitia_info = {}
    appel_nav = requests.get(navitia_base_url + "/lines?filter=line.has_code({},{})".format(code_type, code_value), headers={'Authorization': navitia_API_key})
    if appel_nav.status_code != 200:
        print ("KO navitia " + code_value)
        return navitia_info
    nb_result = appel_nav.json()['pagination']['total_result']
    if nb_result != 1:
        print ("/!\ on a plusieurs lignes qui pourraient correspondre")
        return navitia_info
    navitia_info['network'] = appel_nav.json()['lines'][0]['network']['name']
    navitia_info['mode'] = appel_nav.json()['lines'][0]['commercial_mode']['name']
    navitia_info['color'] = appel_nav.json()['lines'][0]['color']
    navitia_info['navitia_id'] = appel_nav.json()['lines'][0]['id']
    
    # on récupère les coordonnées d'un arrêt de la ligne au hasard
    appel_nav = requests.get(navitia_base_url + "/lines/{}/stop_points?count=1".format(navitia_info['navitia_id']), headers={'Authorization': navitia_API_key})
    navitia_info['latitude'] = appel_nav.json()['stop_points'][0]['coord']['lat']
    navitia_info['longitude'] = appel_nav.json()['stop_points'][0]['coord']['lon']
    return (navitia_info)

def create_opendata_csv():
    navitia_lines = []
    with open('../STIF-to-OSM/data/lignes.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['ref:FR:STIF:ExternalCode_Line']:
                navitia_line = get_opendata_info("source", row['ref:FR:STIF:ExternalCode_Line'])
                if navitia_line == {}: continue
                navitia_line['osm_id'] = row['@id']
                navitia_lines.append(navitia_line)

    headers = ['osm_id', 'mode', 'network', 'color', 'navitia_id', 'latitude', 'longitude']
    with open("analyse/route_master_opendata.csv",'w') as f:
        dw = csv.DictWriter(f, delimiter=',', fieldnames=headers)
        dw.writeheader()
        for row in navitia_lines:
            dw.writerow(row)

def extract_common_values_by_networks():
    with open('../STIF-to-OSM/data/lignes.csv', 'r') as f:
        reader = csv.DictReader(f)
        osm_lines = list(reader)
    with open('collecte/analyse/route_master_opendata.csv', 'r') as f:
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

def get_errors ():
    stats = extract_common_values_by_networks()
    # get_most_common_value(stats, "network", "Noctilien")
    # get_most_common_value(stats, "operator", "Noctilien")

    with open('collecte/analyse/route_master_opendata.csv', 'r') as f:
        reader = csv.DictReader(f)
        opendata_lines = list(reader)

        errors = []
        with open('../STIF-to-OSM/data/lignes.csv', 'r') as f:
            reader = csv.DictReader(f)
            for an_osm_line in reader :
                if not an_osm_line['ref:FR:STIF:ExternalCode_Line']:
                    continue
                opendata_line = [a_line for a_line in opendata_lines if an_osm_line['@id'] == a_line['osm_id']][0]
                if not an_osm_line['network']:
                    fix = get_most_common_value(stats, "network", opendata_line['network'])
                    errors.append([an_osm_line['@id'],'network',fix,"la relation n'a pas de tag network. Valeur probable : " + fix,opendata_line['latitude'], opendata_line['longitude']])
                if not an_osm_line['operator']:
                    fix = get_most_common_value(stats, "operator", opendata_line['network'])
                    errors.append([an_osm_line['@id'],'operator',fix,"la relation n'a pas de tag operator. Valeur probable : " + fix,opendata_line['latitude'], opendata_line['longitude']])
                if not an_osm_line['colour'] and opendata_line['color'] != "000000":
                    fix = '#' + opendata_line['color']
                    errors.append([an_osm_line['@id'],'colour',fix,"la relation n'a pas de tag colour. Valeur probable : " + fix,opendata_line['latitude'], opendata_line['longitude']])
                if not an_osm_line['route_master']:
                    fix = map_modes(opendata_line['mode'])
                    errors.append([an_osm_line['@id'],'route_master',fix,"la relation n'a pas de tag route_master. Valeur probable : " + fix,opendata_line['latitude'], opendata_line['longitude']])

        return errors

def create_osmose_xml(errors):
    with open('osmose_issues_template.xml', 'r') as f:
        doc = xmltodict.parse(f.read())

    now = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    doc['analysers']['@timestamp'] = now
    doc['analysers']['analyser']['@timestamp'] = now
    doc['analysers']['analyser']['class']['@item'] = "1140"
    doc['analysers']['analyser']['class']['@tag'] = "transport en commun"
    doc['analysers']['analyser']['class']['@id'] = "1"
    doc['analysers']['analyser']['class']['@level'] = "3"
    doc['analysers']['analyser']['class']['classtext']['@lang'] = "fr"
    doc['analysers']['analyser']['class']['classtext']['@title'] = "tag manquant sur une relation route_master (ligne de transport en commun)"

    for error in errors :
        current_osmose_error = deepcopy(doc['analysers']['analyser']['error'][0])
        current_osmose_error['relation']['@id'] = error[0]
        current_osmose_error['location']['@lat'] = error[4]
        current_osmose_error['location']['@lon'] = error[5]
        current_osmose_error['text']['@lang'] = "fr"
        current_osmose_error['text']['@value'] = error[3]
        current_osmose_error['fixes']['fix']['relation']['@id'] = error[0]
        current_osmose_error['fixes']['fix']['relation']['tag']['@k'] = error[1]
        current_osmose_error['fixes']['fix']['relation']['tag']['@v'] = error[2]

        doc['analysers']['analyser']['error'].append(current_osmose_error)

    #remove the template errors
    del doc['analysers']['analyser']['error'][0]
    del doc['analysers']['analyser']['error'][0]

    return xmltodict.unparse(doc, pretty=True)


if __name__ == '__main__':

    create_opendata_csv()

    # errors = get_errors()
    # xml = create_osmose_xml(errors)
    #
    # print(xml)
