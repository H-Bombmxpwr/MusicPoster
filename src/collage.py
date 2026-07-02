"""Top-albums collage poster: a grid of the listener's top album covers."""
from PIL import Image, ImageDraw
from io import BytesIO
from datetime import datetime
import math
import requests

from src.helper import load_font, OSWALD_PATH, _COVER_CACHE

BG_COLOR = (10, 10, 15)        # site dark theme
ACCENT = (255, 107, 53)        # site orange accent
TEXT = (244, 244, 244)
MUTED = (150, 150, 160)


def _fetch_cover(url):
    cached = _COVER_CACHE.get(url)
    if cached is None:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        cached = resp.content
        _COVER_CACHE.set(url, cached)
    return Image.open(BytesIO(cached)).convert('RGB')


def _truncate(draw, text, font, max_w):
    if draw.textlength(text, font=font) <= max_w:
        return text
    while len(text) > 1 and draw.textlength(text + "...", font=font) > max_w:
        text = text[:-1].rstrip()
    return text + "..."


def build_collage(albums, display_name, width=1110, height=1800):
    """Build the collage poster.

    albums: list of dicts with 'name', 'artist', 'image' (cover URL).
    display_name: Spotify display name used in the title.
    """
    albums = [a for a in albums if a.get('image')][:8]
    poster = Image.new('RGB', (width, height), BG_COLOR)
    draw = ImageDraw.Draw(poster)

    margin = 60
    s = width / 1110  # scale relative to design size

    # ── Title block ──
    title_font = load_font(OSWALD_PATH, int(72 * s))
    sub_font = load_font(OSWALD_PATH, int(30 * s))
    name = (display_name or 'YOUR').upper()
    title = f"{name}'S TOP ALBUMS"
    title = _truncate(draw, title, title_font, width - 2 * margin)
    draw.text((margin, int(50 * s)), title, font=title_font, fill=TEXT)
    subtitle = f"LAST 6 MONTHS  ·  {datetime.now().strftime('%B %Y').upper()}"
    draw.text((margin, int(140 * s)), subtitle, font=sub_font, fill=ACCENT)

    # ── Cover grid ──
    grid_top = int(220 * s)
    footer_h = int(110 * s)
    grid_h = height - grid_top - footer_h
    gap = int(30 * s)
    text_h = int(58 * s)  # name + artist under each cover

    cols = 2
    rows = max(math.ceil(len(albums) / cols), 1)
    cell_w = (width - 2 * margin - gap * (cols - 1)) // cols
    cell_h = (grid_h - gap * (rows - 1)) // rows
    cover_size = max(min(cell_w, cell_h - text_h), 50)

    name_font = load_font(OSWALD_PATH, int(26 * s))
    artist_font = load_font(OSWALD_PATH, int(22 * s))
    rank_font = load_font(OSWALD_PATH, int(26 * s))

    for i, album in enumerate(albums):
        col = i % cols
        row = i // cols
        cx = margin + col * (cell_w + gap) + (cell_w - cover_size) // 2
        cy = grid_top + row * (cell_h + gap)

        try:
            cover = _fetch_cover(album['image']).resize(
                (cover_size, cover_size), Image.LANCZOS)
            poster.paste(cover, (cx, cy))
        except Exception as e:
            print(f"Collage cover error: {e}")
            draw.rectangle([(cx, cy), (cx + cover_size, cy + cover_size)],
                           fill=(30, 30, 38))

        # Rank number + album/artist under the cover
        ty = cy + cover_size + int(8 * s)
        rank = f"{i + 1:02d}"
        draw.text((cx, ty), rank, font=rank_font, fill=ACCENT)
        rank_w = draw.textlength(rank + "  ", font=rank_font)
        max_text_w = cover_size - rank_w
        album_name = _truncate(draw, (album.get('name') or '').upper(), name_font, max_text_w)
        draw.text((cx + rank_w, ty), album_name, font=name_font, fill=TEXT)
        artist = _truncate(draw, album.get('artist') or '', artist_font, max_text_w)
        draw.text((cx + rank_w, ty + int(30 * s)), artist, font=artist_font, fill=MUTED)

    # ── Footer ──
    line_y = height - footer_h + int(20 * s)
    draw.line([(margin, line_y), (width - margin, line_y)], fill=ACCENT, width=max(int(3 * s), 1))
    foot_font = load_font(OSWALD_PATH, int(24 * s))
    draw.text((margin, line_y + int(15 * s)),
              "POWERED BY SPOTIFY", font=foot_font, fill=MUTED)
    right_text = datetime.now().strftime("%m.%d.%Y")
    rw = draw.textlength(right_text, font=foot_font)
    draw.text((width - margin - rw, line_y + int(15 * s)),
              right_text, font=foot_font, fill=MUTED)

    return poster
