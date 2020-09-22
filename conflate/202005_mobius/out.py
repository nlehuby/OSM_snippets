import json

with open('results.json', 'r') as input:
    results = json.load(input)
    output_create = []
    output_delete = []
    for elem in results['features']:
        if elem['properties']['action'] == "create":
                output_create.append(elem)
        if elem['properties']['action'] == "delete":
                output_delete.append(elem)


with open('results-to_create.json', 'w') as fp:
    json.dump({"type": "FeatureCollection", "features":output_create}, fp, indent=4)
    
with open('results-to_delete.json', 'w') as fp:
    json.dump({"type": "FeatureCollection", "features":output_delete}, fp, indent=4)
