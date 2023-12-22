
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv

class AutoFill:
    def __init__(self):
        # Load your credentials from the .env file
        load_dotenv(dotenv_path='keys.env')
        SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
        SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')

        # Set up the Spotify client
        client_credentials_manager = SpotifyClientCredentials(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET)
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    def search_artists(self, search_string):
        """Search for artists and return the top 7 matches."""
        results = self.sp.search(q=search_string, type='artist', limit=7)
        artists = results['artists']['items']
        return [artist['name'] for artist in artists]

    def search_albums(self, search_string):
        """Search for albums and return the top 7 matches."""
        results = self.sp.search(q=search_string, type='album', limit=7)
        albums = results['albums']['items']
        return [album['name'] for album in albums]