#!/usr/bin/env python
# coding: utf-8

import requests
import json

#bbox_from_config = "48.817037474819,2.5778388977051,48.884134192869,2.7189445495605"
#zone_name = "Marne la Vallée, France"

bbox_from_config = "5.4717813427336,-0.45249938964844,5.8776490743906,0.11192321777344"
zone_name = "Accra, Ghana"

bbox_for_overpass = bbox_from_config

bbox = bbox_from_config.split(',')
bbox_for_osmose = "{},{},{},{}".format(bbox[1],bbox[0],bbox[3], bbox[2])


osmose_9014 = "http://osmose.openstreetmap.fr/fr/api/0.3beta/issues?full=true&item=9014&bbox={}".format(bbox_for_osmose)
osmose_1260 = "http://osmose.openstreetmap.fr/fr/api/0.3beta/issues?full=true&item=1260&bbox={}".format(bbox_for_osmose)
osmose_2140 = "http://osmose.openstreetmap.fr/fr/api/0.3beta/issues?full=true&item=2140&bbox={}".format(bbox_for_osmose)


osmose_call = requests.get(osmose_9014)
if osmose_call.status_code != 200:
    print("erreur osmose 9014 : {}".format(osmose_call.status_code))
all_issues = osmose_call.json()['issues']

osmose_call = requests.get(osmose_2140)
if osmose_call.status_code != 200:
    print("erreur osmose 2140 : {}".format(osmose_call.status_code))
all_issues += osmose_call.json()['issues']

osmose_call = requests.get(osmose_1260)
if osmose_call.status_code != 200:
    print("erreur osmose 1260 : {}".format(osmose_call.status_code))
all_issues += osmose_call.json()['issues']

def is_geom_issue(issue_item, issue_classs):
    if issue_item == 1260 and issue_classs in [1,2]:
        return True
    return False

def is_structural_issue(issue_item, issue_classs):
    if issue_item == 1260 and issue_classs in [3,4]:
        return True
    if issue_item == 2140 and issue_classs in [21401, 21411, 21412]:
        return True
    if issue_item == 9014 and issue_classs in [9014002]:
        return True
    return False

def is_line_metata_issue(issue_item, issue_classs):
    if issue_item == 1260 and issue_classs in [5]:
        return True
    if issue_item == 2140 and issue_classs in [21402, 21403, 21404, 21405]:
        return True
    if issue_item == 9014 and issue_classs in [9014009, 9014010, 9014013, 9014014]:
        return True
    return False

def is_stop_metata_issue(issue_item, issue_classs):
    if issue_item == 9014 and issue_classs in [9014006, 9014007, 9014008]:
        return True
    return False

def is_opendata_issue(issue_item, issue_classs):
    if issue_item == 8040:
        return True
    return False



geom_issues = []
metadata_issues = []
line_metadata_issues = []
stop_metadata_issues = []
opendata_issues = []
structural_issues = []

for issue in all_issues:
    if is_line_metata_issue(int(issue['item']), issue['classs']):
        line_metadata_issues.append(issue)
    elif is_geom_issue(int(issue['item']), issue['classs']):
        geom_issues.append(issue)
    elif is_structural_issue(int(issue['item']), issue['classs']):
        structural_issues.append(issue)
    elif is_opendata_issue(int(issue['item']), issue['classs']):
        opendata.append(issue)
    elif is_stop_metata_issue(int(issue['item']), issue['classs']):
        stop_metadata_issues.append(issue)
    else :
        print(issue)




overpass_base_url = "http://overpass-api.de/api/interpreter?data="
overpass_query_part_for_lines = '[out:json];relation["type"="route"]({});relation["type"="route_master"](br);out meta;'.format(bbox_for_overpass)
overpass_query_part_for_routes = '[out:json];relation["type"="route"]({});out meta;'.format(bbox_for_overpass)
overpass_query_part_for_bus_stop_count = '[out:json];node["highway"="bus_stop"]({});out count;'.format(bbox_for_overpass)
#TODO : créer requêtes pour les autres modes

lines_call = requests.get(overpass_base_url + overpass_query_part_for_lines)
if lines_call.status_code != 200:
    print("erreur overpass :{}".format(lines_call.status_code))

routes_call = requests.get(overpass_base_url + overpass_query_part_for_routes)
if routes_call.status_code != 200:
    print("erreur overpass :{}".format(routes_call.status_code))

all_routes = routes_call.json()["elements"]
all_lines = lines_call.json()["elements"]

modes_list = [elem["tags"]["route_master"] for elem in all_lines if "route_master" in elem['tags']]
modes_list += [elem["tags"]["route"] for elem in all_routes if "route" in elem['tags']]
modes_list = list(set(modes_list))

networks_list = [elem["tags"]["network"] for elem in all_lines + all_routes if "network" in elem['tags']]
networks_list = list(set(networks_list))

operators_list = [elem["tags"]["operator"] for elem in all_lines + all_routes if "operator" in elem['tags']]
operators_list = list(set(operators_list))


if 'bus' in modes_list:
    bus_stop_call = requests.get(overpass_base_url + overpass_query_part_for_bus_stop_count)
    if bus_stop_call.status_code != 200:
        print("erreur overpass :{}".format(bus_stop_call.status_code))
    stops_count = bus_stop_call.json()['elements'][0]['tags']['nodes']

stops_count



all_objects = ["r{}".format(line['id']) for line in all_lines] + ["r{}".format(route['id']) for route in all_routes]


values = {
    'zone_name': zone_name,
    'operators_count' : len(operators_list),
    'networks_count' : len(networks_list),
    'lines_count' : len(all_lines),
    'routes_count' : len(all_routes),
    'stops_count' : stops_count,
    'Osmose_link' : "http://osmose.openstreetmap.fr/fr/errors/?item=9014,2140,1260&limit=500&bbox={}".format(bbox_for_osmose),
    'JOSM_link' : "http://localhost:8111/load_object?new_layer=true&relation_members=true&objects="+",".join(all_objects),
    'structural_issues_count': len(structural_issues),
    'geom_issues_count': len(geom_issues),
    'line_metadata_issues_count': len(line_metadata_issues),
    'stop_metadata_issues_count': len(stop_metadata_issues),
    'opendata_issues_count': len(opendata_issues)
}


report = """
{zone_name} :

Définition de la zone :
{lines_count} lignes

{networks_count} réseaux
{operators_count} transporteurs

Bus :
{routes_count} parcours de bus
{stops_count} arrêts de bus

TODO : faire des graphiques :
(nb de lignes par mode, nb d'arrêts par mode, nb de lignes par réseau, nb de lignes par transporteur)

Qualité :
Erreurs structurelles : {structural_issues_count}
Erreurs sur les métadonnées des lignes : {line_metadata_issues_count}
Erreurs sur les métadonnées des arrêts : {stop_metadata_issues_count}
Erreurs sur la géométrie : {geom_issues_count}

Voir les erreurs dans Osmose : {Osmose_link}

Charger tous les objets de la zone dans JOSM : {JOSM_link}


""".format(**values)

print(report)
