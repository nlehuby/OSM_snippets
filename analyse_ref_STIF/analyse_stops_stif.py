#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import requests

if __name__ == '__main__':
    #on lit le fichier du STIF et on stocke les références
    ref_STIF_list = []
    with open('stops_data/stop_extensions.txt', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader :
            ref_STIF_list.append(row["ZDEr_ID_REF_A"])

    #on lit les stops d'après OSM et on vérifie que les valeurs sont connues
    with open('stops_data/ref_stif.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row['ref:FR:STIF']:
                print("problème d'extraction sur {}".format(row['@id']))
                continue
            if ';' in row['ref:FR:STIF'] :
                for a_ref in row['ref:FR:STIF'].split(';'):
                    if a_ref.strip() not in ref_STIF_list :
                        print ("La ref:FR:STIF {} n'existe pas ou plus, sur le noeud {}".format(a_ref, row['@id']))
                        #TODO : envoyer à Osmose ?
                        #pass
                continue

            try :
                int(row['ref:FR:STIF'])
            except ValueError :
                print ("la ref:FR:STIF '{}' n'est pas numérique sur le noeud {}".format(row['ref:FR:STIF'], row['@id']))
                continue

            if row['ref:FR:STIF'] not in ref_STIF_list :
                print ("La ref:FR:STIF {} n'existe pas ou plus, sur le noeud {}".format(row['ref:FR:STIF'], row['@id']))
