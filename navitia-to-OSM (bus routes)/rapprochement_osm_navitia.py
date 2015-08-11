#-------------------------------------------------------------------------------
#
# Author:      nlehuby
#
# Created:     28/01/2015
# Copyright:   (c) nlehuby 2015
# Licence:     MIT
#-------------------------------------------------------------------------------
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import csv
from fuzzywuzzy import fuzz
from params import navitia_API_key as TOKEN

#paramétrage
navitia_API_key = TOKEN
navitia_base_url = "http://api.navitia.io/v1/coverage/fr-idf"

def pt_objects_by_code(route_code):
    """
    appelle navitia avec un code de route donné, et récupère la liste des routes qui correspondent (nom et extcode)
    """
    appel_nav = requests.get(navitia_base_url + "/pt_objects?type[]=route&q=" + route_code, headers={'Authorization': navitia_API_key})
    mon_json = appel_nav.json()
    if not 'pt_objects' in mon_json:
        result_nav = []
    else :
        result_nav=mon_json['pt_objects']

    liste_name = []
    liste_extcode = []

    for une_route in result_nav:
        liste_extcode.append(une_route['route']['id'])
        liste_name.append(une_route['route']['name'].encode('utf-8'))

    return  [liste_name, liste_extcode] #tableau des nom, tableau des codes

def rapprochement_osm_navitia():
    """
    parcourt le fichier des relations osm et appelle navitia pour chaque, choisit une route pertinente, et loggue un tas de trucs
    """
    ifile  = open('collecte/relations_routes.csv', "rb")
    reader = csv.reader(ifile)

    routes_sans_ref = []
    routes_inconnues_navitia = []
    rapprochements = []

    for row in reader:
        route_code = row[1]
        route_name = row[2]
        route_osm_id = row[0]
        if route_code:
            print route_name
            resultat_navitia = pt_objects_by_code(route_code)
            print resultat_navitia
            if len(resultat_navitia[0]) != 0:
                noms_potentiels = resultat_navitia[0]
                ratio_noms_potentiels = [fuzz.partial_ratio(route_name, nom) for nom in noms_potentiels]
                print ratio_noms_potentiels
                index_max = ratio_noms_potentiels.index(max(ratio_noms_potentiels)) #index du ratio le plus élevé
                #print index_max
                print resultat_navitia[0][index_max]
                navitia_nb_stops = get_navitia_nb_stop(resultat_navitia[1][index_max])
                rapprochements.append([route_osm_id, resultat_navitia[1][index_max], route_name, navitia_nb_stops]) 
            else :
                routes_inconnues_navitia.append(row)           
        else :
            routes_sans_ref.append(row)

    ifile.close()

#    print rapprochements
#    print routes_sans_ref
#    print routes_inconnues_navitia #TODO : persister pour analyse

    #persist to csv
    myfile = open('rapprochement/relations_sans_ref.csv', 'wb')
    wr = csv.writer(myfile)
    for row in routes_sans_ref:
        wr.writerow(row)

    myfile = open('rapprochement/osm_navitia.csv', 'wb')
    wr = csv.writer(myfile)
    for row in rapprochements:
        wr.writerow(row)  #TODO : attention, c'est le nom osm qui est persisté et non le nom navitia


def get_navitia_nb_stop(extcode):
    """
    appelle navitia et récupère le nombre d'arrêts d'une route donnée.
    """
    appel_nav = requests.get(navitia_base_url + "/routes/" + extcode + "/stop_points", headers={'Authorization': navitia_API_key})
    if appel_nav.status_code != 200:
        print "KO navitia :" + extcode
        return None
    nb_result = appel_nav.json()['pagination']['total_result']
    return nb_result
    
def analyse_du_rapprochement():
    """
    pourcentage d'éléments uniques (ceux en doubles sont ceux où le rapprochement est très probablement faux)
    """
    ifile  = open('rapprochement/osm_navitia.csv', "rb")
    reader = csv.reader(ifile)
    extcodes = [row[1] for row in reader]
    #print len(extcodes) - len(list(set(extcodes))) #nombres d'éléments où on est surs que c'est pas bon
    return len(list(set(extcodes)))/float(len(extcodes)) * 100
    


if __name__ == '__main__':
    #print pt_objects_by_code("20")
    #print pt_objects_by_code("185")
    #print pt_objects_by_code("354")
    
    rapprochement_osm_navitia()
    print analyse_du_rapprochement()
