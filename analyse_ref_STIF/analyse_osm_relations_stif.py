#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import csv
import json
import xmltodict
import datetime
from params import navitia_API_key as TOKEN
from collections import Counter
from copy import deepcopy

# paramétrage
navitia_API_key = TOKEN
navitia_base_url = "http://api.navitia.io/v1/coverage/fr-idf"


def get_osm_lines(file_name):
    with open(file_name, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)

def get_opendata_info(code_type, code_value):
    navitia_info = {}
    appel_nav = requests.get(navitia_base_url + "/lines?filter=line.has_code({},{})".format(
        code_type, code_value), headers={'Authorization': navitia_API_key})
    if appel_nav.status_code != 200:
        return "échec à l'appel navitia", navitia_info
    nb_result = appel_nav.json()['pagination']['total_result']
    if nb_result != 1:
        return "plusieurs lignes correspondent dans l'opendata", navitia_info
    navitia_info['network'] = appel_nav.json()['lines'][0]['network']['name']
    navitia_info['mode'] = appel_nav.json(
    )['lines'][0]['commercial_mode']['name']
    navitia_info['color'] = appel_nav.json()['lines'][0]['color']
    navitia_info['navitia_id'] = appel_nav.json()['lines'][0]['id']
    navitia_info['name'] = appel_nav.json()['lines'][0]['name']
    navitia_info['code'] = appel_nav.json()['lines'][0]['code']

    # on récupère les coordonnées d'un arrêt de la ligne au hasard
    appel_nav = requests.get(navitia_base_url + "/lines/{}/stop_points?count=1".format(
        navitia_info['navitia_id']), headers={'Authorization': navitia_API_key})
    if appel_nav.status_code != 200:
        return "échec à l'appel navitia sur les arrêts", navitia_info
    navitia_info['latitude'] = appel_nav.json(
    )['stop_points'][0]['coord']['lat']
    navitia_info['longitude'] = appel_nav.json(
    )['stop_points'][0]['coord']['lon']
    return "ok", navitia_info


def create_opendata_csv(osm_lines):
    navitia_lines = []
    osm_lines_with_errors = []
    for row in osm_lines :
        if row['osm:ref:FR:STIF:ExternalCode_Line']:
            status, navitia_line = get_opendata_info(
                "source", row['osm:ref:FR:STIF:ExternalCode_Line'])
            if status != "ok":
                row["error"] = status
                row['osm_id'] = row['line_id']
                osm_lines_with_errors.append(row)
            else:
                navitia_line['osm_id'] = row['line_id']
                navitia_lines.append(navitia_line)

    headers = ['osm_id', 'mode', 'network', 'color',
               'navitia_id', 'name', 'code', 'latitude', 'longitude']
    with open("analyse/route_master_opendata.csv", 'w') as f:
        dw = csv.DictWriter(f, delimiter=',', fieldnames=headers)
        dw.writeheader()
        for row in navitia_lines:
            dw.writerow(row)

    headers = ['osm_id', 'name', 'ref', 'error']
    osm_lines = [dict((k, result.get(k, None)) for k in headers)
                 for result in osm_lines_with_errors]
    with open("analyse/route_master_opendata_errors.csv", 'w') as f:
        dw = csv.DictWriter(f, delimiter=',', fieldnames=headers)
        dw.writeheader()
        for row in osm_lines:
            dw.writerow(row)

    return navitia_lines


def extract_common_values_by_networks(osm_lines, opendata_lines):
    networks = {}
    operators = {}
    for a_navitia_line in opendata_lines:
        nav_network = networks.setdefault(a_navitia_line['network'], [])
        nav_operator = operators.setdefault(a_navitia_line['network'], [])
        osm_match = [a_line for a_line in osm_lines if a_line['line_id']
                     == a_navitia_line['osm_id']]
        nav_network.append(osm_match[0]['network'])
        nav_operator.append(osm_match[0]['operator'])
    return {"networks": networks, "operators": operators}


def get_most_common_value(stat_info, tag, opendata_network):
    c = Counter(stat_info[tag + 's'][opendata_network])
    return c.most_common(1)[0][0]


def map_modes(opendata_mode):
    mapping = {"Bus": "bus", "RapidTransit": "train",
               "Tramway": "tram", "Metro": "subway"}
    return mapping[opendata_mode]


