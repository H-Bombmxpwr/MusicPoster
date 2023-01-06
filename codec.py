from spotifycodegen.main import SpotifyCodeGen
from dotenv import load_dotenv
import os
from spotipy.oauth2 import SpotifyClientCredentials
from PIL import Image, ImageDraw, ImageFont, ImageColor

def return_banner(album_id):

    load_dotenv(dotenv_path = 'keys.env')
    SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
    SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
    client_credentials_manager = SpotifyClientCredentials(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET)

    
    spot = SpotifyCodeGen()
    
    album_uri = "spotify:album:" + str(album_id)

    img = spot.gen_codes_uris([album_uri])

    image_file_name = "spotify-album-" + str(album_id) + ".png"
    album_img = Image.open(image_file_name).convert("RGBA")
    os.remove(image_file_name) #remove the generated image

    banner = album_img.crop((0,640,640,800))

    banner = banner.resize((250,75))

    return banner
