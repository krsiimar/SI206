import spotipy 
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
from musixmatch import Musixmatch
import requests
import json
import os
import sqlite3

'''
class Spotify:

    def __init__(self, username, scope, client_id, client_secret, redirect_uri):
        self.username = username
        self.scope = scope
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

        self.token = util.prompt_for_user_token(self.username, self.scope, client_id = self.client_id, client_secret = self.client_secret, 
                                                           redirect_uri = self.redirect_uri)
        if self.token:
            self.sp = spotipy.Spotify(auth = self.token)
        else:
            print("Can't get token for", self.username)

    def write_cache_top_artists(self, cache_file):
        cache_json = json.dumps(self.sp.current_user_top_artists(50, 0, 'long_term'), indent = 4)
        with open(cache_file, 'w') as cache_file: 
            cache_file.write(cache_json) 

    def top_artists(self, limit, offset, time_range):
        artists_list = []
        top_artists = self.sp.current_user_top_artists(limit, offset, time_range)
        for artist in top_artists['items']:
            artist_name = artist['name']
            artist_id = artist['id']
            artists_list.append((artist_id, artist_name))
        return artists_list
        
    def top_tracks(self, limit, offset, time_range):
        tracks_list = []
        top_tracks = self.sp.current_user_top_tracks(limit, offset, time_range)
        for track in top_tracks['items']:
           track_name = track['name']
           track_id = track['id']
           tracks_list.append((track_id, track_name))
        return tracks_list

    def liveness(self, track_id):
        liveness = self.sp.audio_analysis(track_id)
        return liveness


spotify = Spotify("kristofersiimar", 'user-top-read', "c718242a780d4369866e47defc06d637", "93ca05c182d3470bbcd143090e6688a1", 'https://example.com/callback/')

#kris_top_artist = spotify.top_artists(100, 0, 'long_term')
#kris_top_songs = spotify.top_tracks(100, 0, 'long_term')


# Writing kris_top_tracks into a file 
spotify.write_cache_top_artists('top_artists_file.txt')
'''

class Musixmatch:

    def __init__(self, user_api_key):
        self.user_key = user_api_key

    def lyrics(self, artist_name, track_name):
        track_name = track_name.lower()
        artist_name = artist_name.lower()
        request = requests.get('https://api.musixmatch.com/ws/1.1/matcher.lyrics.get?format=json&callback=callback&q_artist=' + artist_name + '&q_track=' + track_name + '&apikey=' + self.user_key) 
        data = json.loads(request.text)
        try:
            return data['message']['body']['lyrics']['lyrics_body']
        except:
            return 'no lyrics'
    
    def artist_top_tracks(self, artist_name, number_of_tracks):
        track_list = []
        artist_name = artist_name.lower()
        request = requests.get('http://api.musixmatch.com/ws/1.1/track.search?q_artist=' + artist_name + '&page_size=' + str(number_of_tracks) + '&page=1&s_track_rating=desc&apikey=' + self.user_key) 
        data = json.loads(request.text)
        #print(json.dumps(data, indent = 4))
        for track in data['message']['body']['track_list']:
            track_id = track['track']['track_id']
            track_name = track['track']['track_name']
            track_list.append((track_id, track_name))
        return track_list

musixmatch = Musixmatch('f85963e4bac8c2c33b149cab49c2b81d')
#print(musixmatch.lyrics('Reket', 'mina ka'))
#print(musixmatch.artist_top_tracks('drake', 5))


class Database:

    def __init__(self, db_name):
        self.db_name = db_name
        path = os.path.dirname(os.path.abspath(__file__))
        self.conn = sqlite3.connect(path + '/' + db_name)
        self.cur = self.conn.cursor()
        
        self.cur.execute("DROP TABLE IF EXISTS Artists")
        self.cur.execute("CREATE TABLE Artists (artist_id PRIMARY KEY, name TEXT)")

        self.cur.execute("DROP TABLE IF EXISTS Songs")
        self.cur.execute("CREATE TABLE Songs (song_id INTEGER PRIMARY KEY, title TEXT, lyrics TEXT, artist_id TEXT, genere_id)")

        '''
        self.cur.execute("DROP TABLE IF EXISTS Generes")
        self.cur.execute("CREATE TABLE Generes (genere_id INTEGER PRIMARY KEY, genere TEXT)")
        '''


        self.conn.commit()

db = Database('FinalProject.db')




# getting Spotify artist data from file to prevent API limits
artists_file = open('top_artists_file.txt', 'r').read()
artists_dict = json.loads(artists_file)

kris_top_artists = []

for artist in artists_dict['items']:
    artist_name = artist['name']
    artist_id = artist['id']
    kris_top_artists.append((artist_id, artist_name))

#print(json.dumps(artists_dict, indent = 4))


# Pushing artist and song data into db
for artist in kris_top_artists: 
    artist_id = artist[0]
    name = artist[1]
    
    try:
        db.cur.execute("SELECT name FROM Artists WHERE name = ?", name)
        print(name + 'already in database')
        pass
    
    except:
        db.cur.execute("INSERT INTO Artists (artist_id, name) VALUES (?, ?)", (artist_id, name))
        pass
    
    top_songs = musixmatch.artist_top_tracks(name, 5)
    for song in top_songs:
        song_id = song[0]
        title = song[1]
        lyrics = musixmatch.lyrics(name, title)
    
        try:
            db.cur.execute("SELECT title FROM Songs WHERE title = ?", title)
            print(title + ' already in database')
            continue
    
        except:
            
            db.cur.execute("INSERT INTO Songs (song_id, title, lyrics, artist_id) VALUES (?, ?, ?, ?)", (song_id, title, lyrics, artist_id))
            continue
    
    db.conn.commit()
    
