import random
import requests
from src.album import Album
from src.helper import Utility
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials


class InfinityPoster:
    def __init__(self):
        # Spotify API setup
        client_credentials_manager = SpotifyClientCredentials()
        self.sp = Spotify(client_credentials_manager=client_credentials_manager)
        self.keywords_api = "https://random-word-api.herokuapp.com/word?number=1000"  # Fetch 1000 random keywords
        self.generated_album_ids = set()  # Store album IDs to prevent duplicates

    def get_keywords(self, limit=1000):
        """Fetch a long list of unique keywords."""
        try:
            response = requests.get(self.keywords_api)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching keywords from API: {e}")
        # Fallback to static keywords if API fails
        return [
            "love", "dream", "night", "world", "summer", "rock", "jazz", "pop",
            "country", "happy", "sad", "dance", "hip-hop", "rain", "fire", "soul",
            "freedom", "sun", "moon", "ocean", "party", "energy", "classic",
            "festival", "blue", "red", "green", "disco", "chill", "vibe", "spirit"
        ]

    def search_albums_by_keyword(self, keyword, limit=10):
        """Search for albums using a keyword."""
        try:
            search_results = self.sp.search(q=keyword, type="album", limit=limit)
            if search_results and "albums" in search_results and "items" in search_results["albums"]:
                return search_results["albums"]["items"]
        except Exception as e:
            print(f"Error searching albums by keyword '{keyword}': {e}")
        return []

    def find_contrasting_color(self, colors, base_color, threshold=4.5):
        """Find a color that contrasts with the base color."""
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

    def generate_posters(self, limit=5):
        """Generate posters for a set number of albums."""
        generated_posters = []

        try:
            # Fetch a fresh list of keywords
            keywords = self.get_keywords()
            random.shuffle(keywords)  # Shuffle keywords for randomness

            for keyword in keywords:
                print(f"Searching albums with keyword: {keyword}")
                albums = self.search_albums_by_keyword(keyword, limit)

                for album_data in albums:
                    # Skip duplicate albums
                    if album_data['id'] in self.generated_album_ids:
                        print(f"Skipping duplicate album: {album_data['name']}")
                        continue

                    try:
                        # Mark album as generated
                        self.generated_album_ids.add(album_data['id'])

                        artist_name = album_data['artists'][0]['name']
                        album_name = album_data['name']
                        album = Album(artist_name, album_name)

                        # Create Utility and fetch album cover
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

                        # Build and resize poster
                        poster = utility.buildPoster()
                        poster = poster.resize((740 // 5, 1200 // 5))

                        # Encode the poster in Base64
                        encoded_poster = utility.encodeImage(poster)
                        generated_posters.append(encoded_poster)

                        # Stop generating if we've reached the limit
                        if len(generated_posters) >= limit:
                            return generated_posters
                    except Exception as e:
                        print(f"Error generating poster for {album_data.get('name', 'Unknown Album')}: {e}")
        except Exception as e:
            print(f"Error generating posters: {e}")

        return generated_posters
