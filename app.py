import urllib
import urllib2
import re
import re, string, timeit
import json
from flask import Flask, jsonify, request
import pyechonest
 
app = Flask(__name__)


@app.route('/', methods = ['POST'])

class VibeJukeBox(object):
    
    #### initialize self ####
    
    def __init__(self,songs):
        self.songs =  request.json['songs']
    


    def getArtists(self):
        
        ### API Key Configuration
        
        from pyechonest import config
        config.ECHO_NEST_API_KEY="YZZS9XI0IMOLQRKQ6"
        
        
        ######################          Getting Artists + Song Info           ########################
        
        from pyechonest import track
        songs = self.songs
        artists = []
        EchoNestSongId = []
        EchoNestArtistId = []
        energy = []
        dance = []
        tempo = []
        for i in range(len(songs)):
            songs[i] = songs[i].replace("spotify:track:", "spotify-WW:track:")
            t = track.track_from_id(songs[i])
            EchoNestSongId.append(t.song_id)
            EchoNestArtistId.append(t.id)
            artists.append(t.artist)
            if "energy" in vars(t):
                energy.append(t.energy)
            if "danceability" in vars(t):
                dance.append(t.danceability)
            if "tempo" in vars(t):
                tempo.append(t.tempo)
        self.artist = artists
        self.EchoNestSongId = EchoNestSongId
        self.EchoNestArtistId = EchoNestArtistId    
        self.energy = energy
        self.tempo = tempo
        self.dance = dance
        
        
        
        
        ######################          Terms Per Artist // All Terms           ########################
        
        ### Building Terms from Artists
        artist_dict = {}
        terms = []
        from pyechonest import artist
        
        ##Creates a dictionary with artists and terms associated with that artist, also creates a vector of all terms
        for i in range(len(artists)):
                artistTerm = artist.Artist(artists[i]).terms
                find_term = []
                
                for k in range(4):
                    find_term.append(artistTerm[k]['name'])
                artist_dict[artists[i]] = find_term;
                terms.extend(find_term[0:4])   
        
        self.terms = terms
        self.artist_dict  = artist_dict  
        
        
        ######################           Weights for Terms           ########################
        ##Creates weights for each term based on the number of times it appeared in artist list
        
        terms_dict = {}
        for i in range(len(terms)):
            if terms[i] not in terms_dict.items():
                find_count = terms.count(terms[i])
                terms_dict[terms[i]] = find_count
                    
        self.terms_dict = terms_dict
        
        
        ######################           Weights for Artists            ########################
        ## Adds all of the weights per term per artist to get the overall weight for an artist
        ## 5 subtracted from total weight (number of terms used per artist, each guarenteed a count of 5)
        weights = {}
        
        for key in artist_dict:
            getWeight=0
            for value in artist_dict[key]:
                if value in terms:
                    getWeight = getWeight+terms_dict[value]
            weights[key] = getWeight-5
            
        
        #checking weights
        #for key in weights:
        #    print  key +":" + str(weights[key]) 
        #NOTE::: If we ever want to add more than 5 songs, we have to order the dictionary and select top 5 artists of terms.
        
       
        
        ######################          Finding Similar Artists w/Weights           ########################
        
        createURL = "http://developer.echonest.com/api/v4/artist/similar?api_key=YZZS9XI0IMOLQRKQ6"
        
        for key in weights:
            createURL += "&id=" +artist.Artist(key).id +"^" + str(weights[key])
        
        simMake = urllib2.urlopen(createURL);
        echonestSim = simMake.read();
        findSimilarArtist = []
        for artist in echonestSim.split(":"):
            if "name" in artist:
                artistShrink = artist.split(",")[0]
                artistShrink= artistShrink.translate(None, string.punctuation)
                artistShrink = artistShrink.strip()
                findSimilarArtist.append(artistShrink)
        findSimilarArtists = findSimilarArtist[1:20]
        
        self.findSimilarArtists = findSimilarArtists
        
        
        ######################          Setting Limits on Audio for Song Rec          ########################
        
        
        min_danceability = dance[dance.index(min(dance))]
        max_danceability = dance[dance.index(max(dance))]
                                               
        min_tempo = tempo[tempo.index(min(tempo))]
        max_tempo = tempo[tempo.index(max(tempo))]
                                        
        min_energy = energy[energy.index(min(energy))] 
        max_energy = energy[energy.index(max(energy))]
                
                                               
        
               
        ######################          Selecting Top Songs for Recommended Artists + Creates Playlist         ########################        
        playlist = []
        for i in findSimilarArtists:
            createURL="http://developer.echonest.com/api/v4/song/search?api_key=YZZS9XI0IMOLQRKQ6&artist_id=" +i+ "&bucket=id:spotify-WW&bucket=tracks&sort=song_hotttnesss-desc&min_danceability=" + str(min_danceability) + "&max_danceability=" + str(max_danceability) + "&results=2"
            getURL = urllib2.urlopen(createURL);
            clean_page = getURL.read();
            if "spotify-WW:track" in clean_page:
                get_track = clean_page[clean_page.index("spotify-WW:track")-1:clean_page.index("spotify-WW:track")+60].replace(":", ",").split(",")[2].translate(None, string.punctuation)
                playlist.append("spotify:track:" + get_track)        
        
        self.playlist = jsonify( { 'playlist': playlist} )
  
        


test = VibeJukeBox(songs = songs)
test2 = test.getArtists()

return test.playlist
  
    
if __name__ == '__main__':
    app.run(debug = True)
    
