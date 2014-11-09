#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#-------------------------------------------------------------------------------
# Name:        navitia2OSM.py
#
# Author:      @nlehuby - noemie.lehuby(at)gmail.com
#
# Created:     04/06/2014
# Licence:     WTFPL
#-------------------------------------------------------------------------------

import requests
import demjson
import smtplib

url = "http://taginfo.openstreetmap.org/api/4/key/values?key=brewery:note"
appel_taginfo = requests.get(url)

data_tag = demjson.decode(appel_taginfo.content)

if data_tag['total'] == 0:
	print "Pas de résultats, rien de neuf ..."
else :
    print "Il y a des résultats !"
    FROM = 'openbeermap@gmail.com'
    TO = ['openbeermap@gmail.com'] 
    SUBJECT = "Il y a du nouveau sur taginfo !"
    TEXT = "Il y a "+ str(data_tag['total']) + " nouveaux résultats : " + url 
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s""" % (FROM, ", ".join(TO), SUBJECT, TEXT)
    smtp = smtplib.SMTP()
    smtp.connect('serveur',587)
    smtp.starttls()
    smtp.login('login', 'password')
    smtp.sendmail(FROM, TO, message)
    smtp.close()
        
print data_tag['total']
