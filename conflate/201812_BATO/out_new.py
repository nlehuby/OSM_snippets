import json

with open('results_again.json', 'r') as input:
    results = json.load(input)
    output = []
    for elem in results['features']:
        if elem['properties']['action'] == "create":
                output.append(elem)

print(len(output))
with open('results-news-again.json', 'w') as fp:
    json.dump({"type": "FeatureCollection", "features":output}, fp, indent=4)
