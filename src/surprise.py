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

    def get_random_album(self):
        # Fetch 30 new releases
        new_releases = self.sp.new_releases(limit=30)
        albums = new_releases['albums']['items']

        # Randomly select an album
        selected_album = random.choice(albums)
        artist_name = selected_album['artists'][0]['name']
        album_name = selected_album['name']
        return artist_name, album_name

    def generate_random_poster(self):
        # Get a random album
        artist_name, album_name = self.get_random_album()

        # Create Album and Utility objects
        album = Album(artist_name, album_name)
        album_img = None
        img_data = None

        if album.album_found:  # Ensure the album was found
            utility = Utility(album)
            album_img = utility.fetch_album_cover(album.getCoverArt()[0]['url'])
            colors = utility.get_colors(album_img, 6)

            # Choose background and text colors
            background_color = colors[0]
            text_color = self.find_contrasting_color(colors[1:], background_color)

            # Set album colors
            album.setColors(
                f"#{background_color[0]:02x}{background_color[1]:02x}{background_color[2]:02x}",
                f"#{text_color[0]:02x}{text_color[1]:02x}{text_color[2]:02x}",
            )

            # Build poster
            poster = utility.buildPoster()
            img_data = utility.encodeImage(poster)

        return img_data, album_name, artist_name

    def find_contrasting_color(self, colors, base_color, threshold=4.5):
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
        return colors[0]
