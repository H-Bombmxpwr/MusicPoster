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
        """Search for artists and return the top 10 matches with images."""
        results = self.sp.search(q=search_string, type='artist', limit=10)
        artists = results['artists']['items']
        
        # Return list of dicts with name and image
        artist_data = []
        for artist in artists:
            # Get the smallest image (usually 64x64) for efficiency, or None if no images
            image_url = None
            if artist.get('images') and len(artist['images']) > 0:
                # Images are sorted by size descending, so last one is smallest
                image_url = artist['images'][-1]['url']
            
            artist_data.append({
                'name': artist['name'],
                'image': image_url
            })
        
        return artist_data

    def search_albums(self, search_string, artist_name=None):
        """Search for albums and return the top 10 matches with images."""
        if artist_name:
            # Search for albums by a specific artist (quote values to handle special chars like slashes)
            query = f'artist:"{artist_name}" album:"{search_string}"'
        else:
            # General album search
            query = search_string

        results = self.sp.search(q=query, type='album', limit=10)
        albums = results['albums']['items']

        # Return list of dicts with name, artist, image, and album_id
        album_data = []
        for album in albums:
            # Get the smallest image for efficiency
            image_url = None
            if album.get('images') and len(album['images']) > 0:
                image_url = album['images'][-1]['url']

            # Get artist name for display
            artist = album['artists'][0]['name'] if album.get('artists') else ''

            album_data.append({
                'name': album['name'],
                'artist': artist,
                'image': image_url,
                'album_id': album['id']
            })

        return album_data
    
    # Keep backward compatible methods that return just names
    def search_artists_simple(self, search_string):
        """Search for artists and return just names (backward compatible)."""
        results = self.sp.search(q=search_string, type='artist', limit=10)
        artists = results['artists']['items']
        return [artist['name'] for artist in artists]

    def search_albums_simple(self, search_string, artist_name=None):
        """Search for albums and return just names (backward compatible)."""
        if artist_name:
            query = f'artist:"{artist_name}" album:"{search_string}"'
        else:
            query = search_string
        results = self.sp.search(q=query, type='album', limit=10)
        albums = results['albums']['items']
        return [album['name'] for album in albums]