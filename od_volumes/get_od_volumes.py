#!/usr/bin/env python
# coding: utf-8

from transporthours.main import Main
import datetime
import csv


"""
## preprocessing

cat osm-transit-extractor_route_points.csv |xsv search -s role platform |xsv select '!role' > route_stops.csv

cat osm-transit-extractor_lines.csv |xsv select line_id,name,network,frequency,opening_hours,frequency_exceptions > lines.csv

xsv join line_id lines.csv line_id osm-transit-extractor_line_routes.csv |xsv select line_id,name,network,frequency,opening_hours,frequency_exceptions,route_id > line_routes.csv

xsv join route_id line_routes.csv route_id route_stops.csv |xsv select line_id,name,network,frequency,opening_hours,frequency_exceptions,route_id,stop_id > line_route_stops.csv
"""


myTh = Main()


data = []
with open("line_route_stops.csv") as csvfile:
    tt = csv.DictReader(csvfile)
    for elem in tt:
        elem['interval'] = elem.get("frequency")
        elem['interval:conditional'] = elem.get("frequency_exceptions")
        InterpretedHours = myTh.tagsToHoursObject(elem)
        if InterpretedHours['allComputedIntervals']:
            nb_passages = 0
            for period, interval in InterpretedHours['allComputedIntervals'][0]['intervals'].items():
                start,end = period.split('-')
                period_duration = datetime.datetime.strptime(end, '%H:%M') - datetime.datetime.strptime(start, '%H:%M')
                interval_datetime = datetime.timedelta(minutes = interval)
                nb_passages += period_duration/interval_datetime
    
            elem['nb_passages'] = nb_passages

        data.append(elem)

for i in range(len(data) - 1):
    first_stop = data[i]
    second_stop = data[i+1]
    if first_stop['route_id'] != second_stop['route_id']:
        continue
    if 'nb_passages' not in first_stop:
        continue
    print("{},{},{}".format(first_stop['stop_id'], second_stop['stop_id'], int(first_stop['nb_passages'])))

