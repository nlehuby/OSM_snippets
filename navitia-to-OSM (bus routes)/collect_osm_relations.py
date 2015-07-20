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

#paramétrage
overpass_base_url = "http://api.openstreetmap.fr/oapi/interpreter"

def collect_relations_from_wiki():
    """
    consulte la page de wiki sur les bus RATP et extrait tous les liens de relations OSM
    """
    page = requests.get('https://wiki.openstreetmap.org/wiki/WikiProject_France/Bus_RATP')
    liste_relations = re.findall(r'href="//www.openstreetmap.org/relation/(\w+)"', page.text)
    liste_relations = list(set(liste_relations))
    return liste_relations

def collect_relations_from_overpass():
    """
    appelle l'API overpass et extrait tous les id de relations qui vont bien
    """
    pass #TODO

def persist_list_to_csv(liste, nom_fichier):
    """
    enregistre une liste au format csv
    """
    mon_fichier = open(nom_fichier, "wb")
    for elem in liste :
        mon_fichier.write(str(elem) + '\n')
    mon_fichier.close()
    
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

    mon_fichier = open(fichier_a_analyser, "rb")
    for elem in mon_fichier :
        print int(elem)
        relation_param = '[out:json][timeout:25];relation('+ elem+');out;'
        resp = requests.get(overpass_base_url, params={'data': relation_param})
        if resp.status_code != 200:
            print "KO"
            continue
            relations_hors_sujet.append(int(elem))
        mon_json = resp.json()
        if 'elements' in mon_json:
            if len(mon_json['elements']) > 0 :
                ma_relation = mon_json['elements'][0]['tags']
            else :
                print "KO"
                continue
                relations_hors_sujet.append(int(elem))
        if 'type' in ma_relation:
            if ma_relation['type'] == "route_master":
                relations_lignes.append(int(elem)) 
            elif ma_relation['type'] == "route":
                ma_route = {}
                if not 'from' in ma_relation:
                    routes_sans_from.append(int(elem))
                if not 'to' in ma_relation:
                    routes_sans_to.append(int(elem))
                if not 'operator' in ma_relation:
                    routes_sans_operator.append(int(elem)) 
                if not 'network' in ma_relation:
                    routes_sans_network.append(int(elem)) 
                if not 'colour' in ma_relation:
                    routes_sans_colour.append(int(elem))  
                if not 'name' in ma_relation:
                    routes_sans_name.append(int(elem)) 
                else :
                    ma_route['name'] = ma_relation['name'].encode('utf-8')
                if not 'ref' in ma_relation:
                    routes_sans_ref.append(int(elem)) 
                else :
                    ma_route['code'] = ma_relation['ref']
                ma_route['osm_id'] = int(elem)
                relations_routes.append(ma_route)
                print ma_route
            else :
                relations_hors_sujet.append(int(elem))
        else :
            relations_hors_sujet.append(int(elem))   
         
    persist_list_to_csv(routes_sans_from, "collecte/analyse/routes_sans_from.csv")
    persist_list_to_csv(routes_sans_to, "collecte/analyse/routes_sans_to.csv")
    persist_list_to_csv(routes_sans_network, "collecte/analyse/routes_sans_network.csv")
    persist_list_to_csv(routes_sans_operator, "collecte/analyse/routes_sans_operator.csv")
    persist_list_to_csv(routes_sans_colour, "collecte/analyse/routes_sans_colour.csv")
    persist_list_to_csv(routes_sans_name, "collecte/analyse/routes_sans_name.csv")
    persist_list_to_csv(routes_sans_ref, "collecte/analyse/routes_sans_ref.csv")
    persist_list_to_csv(relations_hors_sujet, "analyse/relations_hors_sujet.csv")
 
    relations_routes_csv = []
    for a in relations_routes:
        relations_routes_csv.append([a['code'] + u"," + a['name'].decode('utf-8') + u',' + str(a['osm_id'])] )
    mon_fichier = open("collecte/relations_routes.csv", "wb")
    for elem in relations_routes_csv :
        mon_fichier.write(elem[0].encode('utf-8') + '\n')
    mon_fichier.close()

if __name__ == '__main__':
    persist_list_to_csv(collect_relations_from_wiki(), "collecte/liste_relations.csv")
    analyse_relation_list("collecte/liste_relations.csv")   
 
