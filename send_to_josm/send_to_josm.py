#!/usr/bin/env python
# coding: utf-8

import requests
import csv
import sys
import argparse

def guess_osm_id_format(sample_osm_id):
    #TODO : only works for relation for now
    try:
        tmp = int(sample_osm_id.split("r")[-1])  # r10512380
        return "use_as_is"
    except:
        try:
            tmp = int(sample_osm_id.split("/")[-1])  # relation/10512380
            return "slash_split"
        except:
            try:
                tmp = int(sample_osm_id.split(":")[-1])  # relation:10512380
                return "two_points_split"
            except:
                print(
                    "Error: Could not guess format of osm_id (try for instance r10512380)"
                )
                sys.exit()

parser = argparse.ArgumentParser(
    prog="Send to josm",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description="A script to load OSM objets in JOSM",
)

parser.add_argument(
        "input_file",
        metavar="FILE",
        type=argparse.FileType("r"),
        nargs="?",
        default="osm.csv",
        help="a csv file with at least an osm_id column",
    )

parser.add_argument(
        "--dry-run",
        "-d",
        action='store_true',
        help="do not load in JOSM, only print load url",
    )

parser.add_argument(
        "--load-one",
        "-o",
        action='store_true',
        help="only load first row in JOSM",
    )


args = parser.parse_args()

josm_template_url = "http://localhost:8111/load_object?objects="

dry_run = args.dry_run
load_one = args.load_one

init_done = False
tags_to_add = []

csv_reader = csv.DictReader(args.input_file, delimiter=',')
for row in csv_reader:
	if not init_done:
		if not "osm_id" in row:
			print("Error: need an 'osm_id' column with valid osm_id (for instance r10512380)")
			sys.exit()
		if len(row.keys()) > 1:
			tags_to_add = [column for column in row.keys() if column != "osm_id"]
		
		osm_id_format = guess_osm_id_format(row["osm_id"])
		
		init_done = True
	
	if osm_id_format == "use_as_is":
		osm_id = row["osm_id"]
	elif osm_id_format == "slash_split":
		osm_id = "{}{}".format("r", row["osm_id"].split("/")[-1])
	elif osm_id_format == "two_points_split":
		osm_id = "{}{}".format("r", row["osm_id"].split(":")[-1])
	
	if not tags_to_add:
		josm_url = "{}{}".format(josm_template_url, osm_id)
	else :
		tags_list = "|".join(["{}={}".format(col,row[col]) for col in tags_to_add])
		tags = "&addtags={}".format(tags_list)
		
		josm_url = "{}{}{}".format(josm_template_url, osm_id, tags)
	
	if dry_run:
		print(josm_url)
		sys.exit()
	
	if load_one:
		requests.get(josm_url)
		sys.exit()
	
	requests.get(josm_url)


