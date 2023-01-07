from spotifycodegen.main import SpotifyCodeGen
import spotipy
from dotenv import load_dotenv
import os
from spotipy.oauth2 import SpotifyClientCredentials
from PIL import Image, ImageDraw, ImageFont, ImageColor
from urllib.request import urlopen
import numpy as np

def return_banner(album_id,background_color,text_color):
    
    album_uri = "spotify:album:" + str(album_id)
    
    uri_call = album_uri.replace(":", "%3A")
    if background_color != "#000000":
        cover_color = "black"
    else:
        cover_color = "white"
    cover_size = 640
    url = f"https://www.spotifycodes.com/downloadCode.php?uri=png%2F{background_color[1:]}%2F{cover_color}%2F{300}%2F{uri_call}" # noqa
    banner = Image.open(urlopen(url)).convert("RGBA")# noqa:S310

    #making the spotify code itself the same color as the text
    data = np.array(banner)   # "data" is a height x width x 4 numpy array
    red, green, blue, alpha = data.T # Temporarily unpack the bands for readability
    #saving the text in rgb form
    h = text_color.lstrip('#')
    rgb_text = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    black_areas = (red == 0) & (blue == 0) & (green == 0)
    white_areas = (red == 255) & (blue == 255) & (green == 255)
    if cover_color == "black":
        data[..., :-1][black_areas.T] = rgb_text # replace black with text color
    else:
        data[..., :-1][white_areas.T] = rgb_text # replace white with text color

    banner = Image.fromarray(data)

    banner = banner.resize((300,75))

    return banner
