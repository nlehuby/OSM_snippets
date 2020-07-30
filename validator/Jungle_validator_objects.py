#!/usr/bin/env python
# coding: utf-8

#-------------------------------------------------------------------------------
# Author:      nlehuby
#
# Copyright:   (c) Jungle Bus 2020
# Licence:     MIT
#-------------------------------------------------------------------------------

import requests
import json
import csv

project_name = "Abidjan"
project_unroll_url = "https://jungle-bus.github.io/unroll/?project=Abidjan"
project_home = "https://wiki.openstreetmap.org/wiki/FR:WikiProject_C%C3%B4te_d'Ivoire/Transport_Abidjan"
route_master_file = "osm-transit-extractor_lines.csv"
route_file = "osm-transit-extractor_routes.csv"

osmose_url= "http://osmose.openstreetmap.fr/fr/api/0.3/issues?osm_type=relation&osm_id={}&full=true"
josm_url = "http://localhost:8111/load_object?relation_members=true&objects="


osm_routes = []
osm_lines = []

with open(route_master_file) as lines_file:
    tt = csv.DictReader(lines_file)
    osm_lines = list(tt)

with open(route_file) as routes_file:
    tt = csv.DictReader(routes_file)
    osm_routes = list(tt)

osm_relations = [line['line_id'].split(":")[-1] for line in osm_lines] + [line['route_id'].split(":")[-1] for line in osm_routes]

seems_ok = []
to_check = []
errors = {}

for a_relation in osm_relations:
    osmose_ = osmose_url.format(a_relation)
    osmose_call = requests.get(osmose_)
    osmose_results = osmose_call.json()['issues']
    if not osmose_results:
        seems_ok.append(a_relation)
        continue

    for error in osmose_results:
        error_type = "{}_{}".format(error['item'], error['class'])
        if error_type in ['2140_21404']:
            if len(osmose_results) == 1:
                seems_ok.append(a_relation)
            continue
        if error_type not in errors :
            output_error = {"title":error['title'],
                            "subtitle": error['subtitle'],
                            "objects": []
                           }
            errors[error_type] = output_error
        errors[error_type]["objects"].append(a_relation)
        to_check.append(a_relation)

seems_ok_objects = ["r{}".format(relation) for relation in seems_ok]
josm_ok = "{}{}".format(josm_url, ",".join(seems_ok_objects))

to_check_objects = ["r{}".format(relation) for relation in to_check]
josm_to_check = "{}{}".format(josm_url, ",".join(to_check_objects))

print("# Analyse qualité pour {}".format(project_name))

print("- [Voir la documentation]({})".format(project_home))
print("- [Explorer les lignes]({})".format(project_unroll_url))
print("")
print("")
print("## Erreurs")
print("- {} objets".format(len(osm_relations)))
print("- {} objets en erreur : [Charger dans JOSM]({})".format(len(to_check_objects),josm_to_check))
print("- {} objets a priori ok : [Charger dans JOSM]({})".format(len(seems_ok_objects),josm_ok))
print("")

print("## Liste des erreurs")

for error in errors.values():
    title = error["title"]["auto"]
    subtitle = ""
    if error["subtitle"]:
        subtitle = error["subtitle"]["auto"]
    object_list = ["- [{}]({}r{})\n".format(elem,josm_url,elem) for elem in error["objects"]]

    print("""
#### {}

{}

Objet(s): 

{}
    """.format(title, subtitle, "".join(object_list)))

