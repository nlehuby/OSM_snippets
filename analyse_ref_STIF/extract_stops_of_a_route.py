#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Ce script réalise une extraction <<csv>> des arrêts d'un parcours opendata

from params import navitia_API_key as TOKEN
import requests


#paramétrage
navitia_API_key = TOKEN
navitia_base_url = "http://api.navitia.io/v1/coverage/fr-idf"


# Overpass :  relation(1257168);node(r:"stop");out meta;

navitia_route_id = "route:OIF:100100117:117"

appel_nav = requests.get(navitia_base_url + "/routes/{}/stop_points?count=120".format(navitia_route_id), headers={'Authorization': navitia_API_key})
if appel_nav.status_code != 200:
    print("échec à l'appel navitia")

print("stop_id, stop_name, latitude, longitude, ref:FR:STIF")
for a_stop in appel_nav.json()['stop_points']:
    code_STIF_list = [elem['value'] for elem in a_stop["codes"] if elem['type'] == "ZDEr_ID_REF_A"]
    code_STIF = ';'.join(code_STIF_list)
    print("{},{},{},{},{}".format(a_stop['id'], a_stop['name'], a_stop['coord']['lat'], a_stop['coord']['lon'], code_STIF))
