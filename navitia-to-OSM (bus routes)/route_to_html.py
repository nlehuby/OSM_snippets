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
import json
import requests
import datetime
import csv
from params import navitia_API_key as TOKEN

#paramétrage
navitia_API_key = TOKEN
navitia_base_url = "http://api.navitia.io/v1/coverage/fr-idf"
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
        return result_nav["name"]#.decode('utf-8')
    except :
        print "navitia - impossible de récupérer le nom de la route " + route_extcode


def extract_nb_stop_from_navitia(route_extcode):
    """
    appelle navitia et récupère le nombre d'arrêts d'une route donnée.
    """
    my_route= route_extcode
    appel_nav = requests.get(navitia_base_url + "/routes/" + my_route + "/stop_points", headers={'Authorization': navitia_API_key})
    if appel_nav.status_code != 200:
        print "KO navitia " + my_route
        return None
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
        print "KO OSM"
        return None
    return resp.json()['elements'][0]['count']["nodes"]

def extract_geojson_from_navitia(route_extcode, nb_stops = None):
    """
    appelle navitia et construit un geojson de tous les arrêts d'une route donnée.
    """
    if nb_stops is None :
        print "nb de stops navitia à recalculer"
        nb_stops  = extract_nb_stop_from_navitia(route_extcode)

    if nb_stops is None :
        print "KO navitia " + route_extcode
        return  "{}"

    appel_nav = requests.get(navitia_base_url + "/routes/" + route_extcode + "/stop_points?count=" + str(nb_stops), headers={'Authorization': navitia_API_key})
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


