import os
from flask import Flask
import urllib
import urllib2
import re
import re, string, timeit
import json


# initialization
app = Flask(__name__)
app.config.update(
    DEBUG = True,
)

# controllers
@app.route("/")

#a function to get the artist ids for each song loaded 
#relevant to use for getTerms, and findSimilar

def getArtists(songs):
     find_artist_final = []
     songs = ["spotify:track:2kW59AS9OrpFsuXbi2939R", "spotify:track:4c9WmjVlQMr0s1IjbYO52Z", "spotify:track:6nAD4H0ujyEeBTxbXZkZeC", "spotify:track:2QzMJkYUhThZxM94ahgOzN", "spotify:track:4LloVtxNZpeh7q7xdi1DQc"]
   
     for i in range(len(songs)):
         createURL = "http://ws.spotify.com/lookup/1/?uri=" + songs[i]
         aResp = urllib2.urlopen(createURL);
         web_pg = aResp.read();
         find_artist =[]
         for item in web_pg.split("\n"):
            if "spotify:artist" in item:
                find_artist.append(item)
                break                
         find_artist = find_artist[0].split(":",2)[2]
         find_artist = find_artist.translate(None, string.punctuation)
         find_artist_final.append("&id=spotify-WW:artist:"+ find_artist)
     
     
     return find_artist_final

# launch
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
