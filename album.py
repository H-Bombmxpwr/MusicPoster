import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv

#pull api keys
load_dotenv(dotenv_path = 'keys.env')
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')


class Album:
    def __init__(self,artist,title):
        #setup a spotfy client
        client_credentials_manager = SpotifyClientCredentials(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET)
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        #search based on the query and make an album object
        album = self.sp.search(q= 'artist:' + artist + ' ' +'album:' + title, type='album', limit=1)
        #checking if the album was found
        if not album['albums']['items']:
            self.artist_id = None
            self.artist_name = artist
            self.album_id = None
            self.album_name = title
            self.found = False
        else:
            self.artist_id = album['albums']['items'][0]['artists'][0]['id']
            self.artist_name = album['albums']['items'][0]['artists'][0]['name']
            self.album_id = album['albums']['items'][0]['id']
            self.album_name = album['albums']['items'][0]['name']
            self.found = True
        if self.found:
            print(self.album_name + " by " + self.artist_name)
        else:
            print("NOT FOUND")


    #get the track of an album object, optional parameter limit to limit the tracks returned
    def getTracks(self,limit = 50):
        track_return = self.sp.album_tracks(self.album_id, limit)['items']
        tracks = {}
        for i in range(0,len(track_return)):
            tracks[track_return[i]['id']] = track_return[i]['name']
        return tracks


    def getCoverArt(self,):
        album_images = self.sp.album(self.album_id)['images']
        return album_images

    def getLabel(self):
        label = self.sp.album(self.album_id)['label']
        return label

    def getReleaseDate(self):
        date = self.sp.album(self.album_id)['release_date']
        return date


