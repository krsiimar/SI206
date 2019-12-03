import spotipy 
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import requests
import json
import os
import sqlite3


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

        
    def top_tracks_data(self, limit, offset, time_range):
        tracks_data_list = []
        top_tracks = self.sp.current_user_top_tracks(limit, offset, time_range)
        for track in top_tracks['items']:
           track_name = track['name']
           track_id = track['id']
           artist = track['artists'][0]['name']
           artist_id = track['artists'][0]['id']
           liveness = self.sp.audio_features(track_id)[0]['liveness']

           tracks_data_list.append((track_id, track_name, liveness, artist, artist_id))
        return tracks_data_list

spotify = Spotify("kristofersiimar", 'user-top-read', "c718242a780d4369866e47defc06d637", "93ca05c182d3470bbcd143090e6688a1", 'https://example.com/callback/')

kris_top_tracks_data = spotify.top_tracks_data(100, 0, 'long_term')


class Database:

    def __init__(self, db_name):
        self.db_name = db_name
        path = os.path.dirname(os.path.abspath(__file__))
        self.conn = sqlite3.connect(path + '/' + db_name)
        self.cur = self.conn.cursor()
        
        self.cur.execute("DROP TABLE IF EXISTS Top_Songs")
        self.cur.execute("CREATE TABLE Top_Songs (track_id PRIMARY KEY, title TEXT, liveness INTEGER, artist TEXT, artist_id TEXT)")

        self.conn.commit()

db = Database('FinalProject.db')
print(db)


db_tracks_list = []

for track in kris_top_tracks_data: 
    track_id = track[0]
    title = track[1]
    liveness = track[2]
    artist = track[3]
    artist_id = track[4]

    if title not in db_tracks_list:
        db.cur.execute("INSERT INTO Top_Songs (track_id, title, liveness, artist, artist_id) VALUES (?, ?, ?, ?, ?)", (track_id, title, liveness, artist, artist_id))
        db_tracks_list.append(title)
    
    db.conn.commit()
    





