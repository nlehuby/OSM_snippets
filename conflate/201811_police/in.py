import csv
import json

output = []

with open("export-pn.csv") as target:
    reader = csv.DictReader(target, delimiter=';')
    for row in reader:
        output.append(row)

with open('pn.json', 'w') as fp:
    json.dump(output, fp, indent=4)
