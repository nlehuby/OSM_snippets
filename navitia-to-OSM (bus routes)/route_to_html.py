#-------------------------------------------------------------------------------
# Author:      nlehuby
#
# Created:     28/01/2015
# Copyright:   (c) nlehuby 2015
# Licence:     MIT
#-------------------------------------------------------------------------------
#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import datetime
import csv


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
    result_int.sort(key=lambda osm_route: int(osm_route[1]))
    result_other.sort(key=lambda osm_route: osm_route[1])
    result_list = result_int + result_other


    with open("rendu/sources/osm_parcours.csv", "wb") as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for line in result_list:
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
        parcours['label'] = "[{}] {} > {}".format(osm_route[5], osm_route[1], osm_route[3])

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
    to_html()
