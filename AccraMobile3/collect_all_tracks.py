# coding: utf-8
### nlehuby - AccraMobile3

import requests
import xml.dom.minidom as dom

def dl_track(track_url, track_name):
    #TODO : skip download if the file already exist ?
    r = requests.get(track_url)
    with open(track_name, "wb") as code:
        code.write(r.content)

def download_all_track_from_user(user):
    url1 = "http://www.openstreetmap.org/user/"+user+"/traces/rss"
    rss = requests.get(url1)

    dom3 = dom.parseString(rss.content)
    tracks = dom3.getElementsByTagName("item")

    for a_track in tracks:
        title_elem = a_track.getElementsByTagName('title')[0]
        title = title_elem.childNodes[0].data
        url_elem = a_track.getElementsByTagName('link')[0]
        track_id = url_elem.childNodes[0].data.split('/')[-1]
        track_url = "http://www.openstreetmap.org/trace/{}/data".format(track_id)
        dl_track(track_url, title)

if __name__ == '__main__':
    for index in range(10):
        user_id = "accramobileghana" + str(index +1)
        download_all_track_from_user(user_id)
