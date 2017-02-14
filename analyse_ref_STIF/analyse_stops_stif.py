#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import xmltodict
import datetime
from copy import deepcopy

def create_osmose_xml(errors):
    with open('osmose_issues_template.xml', 'r') as f:
        doc = xmltodict.parse(f.read())

    now = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    doc['analysers']['@timestamp'] = now
    doc['analysers']['analyser']['@timestamp'] = now
    doc['analysers']['analyser']['class']['@item'] = "8041"
    doc['analysers']['analyser']['class']['@tag'] = "transport en commun"
    doc['analysers']['analyser']['class']['@id'] = "1"
    doc['analysers']['analyser']['class']['@level'] = "3"
    doc['analysers']['analyser']['class']['classtext']['@lang'] = "fr"
    doc['analysers']['analyser']['class']['classtext']['@title'] = "tag erroné sur un arrêt de transport en commun d'Île-de-France"

    for error in errors :
        current_osmose_error = deepcopy(doc['analysers']['analyser']['error'][1])
        current_osmose_error['node']['@id'] = error['id']
        current_osmose_error['location']['@lat'] = error['lat']
        current_osmose_error['location']['@lon'] = error['lon']
        current_osmose_error['text']['@lang'] = "fr"
        current_osmose_error['text']['@value'] = error['label']
        current_osmose_error['fixes']['fix']['node']['@id'] = error['id']
        current_osmose_error['fixes']['fix']['node']['tag']['@k'] = 'ref:FR:STIF'


        doc['analysers']['analyser']['error'].append(current_osmose_error)

    #remove the template errors
    del doc['analysers']['analyser']['error'][0]
    del doc['analysers']['analyser']['error'][0]

    return xmltodict.unparse(doc, pretty=True)

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
        errors = []
        for row in reader:
            error = {"id" : row['@id'] }
            if not row['ref:FR:STIF']:
                print("problème d'extraction sur {}".format(row['@id']))
                continue
            if ';' in row['ref:FR:STIF'] :
                for a_ref in row['ref:FR:STIF'].split(';'):
                    if a_ref.strip() not in ref_STIF_list :
                        error['label'] = "La ref:FR:STIF {} n'existe pas ou plus".format(a_ref)
                        error['lat'], error['lon'] = row['@lat'], row['@lon']
                        errors.append(error)
                continue

            try :
                int(row['ref:FR:STIF'])
            except ValueError :
                error['label'] = "la ref:FR:STIF '{}' n'est pas numérique".format(row['ref:FR:STIF'])
                error['lat'], error['lon'] = row['@lat'], row['@lon']
                errors.append(error)
                continue

            if row['ref:FR:STIF'] not in ref_STIF_list :
                error['label'] = "La ref:FR:STIF {} n'existe pas ou plus".format(row['ref:FR:STIF'])
                error['lat'], error['lon'] = row['@lat'], row['@lon']
                errors.append(error)

    #on écrit ça au format Osmose
    xml = create_osmose_xml(errors)
    print (xml)

    #print(len(errors))

    #TODO : aussi supprimer le tag source:ref:FR:STIF voire source si ça a du sens
