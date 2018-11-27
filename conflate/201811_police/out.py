import json

with open('results_pn.json', 'r') as input:
    results = json.load(input)
    output = []
    for elem in results['features']:
        if elem['properties']['action'] == "modify":
            elem['properties']['@id'] = "{}/{}".format(elem['properties']['osm_type'],elem['properties']['osm_id'])
            tags_to_add = [prop for prop in elem['properties'].keys() if prop.startswith("tags_new")]
            tags = tags_to_add + ['@id', 'ref_id']
            if tags_to_add:
                for t in elem['properties'].copy():
                    if t not in tags:
                        del(elem['properties'][t])

                output.append(elem)


with open('results-pn-tocheck.json', 'w') as fp:
    json.dump({"type": "FeatureCollection", "features":output}, fp, indent=4)
