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
import difflib
from fuzzywuzzy import fuzz
from params import navitia_API_key as TOKEN

#paramétrage
navitia_API_key = TOKEN
navitia_base_url = "http://api.navitia.io/v1/coverage/fr-idf"

def get_navitia_info_by_line_code(line_code):
    """
    appelle navitia avec un code de route donné, et récupère la liste des parcours qui correspondent 
    retourne [{'id':'', 'name':'', 'destination':''}, {'id':'', 'name':"", 'destination':''}]
    """
    appel_nav = requests.get(navitia_base_url + "/pt_objects?type[]=route&q=" + line_code, headers={'Authorization': navitia_API_key})
    mon_json = appel_nav.json()
    if not 'pt_objects' in mon_json:
        print 'KO navitia'
        return []
    else :
        result_nav=mon_json['pt_objects']

    navitia_info = []
    for un_parcours in result_nav:
        route_info = {'id' : '','name':'', 'destination':''}
        route_info['id'] = un_parcours['route']['id']
        route_info['name'] = un_parcours['route']['name']
        route_info['destination'] = un_parcours['route']['direction']['name']
        navitia_info.append(route_info)
    
    return navitia_info

def pt_objects_by_code(route_code):
    """
    Déprécié
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
    parcourt le fichier des relations osm et appelle navitia pour chaque, choisit un parcours pertinent
    """
    ifile  = open('collecte/relations_routes.csv', "rb")
    reader = csv.reader(ifile)

    pas_de_match_navitia = []
    trop_de_solutions_navitia = []
    rapprochements_ok = []
    
    for an_osm_route in reader:
        line_code = an_osm_route[1]
        route_name = an_osm_route[2]
        route_osm_id = an_osm_route[0] 
        print route_name
        if line_code:
            navitia_potential_matches = get_navitia_info_by_line_code(line_code)
            navitia_matches = list(navitia_potential_matches) #si ça matche pas, on retirera le candidat de cette liste
            for a_nav_route in navitia_potential_matches :
                is_there_a_match = difflib.get_close_matches(route_name.lower().decode('utf-8'), [a_nav_route['name'].lower().decode('utf-8')]) #match sur le nom
                #match sur le nom ou sur la destination ou les deux ou l'un si pas l'autre?
                if len(is_there_a_match) == 0:
                    navitia_matches.remove(a_nav_route)          
                
            print navitia_matches   
            if len(navitia_matches) == 1:#cas générique
                navitia_nb_stops = get_navitia_nb_stop(navitia_matches[0]['id'])
                rapprochements_ok.append([route_osm_id, navitia_matches[0]['id'], navitia_matches[0]['name'].encode('utf-8'), navitia_nb_stops, navitia_matches[0]['destination'].encode('utf-8')]) 
            elif len(navitia_matches) == 0: #cas où rien ne matche
                pas_de_match_navitia.append([route_osm_id])
            else : #cas où il y a plusieurs solutions
                trop_de_solutions_navitia.append([route_osm_id] + navitia_matches)
        else :        
            pas_de_match_navitia.append([route_osm_id])

    ifile.close()

    myfile = open('rapprochement/osm_navitia.csv', 'wb')
    wr = csv.writer(myfile)
    for row in rapprochements_ok:
        wr.writerow(row)                   
    
def rapprochement_osm_navitia_with_fuzzywuzzy():
    """
    -- Déprécié --
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
                rapprochements.append([route_osm_id, resultat_navitia[1][index_max], resultat_navitia[0][index_max], navitia_nb_stops]) 
            else :
                routes_inconnues_navitia.append(row)           
        else :
            routes_sans_ref.append(row)

    ifile.close()

#    print rapprochements
#    print routes_sans_ref
#    print routes_inconnues_navitia 

    #persist to csv
    myfile = open('rapprochement/relations_sans_ref.csv', 'wb')
    wr = csv.writer(myfile)
    for row in routes_sans_ref:
        wr.writerow(row)

    myfile = open('rapprochement/osm_navitia.csv', 'wb')
    wr = csv.writer(myfile)
    for row in rapprochements:
        wr.writerow(row)  


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
    return len(list(set(extcodes)))/float(len(extcodes)) * 100
    


if __name__ == '__main__':    
    #print get_navitia_info_by_line_code("467")
    
    #rapprochement_osm_navitia_with_fuzzywuzzy() > 385 / 396 matches, mais 88% de cas a priori ok
    #rapprochement_osm_navitia() sur le name > 275 / 396 mais 100 % a priori ok
    rapprochement_osm_navitia() #sur la direction > TODO/396 mais TODO a priori ok
    print analyse_du_rapprochement()
