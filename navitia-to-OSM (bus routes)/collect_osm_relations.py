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

def collect_relations_from_wiki(wiki_url):
    """
    consulte la page de wiki sur les bus RATP et extrait tous les liens de relations OSM
    """
    #page = requests.get('https://wiki.openstreetmap.org/wiki/WikiProject_France/Bus_RATP')
    page = requests.get(wiki_url)
    liste_relations = re.findall(r'href="//www.openstreetmap.org/relation/(\w+)"', page.text)
    liste_relations = list(set(liste_relations))
    return liste_relations

def collect_relations_from_overpass(overpass_query):
    """
    appelle l'API overpass et extrait tous les id de relations qui vont bien
    """
    #[out:json][timeout:25];(relation["network"="Noctilien"]["route"="bus"(48.68098749511622,2.1258544921875,48.9220480811836,2.6126861572265625););out ids;
    resp = requests.get(overpass_base_url, params={'data': overpass_query})
    if resp.status_code != 200:
        print "échec de l'appel overpass de collecte des relations"
        return []
    return [str(a_relation['id']) for a_relation in resp.json()['elements'] ]
    
        


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
            if ma_relation['type'] == "route":
                ma_route = {}
                if not 'from' in ma_relation:
                    routes_sans_from.append(int(elem))
                if not 'to' in ma_relation:
                    routes_sans_to.append(int(elem))
                    ma_route['destination'] = ''
                else :
                    ma_route['destination'] = ma_relation['to'].encode('utf-8')                    
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
                stop_count = 0
                for a_member in mon_json['elements'][0]['members']:
                    if a_member['type'] == 'node':
                        stop_count += 1
                ma_route['stop_count'] = stop_count
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
    persist_list_to_csv(relations_hors_sujet, "collecte/analyse/relations_hors_sujet.csv")
 
    relations_routes_csv = []
    for a in relations_routes:
        relations_routes_csv.append([str(a['osm_id']) + u',' + a['code'] + u"," + a['name'].decode('utf-8') + u"," + a['destination'].decode('utf-8') + u"," + str(a['stop_count']) ])
    mon_fichier = open("collecte/relations_routes.csv", "wb")
    for elem in relations_routes_csv :
        mon_fichier.write(elem[0].encode('utf-8') + '\n')
    mon_fichier.close()

if __name__ == '__main__': 
     #noctiliens_ov = collect_relations_from_overpass('[out:json][timeout:25];(relation["network"="Noctilien"]["route"="bus"](48.68098749511622,2.1258544921875,48.9220480811836,2.6126861572265625););out ids;' )


    noctiliens = collect_relations_from_wiki('https://wiki.openstreetmap.org/wiki/WikiProject_France/Noctilien')
    autres_bus = collect_relations_from_wiki('https://wiki.openstreetmap.org/wiki/WikiProject_France/Bus_RATP')
    #autres_bus = [] #collect_relations_from_wiki('https://wiki.openstreetmap.org/wiki/WikiProject_France/Bus_RATP')
    persist_list_to_csv(list(set(noctiliens + autres_bus)), "collecte/liste_relations.csv")
    analyse_relation_list("collecte/liste_relations.csv") 
