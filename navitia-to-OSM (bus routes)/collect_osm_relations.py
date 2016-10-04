#-------------------------------------------------------------------------------
# Author:      nlehuby
#
# Created:     28/01/2015
# Copyright:   (c) nlehuby 2015
# Licence:     MIT
#-------------------------------------------------------------------------------
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import re
import csv
import json

#paramétrage
overpass_base_url = "http://overpass-api.de/api/interpreter"

def collect_relations_from_wiki(wiki_url):
    """
    consulte la page de wiki passée en paramètre et extrait tous les liens de relations OSM
    """
    page = requests.get(wiki_url)
    liste_relations = re.findall(r'href="//www.openstreetmap.org/relation/(\w+)"', page.text)
    liste_relations += re.findall(r'href="//openstreetmap.org/relation/(\w+)"', page.text)
    liste_relations = list(set(liste_relations))
    return liste_relations

def persist_list_to_csv(liste, nom_fichier):
    """
    enregistre une liste au format csv
    """
    with open(nom_fichier, 'w') as f:
        for elem in liste :
            f.write("{}\n".format(elem))

def analyse_relation_list(fichier_a_analyser):
    """
    parcourt un fichier contenant des id de relations
    appelle Overpass pour chaque relation
    crée des listes de données nécessitant des corrections
    crée une liste avec numéro de ligne, nom et id
    """

    relations_lignes = []
    relations_routes = []
    relations_hors_sujet = []
    routes_sans_name = []
    routes_sans_ref = []
    routes_sans_operator = []
    routes_sans_network = []
    routes_sans_from = []
    routes_sans_to = []
    routes_sans_colour = []


    with open(fichier_a_analyser, "r") as mon_fichier:
        for elem in mon_fichier :
            print(">> {}".format(elem))
            relation_param = '[out:json][timeout:25];relation({});out;'.format(elem)
            resp = requests.get(overpass_base_url, params={'data': relation_param})
            if resp.status_code != 200:
                print ("KO à l'appel")
                relations_hors_sujet.append(int(elem))
                continue
            mon_json = resp.json()
            if not 'elements' in mon_json :
                print ("KO sur elements")
                relations_hors_sujet.append(int(elem))
                continue
            if len(mon_json['elements']) == 0 :
                print ("KO sur nb elements")
                relations_hors_sujet.append(int(elem))
                continue

            if "tags" in mon_json['elements'][0]:
                ma_relation = mon_json['elements'][0]['tags']
            else :
                print ("KO sur tags")
                relations_hors_sujet.append(int(elem))
                continue

            if not "type" in ma_relation:
                print ("KO sur type")
                relations_hors_sujet.append(int(elem))
                continue
            if ma_relation['type'] != "route" :
                print ("KO sur type = route")
                relations_hors_sujet.append(int(elem))
                continue

            ma_route = {}
            if not 'from' in ma_relation:
                routes_sans_from.append(int(elem))
            if not 'to' in ma_relation:
                routes_sans_to.append(int(elem))
                ma_route['destination'] = ''
            else :
                ma_route['destination'] = ma_relation['to']
            if not 'operator' in ma_relation:
                routes_sans_operator.append(int(elem))
            if not 'network' in ma_relation:
                routes_sans_network.append(int(elem))
                ma_route['network'] = ''
            else :
                ma_route['network'] = ma_relation['network']
            if not 'colour' in ma_relation:
                routes_sans_colour.append(int(elem))
            if not 'name' in ma_relation:
                routes_sans_name.append(int(elem))
            else :
                ma_route['name'] = ma_relation['name']
            if not 'ref' in ma_relation:
                routes_sans_ref.append(int(elem))
            else :
                ma_route['code'] = ma_relation['ref']
            stop_count = 0
            for a_member in mon_json['elements'][0]['members']:
                if a_member['type'] == 'node':
                    stop_count += 1
            ma_route['stop_count'] = stop_count
            ma_route['osm_id'] = int(elem)
            relations_routes.append(ma_route)

            print (ma_route)


    persist_list_to_csv(routes_sans_from, "collecte/analyse/routes_sans_from.csv")
    persist_list_to_csv(routes_sans_to, "collecte/analyse/routes_sans_to.csv")
    persist_list_to_csv(routes_sans_network, "collecte/analyse/routes_sans_network.csv")
    persist_list_to_csv(routes_sans_operator, "collecte/analyse/routes_sans_operator.csv")
    persist_list_to_csv(routes_sans_colour, "collecte/analyse/routes_sans_colour.csv")
    persist_list_to_csv(routes_sans_name, "collecte/analyse/routes_sans_name.csv")
    persist_list_to_csv(routes_sans_ref, "collecte/analyse/routes_sans_ref.csv")
    persist_list_to_csv(relations_hors_sujet, "collecte/analyse/relations_hors_sujet.csv")

    headers = ['osm_id', 'code', 'name', 'destination', 'stop_count', 'network']
    with open("collecte/relations_routes.csv",'w') as f:
        dw = csv.DictWriter(f, delimiter=',', fieldnames=headers)
        for row in relations_routes:
            dw.writerow(row)

def generate_autocomplete_osm_json():
    """ depréciée. Cette opération est effectuée directement dans route_to_html """
    fichier_json = 'collecte/osm_parcours.json'
    objet_json = {"parcours_osm":[]}

    with open("collecte/relations_routes.csv",'r') as f:
        reader = csv.reader(f)
        for row in reader :
            print (row[0])
            parcours = {}
            parcours['value'] = row[0]
            parcours['label'] = "[{}] {} > {}".format(row[-1], row[1], row[3])
            objet_json['parcours_osm'].append(parcours)

    json.dump(objet_json, open(fichier_json, "w"), indent=4)

if __name__ == '__main__':

    tous_les_bus = []
    tous_les_bus += collect_relations_from_wiki('https://wiki.openstreetmap.org/wiki/WikiProject_France/Noctilien')
    tous_les_bus += collect_relations_from_wiki('https://wiki.openstreetmap.org/wiki/WikiProject_France/Bus_RATP')
    tous_les_bus += collect_relations_from_wiki('https://wiki.openstreetmap.org/wiki/WikiProject_France/Bus_TRA')
    tous_les_bus += collect_relations_from_wiki('https://wiki.openstreetmap.org/wiki/WikiProject_France/Bus_STRAV')
    tous_les_bus += collect_relations_from_wiki('https://wiki.openstreetmap.org/wiki/WikiProject_France/Bus_TICE')
    tous_les_bus += collect_relations_from_wiki('https://wiki.openstreetmap.org/wiki/WikiProject_France/Bus_SETRA')
    tous_les_bus += collect_relations_from_wiki('https://wiki.openstreetmap.org/wiki/WikiProject_France/Bus_SITUS')
    tous_les_bus += collect_relations_from_wiki('https://wiki.openstreetmap.org/wiki/WikiProject_France/Bus_DM')
    tous_les_bus += collect_relations_from_wiki('https://wiki.openstreetmap.org/wiki/WikiProject_France/Bus_Paladin')
    tous_les_bus += collect_relations_from_wiki('https://wiki.openstreetmap.org/wiki/WikiProject_France/Bus_Mobicaps')
    tous_les_bus += collect_relations_from_wiki("https://wiki.openstreetmap.org/wiki/WikiProject_France/Bus_Pep's")

    persist_list_to_csv(list(set(tous_les_bus)), "collecte/liste_relations.csv")
    analyse_relation_list("collecte/liste_relations.csv")
