from src.spotify_client import get_spotify

class AutoFill:
    def __init__(self):
        # Shared Spotify client (reuses cached token instead of re-authenticating)
        self.sp = get_spotify()

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
    
    def search_mixed(self, search_string):
        """Search albums AND playlists — returns items tagged with a 'type' field."""
        try:
            results = self.sp.search(q=search_string, type='album,playlist', limit=6)
        except Exception as e:
            print(f"Mixed search error: {e}")
            return []

        out = []
        for album in (results.get('albums', {}) or {}).get('items', [])[:6]:
            if not album:
                continue
            images = album.get('images') or []
            out.append({
                'name': album['name'],
                'artist': album['artists'][0]['name'] if album.get('artists') else '',
                'image': images[-1]['url'] if images else None,
                'album_id': album['id'],
                'type': 'album',
            })
        # Spotify's search can return null playlist entries — skip them
        for pl in (results.get('playlists', {}) or {}).get('items', [])[:4]:
            if not pl:
                continue
            images = pl.get('images') or []
            owner = (pl.get('owner') or {}).get('display_name') or ''
            out.append({
                'name': pl['name'],
                'artist': f"Playlist · {owner}" if owner else 'Playlist',
                'image': images[-1]['url'] if images else None,
                'album_id': pl['id'],
                'type': 'playlist',
            })
        return out

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