def get_errors(osm_lines, opendata_lines):
    stats = extract_common_values_by_networks(osm_lines, opendata_lines)
    # get_most_common_value(stats, "network", "Noctilien")
    # get_most_common_value(stats, "operator", "Noctilien")

    errors = []
    opendata_deduplicated = []
    for an_osm_line in osm_lines:
        an_osm_line['osm_id'] = an_osm_line['line_id'].split(':')[-1]
        if not an_osm_line['osm:ref:FR:STIF:ExternalCode_Line']:
            continue
        if an_osm_line['osm:ref:FR:STIF:ExternalCode_Line'] not in opendata_deduplicated:
            opendata_deduplicated.append(
                an_osm_line['osm:ref:FR:STIF:ExternalCode_Line'])
        else:
            error = {"id": an_osm_line['osm_id']}
            error['label'] = "Il y a plusieurs lignes dans OSM qui ont ce même ref:FR:STIF:ExternalCode_Line ({})".format(
                an_osm_line['osm:ref:FR:STIF:ExternalCode_Line'])
            error['lat'], error['lon'] = opendata_line['latitude'], opendata_line['longitude']
            errors.append(error)
        opendata_matching_lines = [
            a_line for a_line in opendata_lines if an_osm_line['line_id'] == a_line['osm_id']]
        if not opendata_matching_lines:
            continue
        opendata_line = opendata_matching_lines[0]
        if not an_osm_line['network']:
            error = {"id": an_osm_line['osm_id']}
            fix = get_most_common_value(
                stats, "network", opendata_line['network'])
            error['label'] = "la relation n'a pas de tag network."
            if fix != "":
                error['fix'] = [{"key": "network", "value": fix}]
                error['label'] = "la relation n'a pas de tag network. Valeur probable : " + fix
            error['lat'], error['lon'] = opendata_line['latitude'], opendata_line['longitude']
            errors.append(error)
        if not an_osm_line['operator']:
            error = {"id": an_osm_line['osm_id']}
            fix = get_most_common_value(
                stats, "operator", opendata_line['network'])
            error['label'] = "la relation n'a pas de tag operator."
            if fix != "":
                error['fix'] = [{"key": "operator", "value": fix}]
                error['label'] = "la relation n'a pas de tag operator. Valeur probable : " + fix
            error['lat'], error['lon'] = opendata_line['latitude'], opendata_line['longitude']
            errors.append(error)
        if not an_osm_line['colour'] and opendata_line['color'] not in ["000000", "0", ""]:
            error = {"id": an_osm_line['osm_id']}
            error['label'] = "la relation n'a pas de tag colour."
            fix = '#' + opendata_line['color']
            if opendata_line['color'] not in ["", "0", "000000"]:
                error['fix'] = [{"key": "colour", "value": fix}]
                error['label'] = "la relation n'a pas de tag colour. Valeur probable : " + fix
            error['lat'], error['lon'] = opendata_line['latitude'], opendata_line['longitude']
            # errors.append(error)
        if not an_osm_line['code']:
            error = {"id": an_osm_line['osm_id']}
            fix = opendata_line['code']
            error['label'] = "la relation n'a pas de tag ref. Valeur probable : " + fix
            error['lat'], error['lon'] = opendata_line['latitude'], opendata_line['longitude']
            error['fix'] = [{"key": "ref", "value": fix}]
            errors.append(error)
        if not an_osm_line['mode']:
            error = {"id": an_osm_line['osm_id']}
            fix = map_modes(opendata_line['mode'])
            error['label'] = "la relation n'a pas de tag route_master. Valeur probable : " + fix
            error['lat'], error['lon'] = opendata_line['latitude'], opendata_line['longitude']
            error['fix'] = [{"key": "route_master", "value": fix}]
            errors.append(error)

    return errors


def create_osmose_xml(errors):
    with open('osmose_issues_template.xml', 'r') as f:
        doc = xmltodict.parse(f.read())

    now = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    doc['analysers']['@timestamp'] = now
    doc['analysers']['analyser']['@timestamp'] = now
    doc['analysers']['analyser']['class']['@item'] = "8042"
    doc['analysers']['analyser']['class']['@tag'] = "transport en commun"
    doc['analysers']['analyser']['class']['@id'] = "1"
    doc['analysers']['analyser']['class']['@level'] = "3"
    doc['analysers']['analyser']['class']['classtext']['@lang'] = "fr"
    doc['analysers']['analyser']['class']['classtext'][
        '@title'] = "tag manquant sur une relation route_master (ligne de transport en commun)"

    for error in errors:
        current_osmose_error = deepcopy(
            doc['analysers']['analyser']['error'][0])
        current_osmose_error['relation']['@id'] = error['id']
        current_osmose_error['location']['@lat'] = error['lat']
        current_osmose_error['location']['@lon'] = error['lon']
        current_osmose_error['text']['@lang'] = "fr"
        current_osmose_error['text']['@value'] = error['label']
        current_osmose_error['fixes']['fix']['relation']['@id'] = error['id']
        if 'fix' in error:
            current_osmose_error['fixes']['fix']['relation']['tag']['@k'] = error['fix'][0]['key'] if 'key' in error['fix'][0] else ''
            current_osmose_error['fixes']['fix']['relation']['tag']['@v'] = error['fix'][0]['value'] if 'key' in error['fix'][0] else ''
        else:
            del current_osmose_error['fixes']

        doc['analysers']['analyser']['error'].append(current_osmose_error)

    # remove the template errors
    del doc['analysers']['analyser']['error'][0]
    del doc['analysers']['analyser']['error'][0]

    return xmltodict.unparse(doc, pretty=True)




if __name__ == '__main__':

    osm_lines = get_osm_lines('../STIF-to-OSM/data/lignes.csv')

    opendata_lines = create_opendata_csv(osm_lines)

    errors = get_errors(osm_lines, opendata_lines)

    xml = create_osmose_xml(errors)
    print("Il y a {} erreurs".format(len(errors)))

    with open("osmose_test.xml", "w") as xml_out_file:
        xml_out_file.write(xml)
