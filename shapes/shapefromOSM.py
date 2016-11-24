#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from shapely.geometry import LineString
from shapely.ops import linemerge

def get_shapes_from_osm(relation_id):
    overpass = 'http://www.overpass-api.de/api/interpreter?data=[out:json][timeout:25];relation('+relation_id+');out body;>;out skel qt;>;out skel qt;'

    resp_overpass = requests.get(overpass)
    resutl = resp_overpass.json()['elements']

    relations = []
    ways = []
    nodes = []

    #stocker tous les nodes/ways dans une structure pour pouvoir les utiliser plus facilement plus tard
    for elem in resutl:
        if elem['type']=="relation" :
            relations.append(elem)
        if elem['type']=="way" :
            ways.append(elem)
        if elem['type']=="node" :
            nodes.append(elem)

    relation = relations[0]
    print ("traitement de la relation {}".format(relation['id']))

    ways_linestrings = []

    for member in relation['members']:
        if member['type'] == "way":
            current_way_details = [way for way in ways if way['id']==member['ref']]
            if len(current_way_details) != 1 :
                print ('>> KO (en cherchant le chemin {})'.format(member['ref']))
                continue
            nodes_in_current_way = []
            for current_node in current_way_details[0]['nodes'] :
                current_node_details = [node for node in nodes if node['id'] == current_node]
                if len(current_node_details) < 1 :
                    print ('>> KO (en cherchant les noeuds {})'.format(current_node))
                    continue
                nodes_in_current_way.append(current_node_details[0])

            #on construit une ligne avec les noeuds
            points_nodes = [(node['lon'], node['lat']) for node in nodes_in_current_way]
            way_linestring = LineString(points_nodes)
            ways_linestrings.append(way_linestring)

    #on fusionne tous les chemins en un
    final_linestring = linemerge(ways_linestrings)

    print(final_linestring)

    if final_linestring.geom_type == "LineString":
        print(list(final_linestring.coords))
    else :
        for a_line in final_linestring.geoms :
            print(list(a_line.coords))

    return "OK"


# get_shapes_from_osm('1257117')
# get_shapes_from_osm('1254451')
get_shapes_from_osm('1254455')
