from PIL import Image
import io
import requests
import numpy as np

from src.spotify_client import LRUCache

# The downloaded scannable only depends on (uri, background hex) — recoloring
# happens locally, so cache the raw PNG bytes and skip the network round-trip.
_BANNER_CACHE = LRUCache(maxsize=128)


def _fetch_banner_bytes(uri, background_color, cover_color, cover_size=1200):
    key = (uri, background_color, cover_color)
    cached = _BANNER_CACHE.get(key)
    if cached is not None:
        return cached

    uri_call = uri.replace(":", "%3A")
    url = f"https://www.spotifycodes.com/downloadCode.php?uri=png%2F{background_color[1:]}%2F{cover_color}%2F{cover_size}%2F{uri_call}"
    content = requests.get(url, timeout=10).content
    _BANNER_CACHE.set(key, content)
    return content


def return_banner(item_id, background_color, text_color, size=(300, 75),
                  transparent_bg=False, uri_type='album'):
    """
    Generate Spotify code banner at specified size.

    Args:
        item_id: Spotify album or playlist ID (or a full spotify: URI)
        background_color: Hex color for background (e.g., "#FFFFFF")
        text_color: Hex color for the code (e.g., "#000000")
        size: Tuple of (width, height) for the banner
        transparent_bg: If True, make the background transparent
        uri_type: 'album' or 'playlist'

    Returns:
        PIL Image of the banner
    """
    if str(item_id).startswith("spotify:"):
        uri = str(item_id)
    else:
        uri = f"spotify:{uri_type}:{item_id}"

    if background_color != "#000000":
        cover_color = "black"
    else:
        cover_color = "white"

    # Always fetch at high resolution (cached), then resize
    raw = _fetch_banner_bytes(uri, background_color, cover_color)
    banner = Image.open(io.BytesIO(raw)).convert("RGBA")

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

    # Make background transparent if requested
    if transparent_bg:
        bg_h = background_color.lstrip('#')
        bg_rgb = tuple(int(bg_h[i:i+2], 16) for i in (0, 2, 4))
        bg_mask = (red == bg_rgb[0]) & (green == bg_rgb[1]) & (blue == bg_rgb[2])
        data[..., 3][bg_mask.T] = 0

    banner = Image.fromarray(data)

    # Resize to requested size with high quality
    banner = banner.resize(size, Image.LANCZOS)

    return banner
