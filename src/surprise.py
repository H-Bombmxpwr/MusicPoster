import random
from src.album import Album
from src.helper import Utility
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

class SurpriseMe:
    def __init__(self):
        # Spotify API setup
        client_credentials_manager = SpotifyClientCredentials()
        self.sp = Spotify(client_credentials_manager=client_credentials_manager)
        
        # Random search terms for variety
        self.search_terms = [
            "love", "night", "summer", "dream", "heart", "fire", "dance",
            "life", "time", "world", "city", "soul", "party", "music",
            "rain", "sun", "moon", "star", "gold", "blue", "red", "black",
            "white", "happy", "sad", "crazy", "wild", "young", "forever",
            "best", "new", "old", "first", "last", "one", "two", "three",
            "baby", "girl", "boy", "man", "woman", "king", "queen"
        ]

    def get_random_album(self):
        """Get a random album using search or new releases"""
        
        # Try random search first (more variety)
        try:
            search_term = random.choice(self.search_terms)
            # Add a random year for more variety
            if random.random() > 0.5:
                year = random.randint(1990, 2024)
                search_query = f"{search_term} year:{year}"
            else:
                search_query = search_term
            
            results = self.sp.search(q=search_query, type='album', limit=20)
            
            if results and results['albums']['items']:
                selected_album = random.choice(results['albums']['items'])
                artist_name = selected_album['artists'][0]['name']
                album_name = selected_album['name']
                return artist_name, album_name
        except Exception as e:
            print(f"Error with random search: {e}")
        
        # Fallback to new releases
        return self._get_random_from_new_releases()
    
    def _get_random_from_new_releases(self):
        """Fallback method to get random album from new releases"""
        try:
            new_releases = self.sp.new_releases(limit=30)
            albums = new_releases['albums']['items']
            if albums:
                selected_album = random.choice(albums)
                artist_name = selected_album['artists'][0]['name']
                album_name = selected_album['name']
                return artist_name, album_name
        except Exception as e:
            print(f"Error fetching new releases: {e}")
        
        # Ultimate fallback - return a known popular album
        return "The Beatles", "Abbey Road"

    def generate_random_poster(self):
        """
        Generate a random poster and return image data along with metadata.
        
        Returns:
            tuple: (img_data, album_name, artist_name, background_color, text_color)
        """
        # Get a random album
        artist_name, album_name = self.get_random_album()

        # Create Album and Utility objects
        album = Album(artist_name, album_name)
        album_img = None
        img_data = None
        background_color_hex = "#FFFFFF"
        text_color_hex = "#000000"

        if album.album_found:  # Ensure the album was found
            utility = Utility(album)
            album_img = utility.fetch_album_cover(album.getCoverArt()[0]['url'])
            colors = utility.get_colors(album_img, 6)

            # Choose background and text colors
            background_color = colors[0]
            text_color = self.find_contrasting_color(colors[1:], background_color)

            # Convert to hex strings
            background_color_hex = f"#{background_color[0]:02x}{background_color[1]:02x}{background_color[2]:02x}"
            text_color_hex = f"#{text_color[0]:02x}{text_color[1]:02x}{text_color[2]:02x}"

            # Set album colors
            album.setColors(background_color_hex, text_color_hex)

            # Build poster
            poster = utility.buildPoster()
            img_data = utility.encodeImage(poster)

        # Return all needed data including the actual colors used
        return img_data, album_name, artist_name, background_color_hex, text_color_hex

    def find_contrasting_color(self, colors, base_color, threshold=4.5):
        """Find a color that contrasts well with the base color"""
        def contrast_ratio(color1, color2):
            def luminance(color):
                r, g, b = [c / 255.0 for c in color]
                r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
                g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
                b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
                return 0.2126 * r + 0.7152 * g + 0.0722 * b

            lum1 = luminance(color1) + 0.05
            lum2 = luminance(color2) + 0.05
            return max(lum1, lum2) / min(lum1, lum2)

        for color in colors:
            if contrast_ratio(base_color, color) >= threshold:
                return color
        
        # If no high-contrast color found, try lower threshold
        for color in colors:
            if contrast_ratio(base_color, color) >= 2.5:
                return color
        
        # Fallback: return black or white based on background luminance
        def luminance(color):
            r, g, b = [c / 255.0 for c in color]
            r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
            g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
            b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        if luminance(base_color) > 0.5:
            return (0, 0, 0)  # Dark text on light background
        else:
            return (255, 255, 255)  # Light text on dark background