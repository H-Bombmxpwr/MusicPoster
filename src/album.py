import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
import re
from datetime import datetime
import random
# pull api keys
load_dotenv(dotenv_path='keys.env')
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')


class Album:
    def __init__(self, artist, title):
        # Setup a Spotify client
        client_credentials_manager = SpotifyClientCredentials(
            SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET)
        self.sp = spotipy.Spotify(
            client_credentials_manager=client_credentials_manager)
        
        if self.is_spotify_url(title):
            self.fetch_album_by_url(title)
        else:
            self.fetch_album_by_artist_and_title(artist, title)
        self.tabulated = False
        self.dotted = False

    def is_spotify_url(self, title):
        return re.match(r'https?://open\.spotify\.com/album/[A-Za-z0-9]+', title)

    def fetch_album_by_url(self, url):
        try:
            album_id = url.split('/')[-1].split('?')[0]
            album = self.sp.album(album_id)
            self.set_album_data(album)
        except spotipy.exceptions.SpotifyException as e:
            self.album_found = False
            self.message = f'Error fetching album by URL: {e}'
            print(self.message)

    def fetch_album_by_artist_and_title(self, artist, title):
        # Check if artist and title are provided
        if not artist and not title:
        # Fetch 25 new releases
            new_releases = self.sp.new_releases(limit=25)
            if new_releases['albums']['items']:
                # Choose a random album from the new releases
                album = random.choice(new_releases['albums']['items'])
                self.set_album_data(album)
            else:
                self.album_found = False
                self.message = 'No new releases found.'
                print(self.message)
        else:
            # Existing code to search for an album by artist and title
            album_search_result = self.sp.search(q=self.format_search_query(artist, title), type='album', limit=1)
            if not album_search_result['albums']['items']:
                self.album_found = False
                self.message = 'Album not found.'
                print(self.message)
            else:
                album = album_search_result['albums']['items'][0]
                self.set_album_data(album)

    def format_search_query(self,artist, title):
        query = ""
        if artist:
            query += f'artist:"{artist}"'  # Enclose in quotes for exact match
        if title:
            if query:
                query += " "  # Add space if the artist part is also there
            query += f'album:"{title}"'  # Enclose in quotes for exact match
        return query


    def set_album_data(self, album_data):
        self.album_found = True
        self.artist_id = album_data['artists'][0]['id']
        self.artist_name = album_data['artists'][0]['name']
        self.album_id = album_data['id']
        self.album_name = re.sub("[\(\[].*?[\)\]]|['\"]", "", album_data['name'])
        print(self.album_name + " by " + self.artist_name + " was found!")

    
    # set the colors of the album poster
    def setColors(self, background_color, text_color):
        self.background = background_color
        self.text_color = text_color
        
    # set tracklist name format
    def setTracklistFormat(self, tabulated, dotted):
        self.tabulated = tabulated
        self.dotted = dotted

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
