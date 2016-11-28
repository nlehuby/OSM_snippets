#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import transitfeed #impose python2 :(
import requests

#Les trucs en dur
AGENCY_NAME = "Pep's"
AGENCY_URL = "http://reseau-peps"
GTFS_FEED_PATH = "peps_gtfs_from_osm.zip"
ROUTE_FREQUENCY = 12 # le bus passe toutes les ROUTE_FREQUENCY minutes. S'applique à toutes les lignes
TRIP_DURATION = 1 # le trajet de bout en bout dure TRIP_DURATION heures. S'applique à toutes les lignes

#TODO - utiliser une fonction de OSMvsNavitia (bus routes) pour récupérer la liste depuis le wiki ou overpass plutôt que la mettre en dur ?
RELATIONS_LIST = [3936088, 5470995, 6145134, 3950998, 6147761, 3957778, 6130401, 3955545, 6117018, 6147732, 3069536, 2545213, 2657536, 6116989, 3941999, 3936208, 6145086, 6144401, 3948425, 3936863, 2659171, 3940843, 6101988, 6116961, 3937174, 3936704, 6138427, 3937116, 2659188, 3937529, 6147927]


####

schedule = transitfeed.Schedule()
schedule.AddAgency(AGENCY_NAME, AGENCY_URL, "Europe/Paris")

service_period = schedule.GetDefaultServicePeriod()
service_period.SetStartDate("20160101")
service_period.SetEndDate("20161230")
service_period.SetWeekdayService(True)

stops_id = {}
routes_tags = {}
nodes = []
for relation_id in RELATIONS_LIST:
    overpass_url = 'http://www.overpass-api.de/api/interpreter?data=[out:json][timeout:25];relation({});out body;>;out body qt;>;out skel qt;'.format(relation_id)
    #TODO : à voir si utiliser direction l'API OSM en get ne serait pas plus efficace qu'overpass

    resp_overpass = requests.get(overpass_url)
    result = resp_overpass.json()['elements']

    for elem in result:
        if elem['type']=="node" :
            nodes.append(elem)
        if elem['type']=="relation" :
            print ("traitement de la relation {}".format(elem['id']))

            routes_tags[relation_id] = elem['tags']
            stops_id[relation_id] = []

            for a_stop in elem['members']:
                    if a_stop['role'] == 'stop':#TODO : vérifier le schéma public_transport:version pour savoir si on doit utiliser stop ou platform
                       stops_id[relation_id].append(a_stop['ref'])
            if not stops_id[relation_id]:
                print ("Erreur : ce parcours OSM est ko (pas d'arrêts) : {}".format(route_id))

gtfs_stops = {}
unique_stops_id = set([item for sublist in stops_id.values() for item in sublist])
for a_stop in unique_stops_id:
    current_node_details = [node for node in nodes if node['id'] == a_stop]
    if len(current_node_details) < 1 :
        print ('>> KO (en cherchant le noeud {})'.format(a_stop))
        continue
    stop_info = current_node_details[0]
    stop_name = "<Arrêt sans nom>"
    if 'name' in stop_info['tags']:
        stop_name = stop_info['tags']['name']
    gtfs_stops[a_stop] = schedule.AddStop(lng = stop_info['lon'], lat = stop_info['lat'], name = stop_name, stop_id = str(a_stop))
    #on persiste pour pouvoir leur attribuer les horaires ultérieurement

for a_route_id in routes_tags:
    route_name = routes_tags[a_route_id]['name'] #TODO : gérer le cas pas de name / ref
    print (">> Route & Trip : " + route_name)
    gtfs_route = schedule.AddRoute(route_id = a_route_id ,short_name = routes_tags[a_route_id]['ref'], long_name = route_name, route_type = "Bus")
    gtfs_trip = gtfs_route.AddTrip(schedule)
    gtfs_trip.AddFrequency("06:00:00", "21:00:00", ROUTE_FREQUENCY * 60)

    departure_time = datetime.datetime(2008, 11, 22, 6, 0, 0)
    for index_stop, stop_id in enumerate(stops_id[a_route_id]):
        gtfs_stop = gtfs_stops[stop_id]
        if index_stop == 0 :
            gtfs_trip.AddStopTime(gtfs_stop, stop_time = departure_time.strftime("%H:%M:%S"))
            print (">>>> Premier arrêt")
        elif index_stop == len(stops_id[a_route_id]) -1 :
            print (">>>> Dernier arrêt")
            departure_time += datetime.timedelta(hours = TRIP_DURATION)
            gtfs_trip.AddStopTime(gtfs_stop, stop_time = departure_time.strftime("%H:%M:%S"))
            for secs, stop_time, is_timepoint in gtfs_trip.GetTimeInterpolatedStops():
                if not is_timepoint:
                    print('>>>> Interpolation au milieu')
                    stop_time.arrival_secs = secs
                    stop_time.departure_secs = secs
                    gtfs_trip.ReplaceStopTimeObject(stop_time)
        else :
            gtfs_trip.AddStopTime(gtfs_stop)

schedule.Validate()
schedule.WriteGoogleTransitFeed(GTFS_FEED_PATH)
