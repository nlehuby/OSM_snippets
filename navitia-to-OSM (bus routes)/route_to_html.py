#-------------------------------------------------------------------------------
# Author:      nlehuby
#
# Created:     28/01/2015
# Copyright:   (c) nlehuby 2015
# Licence:     MIT
#-------------------------------------------------------------------------------
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import geojson
import requests
import datetime
import csv
from params import navitia_API_key as TOKEN

#paramétrage
navitia_API_key = TOKEN
navitia_base_url = "http://api.navitia.io/v1/coverage/fr-idf/networks/network:RTP/"
overpass_base_url = "http://www.overpass-api.de/api/interpreter"

def extract_name_from_OSM(osm_id):
    """
    appelle Overpass et récupère le nom d'une relation donnée.
    """
    relation_param = '[out:json][timeout:25];relation('+ osm_id+');out;'
    resp = requests.get(overpass_base_url, params={'data': relation_param})
    try:
        return resp.json()['elements'][0]['tags']['name']
    except :
        print "OSM - impossible de récupérer le nom de la relation " + osm_id


def extract_name_from_navitia(route_extcode):
    """
    appelle navitia et récupère le nom d'une route donnée.
    """
    my_route= route_extcode
    appel_nav = requests.get(navitia_base_url + "/routes/" + my_route, headers={'Authorization': navitia_API_key})
    try:
        result_nav=appel_nav.json()['routes'][0]
        return  {"code" : result_nav["line"]['code'], 'name' : result_nav["name"]}
    except :
        print "navitia - impossible de récupérer le nom de la route " + route_extcode


def extract_nb_stop_from_navitia(route_extcode):
    """
    appelle navitia et récupère le nombre d'arrêts d'une route donnée.
    """
    my_route= route_extcode
    appel_nav = requests.get(navitia_base_url + "/routes/" + my_route + "/stop_points", headers={'Authorization': navitia_API_key})
    nb_result = appel_nav.json()['pagination']['total_result']
    return nb_result

def extract_nb_stop_from_OSM(osm_id):
    """
    appelle Overpass et récupère le nombre de membres noeuds d'une relation donnée.
    TODO : attention, cela compte les stop_position et pas uniquement les highway=bus_stop
    """
    relation_param = '[out:json][timeout:25];relation('+ osm_id+');node(r);out count;'
    resp = requests.get(overpass_base_url, params={'data': relation_param})
    if resp.status_code != 200:
        print "KO"
        return 0
    return resp.json()['elements'][0]['count']["nodes"]

def extract_geojson_from_navitia(route_extcode):
    """
    appelle navitia et construit un geojson de tous les arrêts d'une route donnée.
    """
    my_route= route_extcode

    nb_result = extract_nb_stop_from_navitia(my_route)

    #print  str(nb_result) + " arrêts sur cette route."

    appel_nav = requests.get(navitia_base_url + "/routes/" + my_route + "/stop_points?count=" + str(nb_result), headers={'Authorization': navitia_API_key})
    result_nav=appel_nav.json()

    names = []
    lats = []
    lons = []
    stop_id = []

    for stop in result_nav['stop_points'] :
        names.append( stop['name'] )
        lats.append( float(stop['coord']['lat']) )
        lons.append( float(stop['coord']['lon']) )
        stop_id.append( stop['id'] )

    #transformation en geojson
    my_collection = []

    for a_stop in range(len(names)) :
        my_temp_point = geojson.Point((lons[a_stop], lats[a_stop]))
        my_temp_Feature = geojson.Feature(geometry = my_temp_point, properties = {"name": names[a_stop], "code" : stop_id[a_stop]}, id= a_stop + 1 )
        my_collection.append(my_temp_Feature)

    dump = geojson.dumps(geojson.FeatureCollection(my_collection), sort_keys=True)
    return dump


def save_geojson_to_file(data) :
    """
    fonction de débug : persiste un fichier geojson afin de le lire avec un autre outil.
    utilisation : save_geojson_to_file(extract_geojson_from_navitia('route:RTP:1228007'))
    """
    file = open('route.geosjon', "w")
    file.write(data)
    file.close()


