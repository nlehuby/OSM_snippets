#-------------------------------------------------------------------------------
# Name:        navitia2OSM.py
#
# Author:      @nlehuby - noemie.lehuby(at)canaltp.fr
#
# Created:     04/04/2014
# Licence:     WTFPL
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import requests
import json
import xmltodict
import logging
from logging.handlers import RotatingFileHandler


def Navitia_stop_points_nearby(longitude, latitude, distance) :
    """ recherche tous les stop_points à moins de [distance] mètres du point (longitude, latitude).
    """
    appel_nav = requests.get("http://api.navitia.io/v1/coverage/paris/coords/"+ str(longitude) +';'+ str(latitude) +"/places_nearby?type[]=stop_point&distance=" + str(distance), headers={'Authorization': 'my-api-key'})
    data_nav = json.loads(appel_nav.content)

    if data_nav['pagination']['total_result'] == 0:
        log.info( "Pas de résultats")
        return 0

    log.info( "il y a " + str(data_nav['pagination']['total_result']) + " résultats :")

    resultats = set()
    for resultat in data_nav['places_nearby'] :
        log.info( "--> " + str(resultat['stop_point']['name'].encode('utf-8').title()) + " : à " + str(resultat['distance']) + " mètres.")
        resultats.add(str(resultat['stop_point']['name'].encode('utf-8').title()))
    return list(resultats)

#test de fonction :
#Navitia_stop_points_nearby(2.2959928,48.8631204,100)

def send_to_JOSM(id_arret_bus, nom_arret_bus) :
    """ crée un fichier JOSM pour l'ajout du nom nom_arret_bus au node id_arret_bus.
    """
    #appel de l'API OSM
    appel = requests.get('http://api.openstreetmap.org/api/0.6/node/' + str(id_arret_bus))
    obj = xmltodict.parse(appel.content)

    # tags généraux du fichier
    del obj['osm']['@attribution']
    del obj['osm']['@license']
    del obj['osm']['@copyright']

    obj['osm']['@generator'] = "powered by navitia.io python script"

    # tags spécifiques du noeud
    obj['osm']["node"]['@action'] = 'modify'

    try:
       obj['osm']["node"]['tag'][0]
    except :
       #il n'y a qu'un seul tag, donc il faut construire la liste soi-même
        del obj['osm']["node"]['tag']
        obj['osm']["node"]['tag'] = []

        tag = dict()
        tag['@k'] = 'highway'
        tag['@v'] = 'bus_stop'
        obj['osm']["node"]['tag'].append(tag)


    tag = dict()
    tag['@k'] = 'name'
    tag['@v'] = nom_arret_bus
    obj['osm']["node"]['tag'].append(tag)

    tag = dict()
    tag['@k'] = 'source:name'
    tag['@v'] = 'opendata RATP - navitia.io'
    obj['osm']["node"]['tag'].append(tag)

    #reconstitution du fichier .osm
    #log.debug( xmltodict.unparse(obj, pretty=True))
    fichier = open(str(id_arret_bus) + '.osm', 'w')
    fichier.write(xmltodict.unparse(obj).encode('utf-8'))
    fichier.close()

#test de fonction :
#send_to_JOSM(2522119878,"ici, c'est Boissy")


if __name__ == '__main__':
    # Gestion des logs
    ##soigneusement pompé sur http://sametmax.com/ecrire-des-logs-en-python/ ;)
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
    file_handler = RotatingFileHandler('NAViTiA2OSM.log', 'a', 1000000, 1)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)
    steam_handler = logging.StreamHandler()
    steam_handler.setLevel(logging.WARNING)
    log.addHandler(steam_handler)
    ##

    #requete = "http://api.openstreetmap.fr/oapi/interpreter?data=[out:json];node%28area:3600007444%29[%22highway%22=%22bus_stop%22][%22shelter%22=%22yes%22][name!~%27.%27];out%20body;" #avec abri, à Paris > 216
    #requete = 'http://api.openstreetmap.fr/oapi/interpreter?data=[out:json][timeout:25];area(3600105794)->.area;node["highway"="bus_stop"]["name"!~"."](area.area);out meta qt;' # à Bonneuil sur Marne
    #requete = 'http://api.openstreetmap.fr/oapi/interpreter?data=[out:json][timeout:25];area(3600107966)->.area;node["highway"="bus_stop"]["name"!~"."](area.area);out meta qt;' # à Boissy-Saint-Léger
    requete = 'http://api.openstreetmap.fr/oapi/interpreter?data=[out:json][timeout:125];area(3600007444)->.area;node["highway"="bus_stop"]["name"!~"."](area.area);out meta qt;' # à Paris > 267


    appel = requests.get(requete)
    data_OSM = json.loads(appel.content)

    sans_nom = []
    avec_nom = []

    for bus_stop in data_OSM["elements"] :
        log.info(bus_stop["id"])
        lat = bus_stop["lat"]
        lon = bus_stop["lon"]

        #print Navitia_stop_points_nearby(lon,lat,100)
        test = Navitia_stop_points_nearby(lon,lat,10)
        if test == 0 :
            sans_nom.append(bus_stop["id"])
        else :
            avec_nom.append([bus_stop["id"], test])

    log.warning( "---")
    log.warning( "il y a " + str(len(data_OSM["elements"])) + " arrêts de bus OSM sans nom.")
    log.warning( "il y a " + str(len(avec_nom)) + " arrêts de bus situés à moins de 10 mètres d'un arrêt présent navitia.io")
    log.warning( "il y a " + str(len(sans_nom)) + " arrêts de bus pour lequels aucun arrêt n'a été trouvé dans navitia.io")

##    for arret in avec_nom :
##        if len(arret[1]) == 1 :
##            log.warning( str(arret[0]) + ' : ' + arret[1][0])
##            send_to_JOSM(arret[0],arret[1][0])

