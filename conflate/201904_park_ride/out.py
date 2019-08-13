import json

with open('resultats.json', 'r') as input:
    results = json.load(input)
    output = []
    for elem in results['features']:
        if elem['properties']['action'] == "create":
                output.append(elem)


with open('results-to_crat.json', 'w') as fp:
    json.dump({"type": "FeatureCollection", "features":output}, fp, indent=4)
