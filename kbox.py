"""
Export song list from KBox
"""

import json
import requests
from xml.etree import cElementTree as ElementTree
import csv

# song data tags
tags = [
    ('id', 'song-search-id hidden'),
    ('artist', 'artist-name'),
    ('title', 'song-title'),
]


def parse_song(x):
    """Parse song string"""

    try:
        x = ElementTree.fromstring(x.replace('&', '&amp;'))
        song = {
            key: x.find('span[@class="{0}"]'.format(name)).text
            for key, name in tags
        }
        return song
    except ElementTree.ParseError as e:
        print e
        print x
        return {}


# pull data from site
request = requests.get('http://www.kbox.com.au/search.php')
data = json.loads(request.text)

hits = int(data['total_hits'])
print "Found {0} results.".format(hits)

# parse out the songs
songs = [
    x for x in (
        parse_song(html)
        for i, html in data.items()
        if i.isdigit()
    ) if x
]
key = lambda x: (x['artist'].lower(), x['title'].lower())
songs = sorted(songs, key=key)

print "Parsed {0} songs ({1} missing).".format(len(songs), hits - len(songs))

# write out csv
with open('songs.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames=[x for x, _ in tags])
    writer.writeheader()
    writer.writerows(songs)
