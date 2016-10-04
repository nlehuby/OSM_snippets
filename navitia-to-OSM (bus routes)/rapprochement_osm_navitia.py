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
        route_info['destination'] = un_parcours['route']['direction']['stop_area']['name']
        navitia_info.append(route_info)

    return navitia_info

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
        route_destination = an_osm_route[3]
        route_osm_id = an_osm_route[0]
        print route_name
        if line_code:
            navitia_potential_matches = get_navitia_info_by_line_code(line_code)
            navitia_matches = list(navitia_potential_matches) #si ça matche pas, on retirera le candidat de cette liste
            for a_nav_route in navitia_potential_matches :
                #is_there_a_match = difflib.get_close_matches(route_destination.lower(), [a_nav_route['destination'].lower()]) #match sur la direction
                #is_there_a_match = difflib.get_close_matches(route_name.lower().decode('utf-8'), [a_nav_route['name'].lower().decode('utf-8')]) #match sur le nom
                is_there_a_match = difflib.get_close_matches(route_name.lower(), [a_nav_route['name'].lower()])
                if len(is_there_a_match) == 0:
                    navitia_matches.remove(a_nav_route)

            print navitia_matches
            if len(navitia_matches) == 1:#cas générique
                navitia_nb_stops = get_navitia_nb_stop(navitia_matches[0]['id'])
                rapprochements_ok.append([route_osm_id, navitia_matches[0]['id'], navitia_matches[0]['name'].encode('utf-8'), navitia_nb_stops, navitia_matches[0]['destination'].encode('utf-8')])
            elif len(navitia_matches) == 0: #cas où rien ne matche
                pas_de_match_navitia.append([route_osm_id, route_name])
            else : #cas où il y a plusieurs solutions
                print route_osm_id
                trop_de_solutions_navitia.append([route_osm_id] + [elem['id'] + u' ; ' + elem['destination'] for elem in navitia_matches])
        else :
            pas_de_match_navitia.append([route_osm_id, route_name])

    ifile.close()

    myfile = open('rapprochement/osm_navitia.csv', 'wb')
    wr = csv.writer(myfile)
    for row in rapprochements_ok:
        wr.writerow(row)

    myfile = open('rapprochement/pas_assez.csv', 'wb')
    wr = csv.writer(myfile)
    for row in pas_de_match_navitia:
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
    rapprochement_osm_navitia() #sur la direction > 193/396 mais 99.5 % a priori ok
    print analyse_du_rapprochement()
