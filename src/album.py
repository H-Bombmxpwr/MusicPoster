import spotipy
import re
from datetime import datetime
import random

from src.spotify_client import get_spotify, LRUCache

# Cache of fully-hydrated album/playlist data keyed by ('album'|'playlist', id).
# Skips the sp.album() + sp.album_tracks() round-trips on every poster edit.
_ITEM_CACHE = LRUCache(maxsize=256)


class Album:
    def __init__(self, artist, title, album_id=None, item_type='album'):
        self.sp = get_spotify()

        # Safe defaults so a network error can never leave these unset
        self.album_found = False
        self.message = ''
        self.spotify_type = 'album'  # 'album' or 'playlist'

        try:
            if album_id:
                # Use the id directly to avoid re-searching and getting a different version.
                # item_type tells us whether the id belongs to an album or a playlist.
                if item_type == 'playlist':
                    self.fetch_playlist_by_id(album_id)
                else:
                    self.fetch_album_by_id(album_id)
            elif self.is_spotify_playlist_url(title):
                self.fetch_playlist_by_url(title)
            elif self.is_spotify_url(title):
                self.fetch_album_by_url(title)
            else:
                self.fetch_album_by_artist_and_title(artist, title)
        except Exception as e:
            self.album_found = False
            self.message = f'Error fetching album: {e}'
            print(self.message)

        self.text_color = "#000000"  # Default text color (black)
        self.background = "#FFFFFF"  # Default background color (white)
        self.tabulated = True
        self.dotted = False

    def fetch_album_by_id(self, album_id):
        """Fetch album directly by Spotify album ID (avoids re-search ambiguity)"""
        cached = _ITEM_CACHE.get(('album', album_id))
        if cached:
            self._apply_cached(cached)
            return
        try:
            album = self.sp.album(album_id)
            self.set_album_data(album)
        except spotipy.exceptions.SpotifyException as e:
            self.album_found = False
            self.message = f'Error fetching album by ID: {e}'
            print(self.message)

    def is_spotify_url(self, title):
        return re.match(r'https?://open\.spotify\.com/album/[A-Za-z0-9]+', title or '')

    def is_spotify_playlist_url(self, title):
        return re.match(r'https?://open\.spotify\.com/playlist/[A-Za-z0-9]+', title or '')

    def fetch_album_by_url(self, url):
        try:
            album_id = url.split('/')[-1].split('?')[0]
            self.fetch_album_by_id(album_id)
        except spotipy.exceptions.SpotifyException as e:
            self.album_found = False
            self.message = f'Error fetching album by URL: {e}'
            print(self.message)

    def fetch_playlist_by_url(self, url):
        playlist_id = url.split('/')[-1].split('?')[0]
        self.fetch_playlist_by_id(playlist_id)

    def fetch_playlist_by_id(self, playlist_id):
        """Fetch a playlist and expose it through the same interface as an album"""
        cached = _ITEM_CACHE.get(('playlist', playlist_id))
        if cached:
            self._apply_cached(cached)
            return
        try:
            playlist = self.sp.playlist(playlist_id)
        except spotipy.exceptions.SpotifyException as e:
            self.album_found = False
            self.message = f'Error fetching playlist: {e}'
            print(self.message)
            return

        self.album_found = True
        self.spotify_type = 'playlist'
        owner = playlist.get('owner', {}).get('display_name') or 'Spotify'
        self.artist_id = playlist.get('owner', {}).get('id', '')
        self.artist_name = owner
        self.album_id = playlist['id']
        self.album_name = playlist.get('name', 'Playlist').strip()

        self._cached_images = playlist.get('images', [])
        self._cached_label = f"A playlist by {owner}"
        self._cached_release_date = ''
        tracks = []
        for item in playlist.get('tracks', {}).get('items', [])[:50]:
            track = item.get('track') or {}
            if track.get('name'):
                tracks.append({
                    'id': track.get('id'),
                    'name': track['name'],
                    'duration_ms': track.get('duration_ms', 0),
                })
        self._cached_tracks = tracks
        self._cached_total_tracks = playlist.get('tracks', {}).get('total', len(tracks))
        print(f"{self.album_name} (playlist by {owner}) was found!")
        self._store_in_cache()

    def fetch_album_by_artist_and_title(self, artist, title):
        # Check if artist and title are provided
        if not artist and not title:
        # Fetch 25 new releases
            new_releases = self.sp.new_releases(limit=25)
            if new_releases['albums']['items']:
                # Choose a random album from the new releases
                album = random.choice(new_releases['albums']['items'])
                self.fetch_album_by_id(album['id'])
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
                # Search results lack label/tracks detail — go through the cached ID path
                self.fetch_album_by_id(album['id'])

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
        self.spotify_type = 'album'
        self.artist_id = album_data['artists'][0]['id']
        self.artist_name = album_data['artists'][0]['name']
        self.album_id = album_data['id']
        album_name = re.sub("[\(\[].*?[\)\]]|['\"]", "", album_data['name'])
        # Remove "- Remastered", "- Deluxe Edition", etc. from album name
        album_name = re.sub(r'\s*[-–—]\s*remaster(ed)?\s*\d*\s*$', '', album_name, flags=re.IGNORECASE)
        album_name = re.sub(r'\s*[-–—]\s*\d+\s*remaster(ed)?\s*$', '', album_name, flags=re.IGNORECASE)
        album_name = re.sub(r'\s*[-–—]\s*(mono|stereo|deluxe|bonus|extended|anniversary|edition).*$', '', album_name, flags=re.IGNORECASE)
        self.album_name = album_name.strip()
        print(self.album_name + " by " + self.artist_name + " was found!")

        # Cache all album data so we never re-fetch from the API
        self._cached_images = album_data.get('images', [])
        self._cached_label = album_data.get('label', '')
        self._cached_release_date = album_data.get('release_date', '')
        self._cached_total_tracks = album_data.get('total_tracks', 0)

        # Cache tracks (fetch once, preserve order)
        try:
            track_items = self.sp.album_tracks(self.album_id, limit=50)['items']
        except Exception:
            track_items = []
        self._cached_tracks = []
        for item in track_items:
            self._cached_tracks.append({
                'id': item['id'],
                'name': item['name'],
                'duration_ms': item['duration_ms']
            })
        self._store_in_cache()

    def _store_in_cache(self):
        _ITEM_CACHE.set((self.spotify_type, self.album_id), {
            'spotify_type': self.spotify_type,
            'artist_id': getattr(self, 'artist_id', ''),
            'artist_name': self.artist_name,
            'album_id': self.album_id,
            'album_name': self.album_name,
            'images': self._cached_images,
            'label': self._cached_label,
            'release_date': self._cached_release_date,
            'total_tracks': self._cached_total_tracks,
            'tracks': self._cached_tracks,
        })

    def _apply_cached(self, data):
        self.album_found = True
        self.spotify_type = data['spotify_type']
        self.artist_id = data['artist_id']
        self.artist_name = data['artist_name']
        self.album_id = data['album_id']
        self.album_name = data['album_name']
        self._cached_images = data['images']
        self._cached_label = data['label']
        self._cached_release_date = data['release_date']
        self._cached_total_tracks = data['total_tracks']
        self._cached_tracks = data['tracks']

    def getSpotifyUri(self):
        """URI used for the scannable Spotify code"""
        return f"spotify:{self.spotify_type}:{self.album_id}"

    # set the colors of the album poster
    def setColors(self, background_color, text_color):
        self.background = background_color
        self.text_color = text_color

    # set tracklist name format
    def setTracklistFormat(self, tabulated, dotted):
        self.tabulated = tabulated
        self.dotted = dotted

    # get the tracks of an album object using cached data (preserves order)
    # Returns a list of track names in disc/track order
    def getTracks(self, limit=50):
        return [re.sub("[\(\[].*?[\)\]]", "", item['name']) for item in self._cached_tracks[:limit]]

    def getCoverArt(self):
        # If a custom cover URL is set (and not empty), return it in the same format as Spotify
        if hasattr(self, 'custom_cover_url') and self.custom_cover_url and len(self.custom_cover_url.strip()) > 0:
            return [{'url': self.custom_cover_url, 'height': 640, 'width': 640}]
        return self._cached_images

    def getSpotifyCoverUrl(self):
        """Get the original Spotify cover URL (ignoring any custom cover)"""
        if self._cached_images:
            return self._cached_images[0]['url']
        return None

    def setCustomCover(self, url):
        """Set a custom cover art URL (e.g., from covers.musichoarders.xyz)"""
        if url and len(url.strip()) > 0:
            self.custom_cover_url = url.strip()
        else:
            self.custom_cover_url = None

    def getMusicHoardersUrl(self):
        """Generate the covers.musichoarders.xyz search URL for this album"""
        import urllib.parse
        base_url = "https://covers.musichoarders.xyz/"
        params = {
            'artist': self.artist_name,
            'album': self.album_name
        }
        return base_url + "?" + urllib.parse.urlencode(params)

    def getLabel(self):
        return self._cached_label

    def getReleaseDate(self):
        date = str(self._cached_release_date)
        if len(date.split("-")) == 3:
            date = date.split("-")
            date = datetime(int(date[0]), int(date[1]), int(date[2]))
            date = date.strftime("%B %d, %Y")
        return date

    def getReleaseYear(self):
        date = str(self._cached_release_date)
        date = date.split("-")
        return date[0]

    def getNumTracks(self):
        return int(self._cached_total_tracks)

    def getRuntime(self):
        time = 0
        for item in self._cached_tracks:
            time += item['duration_ms']

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
