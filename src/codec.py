from PIL import Image
from urllib.request import urlopen
import numpy as np

def return_banner(album_id, background_color, text_color, size=(300, 75)):
    """
    Generate Spotify code banner at specified size.
    
    Args:
        album_id: Spotify album ID
        background_color: Hex color for background (e.g., "#FFFFFF")
        text_color: Hex color for the code (e.g., "#000000")
        size: Tuple of (width, height) for the banner
    
    Returns:
        PIL Image of the banner
    """
    album_uri = "spotify:album:" + str(album_id)
    
    uri_call = album_uri.replace(":", "%3A")
    if background_color != "#000000":
        cover_color = "black"
    else:
        cover_color = "white"
    
    # Always fetch at high resolution, then resize
    cover_size = 1200
    url = f"https://www.spotifycodes.com/downloadCode.php?uri=png%2F{background_color[1:]}%2F{cover_color}%2F{cover_size}%2F{uri_call}"
    banner = Image.open(urlopen(url)).convert("RGBA")  # noqa:S310

    # Making the spotify code itself the same color as the text
    data = np.array(banner)
    red, green, blue, alpha = data.T
    
    # Convert hex text color to RGB
    h = text_color.lstrip('#')
    rgb_text = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    black_areas = (red == 0) & (blue == 0) & (green == 0)
    white_areas = (red == 255) & (blue == 255) & (green == 255)
    
    if cover_color == "black":
        data[..., :-1][black_areas.T] = rgb_text
    else:
        data[..., :-1][white_areas.T] = rgb_text

    banner = Image.fromarray(data)
    
    # Resize to requested size with high quality
    banner = banner.resize(size, Image.LANCZOS)

    return banner