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
        results = self.sp.search(q=search_string, type='artist', limit=10)
        artists = results['artists']['items']
        return [artist['name'] for artist in artists]

    def search_albums(self, search_string, artist_name=None):
        """Search for albums and return the top 7 matches. If artist_name is provided, return albums by that artist."""
        if artist_name:
            # Search for albums by a specific artist
            query = f"artist:{artist_name} album:{search_string}"
        else:
            # General album search
            query = search_string
        results = self.sp.search(q=query, type='album', limit=10)
        albums = results['albums']['items']
        return [album['name'] for album in albums]