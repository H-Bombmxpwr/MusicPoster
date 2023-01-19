import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
import datetime
import re

#pull api keys
load_dotenv(dotenv_path = 'keys.env')
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')


class Album:
    def __init__(self,artist = "steely dan",title = "aja"):
        #setup a spotfy client
        client_credentials_manager = SpotifyClientCredentials(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET)
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        #search based on the query and make an album object
        album = self.sp.search(q= 'artist:' + artist + ' ' +'album:' + title, type='album', limit=1)
        #checking if the album was found
        self.background = "white"
        self.text_color = (0,0,0)
        
        if not album['albums']['items']:
            raise ValueError('Was not able to find this album, check your spelling and try again')
        else:
            self.artist_id = album['albums']['items'][0]['artists'][0]['id']
            self.artist_name = album['albums']['items'][0]['artists'][0]['name']
            self.album_id = album['albums']['items'][0]['id']
            self.album_name = re.sub("[\(\[].*?[\)\]]", "", album['albums']['items'][0]['name'])
            print(self.album_name + " by " + self.artist_name + " was found!")


    # set the colors of the album poster
    def setColors(self,background_color,text_color):
        self.background = background_color
        self.text_color = text_color
    

    #get the track of an album object, optional parameter limit to limit the tracks returned
    def getTracks(self,limit = 50):
        track_return = self.sp.album_tracks(self.album_id, limit)['items']
        tracks = {}
        for i in range(0,len(track_return)):
            tracks[track_return[i]['id']] = re.sub("[\(\[].*?[\)\]]", "",track_return[i]['name'])
        return tracks


    def getCoverArt(self,):
        album_images = self.sp.album(self.album_id)['images']
        return album_images

    def getLabel(self):
        label = self.sp.album(self.album_id)['label']
        return label

    def getReleaseDate(self):
        date = str(self.sp.album(self.album_id)['release_date'])
        if len(date.split("-")) == 3:
            date = date.split("-")
            date = datetime.datetime(int(date[0]),int(date[1]),int(date[2]))
            date = date.strftime("%B %d, %Y")
        return date
    
    def getReleaseYear(self):
        date = str(self.sp.album(self.album_id)['release_date'])
        date = date.split("-")
        return date[0]
    
    def getNumTracks(self):
        num_tracks = int(self.sp.album(self.album_id)['total_tracks'])
        return num_tracks

    def getRuntime(self):
        track_return = self.sp.album_tracks(self.album_id)['items']
        time = 0
        for i in range(0,len(track_return)):
           time += track_return[i]['duration_ms']
       
        #calculate the seconds and add leading zero if 1 digit
        seconds=str(int((time/1000)%60))
        if len(seconds) == 1:
            seconds = "0" + str(seconds)
        
        #calculate the minutes and add any hours if they exist
        minutes=int((time/(1000*60))%60)
        hours=int((time/(1000*60*60))%24)
        if hours > 0:
            minutes = int((hours*60) + minutes)
        return str(minutes) + ":" + seconds