def send_to_html(osm_info, navitia_info):
    """
    crée une page html listant les arrêts navitia et OSM d'un parcours
    osm_info & navitia_info ~ {id : '', name : '', nb_stops : '', ref: '', junk : junk }
    seuls les codes sont obligatoires
    """
    #OSM
    OSM_id = osm_info['id']
    if 'name' in osm_info :
        OSM_name = osm_info['name'].decode('utf-8')
    else :
        OSM_name = extract_name_from_OSM(OSM_id)
        osm_info['name'] = OSM_name
    if not OSM_name :
        print "#### échec OSM : parcours ignoré "
        return
    if 'nb_stops' in osm_info :
        OSM_nb_stops = osm_info['nb_stops']
    else :
        OSM_nb_stops = extract_nb_stop_from_OSM(OSM_id)
        osm_info['nb_stops'] = OSM_nb_stops
    if not OSM_nb_stops :
        print "#### échec OSM : parcours ignoré "
        return
    if 'ref' in osm_info :
        OSM_ref = osm_info['ref']
    else :
        pass #TODO : récupérer le code la ligne
    if not OSM_ref :
        print "#### pas de code de ligne"
        OSM_ref = 'No code'
    #navitia
    navitia_id = navitia_info['id']
    if 'name' in navitia_info and navitia_info['name'] != "" :
        navitia_name = navitia_info['name'].decode('utf-8')
    else :
        navitia_name = extract_name_from_navitia(navitia_id)
        navitia_info['name'] = navitia_name
    if not navitia_info['name'] :
        print "#### échec navitia (nom): parcours ignoré "
        #return
    if 'nb_stops' in navitia_info and navitia_info['nb_stops'] != "":
        navitia_nb_stops = navitia_info['nb_stops']
    else :
        navitia_nb_stops = str(extract_nb_stop_from_navitia(navitia_id))
        navitia_info['nb_stops'] = navitia_nb_stops
    if not navitia_nb_stops :
        print "#### échec navitia (nb stops): parcours ignoré "
        return

    generate_navitia_json_file(osm_info, navitia_info)

    ## result to HTML
    now = datetime.datetime.now()
    mon_fichier = open("rendu/assets/template.html", "r")
    template = mon_fichier.read()
    mon_fichier.close()

    template = template.replace("%%navitia_route_geojson%%", extract_geojson_from_navitia(navitia_id, navitia_nb_stops))
    template = template.replace("%%OSM_relation_code%%", OSM_id  )

    mon_fichier = open("rendu/" + OSM_id + ".html", "wb")
    mon_fichier.write(template)
    mon_fichier.close()


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
    crée la page d'index listant toutes les pages html listant tous les parcours osm rapprochés
    """
    template_table = ''
    liste = []


    osm_csv = csv.reader(open("collecte/relations_routes.csv", "rb"))
    navitia_json = json.load(open("rendu/navitia.json", "rb"))

    for osm_route in osm_csv :
        liste_template = """
            <tr>
                <td> %%route_code%%
                </td>
                <td>
                <a href="bus_route.htm?osm=%%relation_id%%&navitia=%%navitia_id%%">%%relation_name%%</a>
                </td>
                <td>
                    %%OSM_nb_stops%%/%%navitia_nb_stops%%
                </td>
                <td>

                    <progress value="%%OSM_nb_stops%%" max="%%navitia_nb_stops%%">état de la carto de la route</progress>
                </td>

            <tr>
        """

        liste_template = liste_template.replace("%%route_code%%", osm_route[1]  )
        liste_template = liste_template.replace("%%relation_id%%", osm_route[0]  )
        liste_template = liste_template.replace("%%relation_name%%", osm_route[2]  )
        liste_template = liste_template.replace("%%OSM_nb_stops%%", osm_route[4]  )
        if osm_route[0] in navitia_json :
            liste_template = liste_template.replace("%%navitia_nb_stops%%", str(navitia_json[osm_route[0]]['navitia_nb_arrets'])  )
            liste_template = liste_template.replace("%%navitia_id%%", str(navitia_json[osm_route[0]]['navitia_id'])  )
        else :
            liste_template = liste_template.replace("%%navitia_nb_stops%%", '0'  )
            liste_template = liste_template.replace("%%navitia_id%%", ''  )
        template_table += liste_template
        liste.append([osm_route[0], osm_route[2]] )

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

    #création du fichier csv utilisé pour l'autocomplétion
    myfile = open('rendu/liste_routes.csv', 'wb')
    wr = csv.writer(myfile)
    for row in liste:
        wr.writerow(row)

def generate_navitia_json_file(osm_info, navitia_info):
    file_name = 'rendu/navitia.json'
    try:
        my_json = json.load(open(file_name))
    except IOError:
        print "on crée le fichier"
        my_json = {"junk":"junk"}
        json.dump(my_json, open(file_name, "w"), indent=4)
    my_json = json.load(open(file_name))
    my_json[osm_info["id"]] = {}
    my_json[osm_info["id"]]['navitia_nb_arrets'] = navitia_info['nb_stops']
    my_json[osm_info["id"]]['navitia_id'] = navitia_info['id']
    my_json[osm_info["id"]]['navitia_name'] = navitia_info['name']
    my_json[osm_info["id"]]['osm_nb_arrets'] = osm_info['nb_stops']
    now = datetime.datetime.now()
    my_json[osm_info["id"]]['date_gen'] = now.strftime("%d/%m/%Y %H:%M")

    json.dump(my_json, open(file_name, "w"), indent=4)

def render_all():
    """
    crée la page html de chaque route, puis la page html listant toutes les routes et leur état de complétion
    """

    osm_csv = csv.reader(open("collecte/relations_routes.csv", "rb"))
    navitia_csv = list(csv.reader(open("rapprochement/osm_navitia.csv", "rb")))
    #persist_for_index = []
    for osm_route in osm_csv:
        print osm_route[2]
        rapp = [route for route in navitia_csv if route[0] == osm_route[0]] #rapprochement osm navitia
        if rapp != []:
            current_osm_route = {'id' : osm_route[0], 'name': osm_route[2], 'ref': osm_route[1], 'nb_stops': osm_route[4]}
            current_nav_route = {'id' : rapp[0][1], 'name' : rapp[0][2], 'nb_stops': rapp[0][3]}
            send_to_html(current_osm_route, current_nav_route)
            #persist_for_index.append([osm_route[0],osm_route[2], osm_route[-1], rapp[0][3], osm_route[1]])
             #osm_relation_id, osm_relation_name, osm_nb_stops, navitia_nb_stops, osm_ref

        else:
            print "pas de correspondance osm navitia trouvée"
            #TODO : créer la page osm sans navitia


    #créer l'index
    create_html_index_page()

def prepare_osm_routes():
    """
    reconstruit les infos osm nécessaires
    """
    source_csv = csv.reader(open("collecte/relations_routes.csv", "rb"))
    result_list = []

    for an_osm_route in source_csv :
        if len(an_osm_route) < 6:
            print ("il faut appeler Overpass pour récupérer les infos manquantes : TODO")
        else :
            result_list.append(an_osm_route)

    #tri
    result_int = []
    result_other= []
    for a_route in result_list:
        try:
            int(a_route[1])
            result_int.append(a_route)
        except ValueError :
            result_other.append(a_route)
    result_int.sort(key=lambda osm_route: osm_route[1])
    result_other.sort(key=lambda osm_route: osm_route[1])
    result_list = result_int + result_other


    with open("rendu/sources/osm_parcours.csv", "wb") as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for line in sorted(result_list, key=lambda osm_route: osm_route[1]):
            writer.writerow(line)

def prepare_navitia_routes():
    """
    reconstruit les infos navitia nécessaires
    """
    source_csv = csv.reader(open("rapprochement/osm_navitia.csv", "rb"))
    result_list = []

    for a_nav_route in source_csv :
        if len(a_nav_route) < 5:
            print ("il faut appeler navitia pour récupérer les infos manquantes : TODO")
        else :
            result_list.append(a_nav_route)

    with open("rendu/sources/navitia_parcours.csv", "wb") as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for line in result_list:
            writer.writerow(line)


def to_html():
    """
    crée la page d'index listant référençant les pages de chaque parcours OSM
    """

    #TODO : récréer les fichiers csv à partir des fonctions déjà existantes en complétant les infos manquantes
    prepare_osm_routes()
    prepare_navitia_routes()

    osm_csv = csv.reader(open("rendu/sources/osm_parcours.csv", "rb"))
    navitia_csv = list(csv.reader(open("rendu/sources/navitia_parcours.csv", "rb")))

    autocomplete = {"parcours_osm":[]}

    template_table = ''

    for osm_route in osm_csv:
        print osm_route[2]
        #création de l'objet pour l'autocomplétion
        parcours = {}
        parcours['value'] = osm_route [0]
        parcours['label'] = "[{}] {} > {}".format(osm_route[-1], osm_route[1], osm_route[3])

        rapp = [route for route in navitia_csv if route[0] == osm_route[0]] #rapprochement osm navitia

        print (rapp)
        if rapp != []:
            print ('ok')
            parcours['url'] = "bus_route.htm?osm={}&navitia={}".format(osm_route[0], rapp[0][1] )

            #current_osm_route = {'id' : osm_route[0], 'name': osm_route[2], 'ref': osm_route[1], 'nb_stops': osm_route[4]}
            #current_nav_route = {'id' : rapp[0][1], 'name' : rapp[0][2], 'nb_stops': rapp[0][3]}

            #ajout dans l'index
            liste_template = """
                <tr>
                    <td> %%network%%
                    </td>
                    <td> %%route_code%%
                    </td>
                    <td>
                    <a href="bus_route.htm?osm=%%relation_id%%&navitia=%%navitia_id%%">%%relation_name%%</a>
                    </td>
                    <td>
                        %%OSM_nb_stops%%/%%navitia_nb_stops%%
                    </td>
                    <td>

                        <progress value="%%OSM_nb_stops%%" max="%%navitia_nb_stops%%">état de la carto de la route</progress>
                    </td>

                <tr>
                """

            liste_template = liste_template.replace("%%route_code%%", osm_route[1]  )
            liste_template = liste_template.replace("%%relation_id%%", osm_route[0]  )
            liste_template = liste_template.replace("%%relation_name%%", osm_route[2]  )
            liste_template = liste_template.replace("%%network%%", osm_route[5]  )
            liste_template = liste_template.replace("%%OSM_nb_stops%%", osm_route[4]  )
            liste_template = liste_template.replace("%%navitia_nb_stops%%", rapp[0][3] )
            liste_template = liste_template.replace("%%navitia_id%%", rapp[0][1] )


        else:
            print ('ko')
            parcours['url'] = "bus_route.htm?osm={}".format(osm_route[0])
            liste_template = """
                <tr>
                    <td> %%network%%
                    </td>
                    <td> %%route_code%%
                    </td>
                    <td>
                    <a href="bus_route.htm?osm=%%relation_id%%">%%relation_name%%</a>
                    </td>
                    <td colspan=2>
                        %%OSM_nb_stops%%
                    </td>
                <tr>
                """
            liste_template = liste_template.replace("%%route_code%%", osm_route[1]  )
            liste_template = liste_template.replace("%%relation_id%%", osm_route[0]  )
            liste_template = liste_template.replace("%%relation_name%%", osm_route[2]  )
            liste_template = liste_template.replace("%%network%%", osm_route[5]  )
            liste_template = liste_template.replace("%%OSM_nb_stops%%", osm_route[4]  )



        #persistance autocomplétion
        autocomplete['parcours_osm'].append(parcours)
        template_table += liste_template

    #persistance de la page d'index
    now = datetime.datetime.now()
    mon_fichier = open("rendu/assets/template_liste.html", "r")
    template = mon_fichier.read()
    mon_fichier.close()
    template = template.replace("%%tableau_des_routes%%", template_table  )
    template = template.replace("%%date_du_jour%%", now.strftime("%d/%m/%Y %H:%M") )
    mon_fichier = open("rendu/index.html", "wb")
    mon_fichier.write(template)
    mon_fichier.close()

    #persistance du fichier d'autocomplétion
    json.dump(autocomplete, open('rendu/osm_parcours.json', "w"), indent=4)

if __name__ == '__main__':
    #save_geojson_to_file(extract_geojson_from_navitia('route:RTP:1330511_R'))
    #render_all()
    to_html()