def send_to_html(navitia_route, OSM_relation, persist=True):
    """
    crée une page html listant les arrêts navitia et OSM d'une route
    Si persist = True, enregistre le nom de la route et les nombres d'arrêts pour générer une page indexant toutes les pages des routes
    """
    my_relation_info = extract_name_from_OSM(OSM_relation)
    my_route_info = extract_name_from_navitia(navitia_route)
    if not my_relation_info :
        print "#### échec OSM : route ignorée "
        return
    if not my_route_info :
        print "#### échec navitia : route ignorée"
        return
    navitia_nb_stops = str(extract_nb_stop_from_navitia(navitia_route))
    OSM_nb_stops = str(extract_nb_stop_from_OSM(OSM_relation))
    now = datetime.datetime.now()

    ## result to HTML
    mon_fichier = open("rendu/assets/template.html", "r")
    template = mon_fichier.read()
    mon_fichier.close()

    template = template.replace("%%navitia_route_extcode%%", navitia_route  )
    template = template.replace("%%navitia_route_name%%", my_route_info['code'].encode('utf-8') + ' : ' + my_route_info['name'].encode('utf-8'))
    template = template.replace("%%navitia_route_geojson%%", extract_geojson_from_navitia(navitia_route))
    template = template.replace("%%OSM_relation_code%%", OSM_relation  )
    template = template.replace("%%OSM_relation_name%%", my_relation_info.encode('utf-8') )
    template = template.replace("%%OSM_nb_stops%%", OSM_nb_stops  )
    template = template.replace("%%navitia_nb_stops%%", navitia_nb_stops  )
    template = template.replace("%%date_du_jour%%", now.strftime("%d/%m/%Y %H:%M")  )

    mon_fichier = open("rendu/" + OSM_relation + ".html", "wb")
    mon_fichier.write(template)
    mon_fichier.close()

    if persist :
        index = [OSM_relation, my_relation_info.encode('utf-8'), OSM_nb_stops, navitia_nb_stops, my_route_info['code'].encode('utf-8') ]
        print index
        mon_csv = csv.writer(open("rendu/liste_routes.csv", "ab"))
        mon_csv.writerow(index)


def comp(v1, v2):
    """tri d'une liste selon son 5ième élément"""
    #TODO : ce tri n'est pas satisfaisant ...
    if v1[4]<v2[4]:
        return -1
    elif v1[4]>v2[4]:
        return 1
    else:
        return 0

def create_html_index_page():
    """
    crée la page d'index listant toutes les pages html des routes déjà créées et persistées'
    """
    template_table = ''

    #récupération des infos à partir du csv
    mycsv_reader = csv.reader(open("rendu/liste_routes.csv", "rb"))

    # retri du csv par code
    liste = list(mycsv_reader)
    liste.sort(cmp=comp)

    #création d'une ligne dans l'index pour chaque ligne du csv
    for route_info in liste:
        liste_template = """
            <tr>
                <td> %%route_code%%
                </td>
                <td>
                <a href="%%relation_id%%.html">%%relation_name%%</a>
                </td>
                <td>
                    %%OSM_nb_stops%%/%%navitia_nb_stops%%
                </td>
                <td>

                    <progress value="%%OSM_nb_stops%%" max="%%navitia_nb_stops%%">état de la carto de la route</progress>
                </td>
            <tr>
        """
        liste_template = liste_template.replace("%%route_code%%", route_info[4]  )
        liste_template = liste_template.replace("%%relation_id%%", route_info[0]  )
        liste_template = liste_template.replace("%%relation_name%%", route_info[1]  )
        liste_template = liste_template.replace("%%OSM_nb_stops%%", route_info[2]  )
        liste_template = liste_template.replace("%%navitia_nb_stops%%", route_info[3]  )
        template_table += liste_template

    #ajout dans le template
    now = datetime.datetime.now()
    mon_fichier = open("rendu/assets/template_liste.html", "r")
    template = mon_fichier.read()
    mon_fichier.close()
    template = template.replace("%%tableau_des_routes%%", template_table  )
    template = template.replace("%%date_du_jour%%", now.strftime("%d/%m/%Y %H:%M") )
    mon_fichier = open("rendu/index.html", "wb")
    mon_fichier.write(template)
    mon_fichier.close()


def render_all():
    """
    crée la page html de chaque route, puis la page html listant toutes les routes et leur état de complétion
    """
    # /!\ ne pas oublier de vider le fichier temp de création de l'index : liste_routes.csv
    mycsv_reader = csv.reader(open("rapprochement/osm_navitia.csv", "rb"))
    for une_route in mycsv_reader:
        send_to_html(une_route[1], une_route[0])

    #créer l'index
    create_html_index_page()


if __name__ == '__main__':
    render_all()

    #exemples
    #send_to_html('route:RTP:1250013','1257174') #bus 57, retour
    #send_to_html('route:RTP:1228417_R','1254000') #bus 68, aller
    #send_to_html('route:RTP:1227971_R','1250938') #bus 87, aller
    #send_to_html('route:RTP:1025341_R','306279') #bus 185, retour
    #send_to_html('route:RTP:1025341','3008944') #bus 185, aller

    #create_html_index_page()
