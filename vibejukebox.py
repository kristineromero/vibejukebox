print "Python is working"
"""
import urllib
import urllib2
import re
import re, string, timeit
import json


#songs = ["spotify:track:4pGqFOfzvfe6avb9kbZicC" ,"spotify:track:4RL77hMWUq35NYnPLXBpih","spotify:track:6Gcr0v9WVP57pWCphoU7FY", "spotify:track:4o0NjemqhmsYLIMwlcosvW", "spotify:track:5ve0BYRZZ2aoHFqZMxqYgt"]
# A songs = ["spotify:track:5etr4CxKuyDKCV2c7YUfPM" ,"spotify:track:597RmuFdTyn7TW3rS2ZSkA","spotify:track:798GAE5BFFx7yCcloeTpCr","spotify:track:6UgyytbryrvB6ZpvpjffM9", "spotify:track:3iUmDHFfMMwa4L0fyA3PbH"]
songs = ["spotify:track:2kW59AS9OrpFsuXbi2939R", "spotify:track:4c9WmjVlQMr0s1IjbYO52Z", "spotify:track:6nAD4H0ujyEeBTxbXZkZeC", "spotify:track:2QzMJkYUhThZxM94ahgOzN", "spotify:track:4LloVtxNZpeh7q7xdi1DQc"]
#a function to get the artist ids for each song loaded 
#relevant to use for getTerms, and findSimilar

def getArtists(songs):
     find_artist_final = []
   
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

artistIds =  getArtists(songs)

#print artistIds


##Find weights is used to find how similar the artists are and give weights
##depending how similar they are to the other artists in the list
#the idea is to remove outliers in music added by comparing agains a list of descriptive terms
#this is used later as a weighting system for findSimilarArtists


def findWeights(artistids):
    artist_dict = {}
    terms = []
    
    #gets list of terms associated with each artist
    for i in range(len(artistids)):
        createURL = "http://developer.echonest.com/api/v4/artist/terms?api_key=YZZS9XI0IMOLQRKQ6" + artistids[i] +"&format=json"
        aResp = urllib2.urlopen(createURL);
        web_pg = aResp.read();
        find_term = []
        for item in web_pg.split(","):
            if "name" in item:
                item = item.split(":")[1]
                find_term.append(item)
        if ' "pop"' in find_term:
            find_term.remove(' "pop"')
        artist_dict[artistids[i]] = find_term[0:4];
        terms.extend(find_term[0:4])
    
    #find duplicates of artists and creates a dictionary of spotifyid and terms
    result = {}
    for key,value in artist_dict.items():
        if value not in result.values():
            result[key] = value
    artist_dict = result
    #return artist_dict
    
    
   
    ##tableing the list of terms to find the top terms
    terms_dict = {}
    for i in range(len(terms)):
        if terms[i] not in terms_dict.items():
            find_count = terms.count(terms[i])
            terms_dict[terms[i]] = find_count
    #sorted_terms_dict = sorted(terms_dict.iteritems(), key=operator.itemgetter(1))
    #return terms_dict
  
  ##Right now our tools are a list of top terms, a list of all artists with terms associated with them
  ##now we use the counts and the 
    weights = {}
    for key in artist_dict:
        getWeight=0
        for value in artist_dict[key]:
            
            
            if value in terms:
                
                getWeight = getWeight+terms_dict[value]
        weights[key] = getWeight
    
    return weights
  
    
findingWeights = findWeights(artistIds)
print findingWeights



def GetSimilarArtists(weights, artists):
    createURL = "http://developer.echonest.com/api/v4/artist/similar?api_key=YZZS9XI0IMOLQRKQ6"
    for i in artists:
        createURL += i + "^" + str(weights[i])
    simMake = urllib2.urlopen(createURL);
    echonestSim = simMake.read();
    findSimilarArtist = []
    for artist in echonestSim.split(":"):
        if "name" in artist:
           artistShrink = artist.split(",")[0]
           artistShrink= artistShrink.translate(None, string.punctuation)
           artistShrink = artistShrink.strip()
           findSimilarArtist.append(artistShrink)
    return findSimilarArtist[0:20]    
  #return findSimilarArtist[0:5]
    
    

simArtist = GetSimilarArtists(findingWeights, artistIds)

print simArtist

def MakePlaylist(similarArtists, songs):
    #get tempo and aliveness for songs added
    added_ids = []
    what = []
    for i in songs:
        shrink = i.replace("spotify:track:", "")
        createURL = "http://developer.echonest.com/api/v4/track/profile?api_key=YZZS9XI0IMOLQRKQ6&id=spotify-WW:track:"+ shrink +"&format=json"
        getURL = urllib2.urlopen(createURL);
        clean_page = getURL.read();
        clean_page = clean_page.replace(":", ",")
        clean_page = clean_page.split(",")
        id = clean_page[clean_page.index(' "song_id"')+1].translate(None, string.punctuation)
        added_ids.append(id.strip())
   
    energy = []
    tempo=[]
    dance = []
    for i in added_ids:
        createURL ="http://developer.echonest.com/api/v4/song/profile?api_key=YZZS9XI0IMOLQRKQ6&format=json&id="+i+ "&bucket=audio_summary"
        getURL = urllib2.urlopen(createURL);
        clean_page = getURL.read();
        
        energy_find = clean_page.index("energy")
        energy.append(float(clean_page[energy_find+9: energy_find+14]))
        
        tempo_find = clean_page.index("tempo")
        tempo.append(float(clean_page[tempo_find+7: tempo_find+14]))
    
        dance_find = clean_page.index("danceability")
        dance.append(float(clean_page[dance_find+15: dance_find+20]))
   
   ##set limits
    min_danceability = dance[dance.index(min(dance))]
    max_danceability = dance[dance.index(max(dance))]
                                   
    min_tempo = tempo[tempo.index(min(tempo))]
    max_tempo = tempo[tempo.index(max(tempo))]
                            
    min_energy = energy[energy.index(min(energy))] 
    max_energy = energy[energy.index(max(energy))]
    
                                   
    playlist = []
    for i in similarArtists:
        createURL="http://developer.echonest.com/api/v4/song/search?api_key=YZZS9XI0IMOLQRKQ6&artist_id=" +i+ "&bucket=id:spotify-WW&bucket=tracks&sort=song_hotttnesss-desc&min_danceability=" + str(min_danceability) + "&max_danceability=" + str(max_danceability) + "&results=2"
        getURL = urllib2.urlopen(createURL);
        clean_page = getURL.read();
        if "spotify-WW:track" in clean_page:
            get_track = clean_page[clean_page.index("spotify-WW:track")-1:clean_page.index("spotify-WW:track")+60].replace(":", ",").split(",")[2].translate(None, string.punctuation)
            playlist.append("spotify:track:" + get_track)
        
    return playlist
        
        

finished = MakePlaylist(simArtist, songs)

print finished
"""
