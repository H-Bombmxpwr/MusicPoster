import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
import re
from datetime import datetime
# pull api keys
load_dotenv(dotenv_path='keys.env')
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')


class Album:
    def __init__(self, artist, title, url=None):
        # Setup a Spotify client
        client_credentials_manager = SpotifyClientCredentials(
            SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET)
        self.sp = spotipy.Spotify(
            client_credentials_manager=client_credentials_manager)

        # Check if URI is provided
        if url:
            self.fetch_album_by_url(url)
        else:
            self.fetch_album_by_artist_and_title(artist, title)

    def fetch_album_by_url(self, url):
        try:
            # Extract album ID from the URL
            album_id = url.split('/')[-1].split('?')[0]
            print(album_id)
            album = self.sp.album(album_id)
            self.set_album_data(album)
        except spotipy.exceptions.SpotifyException as e:
            self.album_found = False
            self.message = f'Error fetching album by URL: {e}'
            print(self.message)

    def fetch_album_by_artist_and_title(self, artist, title):
        # Set a default if the user does not enter anything
        month = datetime.now().month
        # Determine the season based on the month
        if month in [12, 1, 2]:
            season = 'winter'
        elif month in [3, 4, 5]:
            season = 'spring'
        elif month in [6, 7, 8]:
            season = 'summer'
        else:
            season = 'autumn'
        # Set a default artist and album if the user does not enter anything,
        # based on the season
        if artist == "" and title == "":
            if season == 'winter':
                artist = "michael buble"
                title = "christmas"
            elif season == 'spring':
                artist = "fitz and the tantrums"
                title = "more than just a dream"
            elif season == 'summer':
                artist = "jimmy buffet"
                title = "songs you know by heart"
            else:
                artist = "steely dan"
                title = "aja"

        album_search_result = self.sp.search(q='artist:' + artist + ' ' + 'album:' + title, type='album', limit=1)
        if not album_search_result['albums']['items']:
            self.album_found = False
            self.message = 'Album not found. Literal skill issue'
            print(self.message)
        else:
            album = album_search_result['albums']['items'][0]
            self.set_album_data(album)

    def set_album_data(self, album_data):
        self.album_found = True
        self.artist_id = album_data['artists'][0]['id']
        self.artist_name = album_data['artists'][0]['name']
        self.album_id = album_data['id']
        self.album_name = re.sub("[\(\[].*?[\)\]]", "", album_data['name'])
        print(self.album_name + " by " + self.artist_name + " was found!")

    
    # set the colors of the album poster
    def setColors(self, background_color, text_color):
        self.background = background_color
        self.text_color = text_color

    # get the track of an album object, optional parameter limit to limit the tracks returned
    def getTracks(self, limit=30):
        track_return = self.sp.album_tracks(self.album_id, limit)['items']
        tracks = {}
        for i in range(0, len(track_return)):
            tracks[track_return[i]['id']] = re.sub(
                "[\(\[].*?[\)\]]", "", track_return[i]['name'])
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
            date = datetime(int(date[0]), int(date[1]), int(date[2]))
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
        for i in range(0, len(track_return)):
            time += track_return[i]['duration_ms']

        # calculate the seconds and add leading zero if 1 digit
        seconds = str(int((time/1000) % 60))
        if len(seconds) == 1:
            seconds = "0" + str(seconds)

        # calculate the minutes and add any hours if they exist
        minutes = int((time/(1000*60)) % 60)
        hours = int((time/(1000*60*60)) % 24)
        if hours > 0:
            minutes = int((hours*60) + minutes)
        return str(minutes) + ":" + seconds
