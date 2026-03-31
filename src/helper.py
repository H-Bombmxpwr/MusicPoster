from src.album import Album
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import textwrap
from src.codec import return_banner

import numpy as np

import base64
import io
import re


import unicodedata
from PIL import ImageFont

def contains_cjk(text: str) -> bool:
    for ch in text:
        code = ord(ch)
        # CJK Unified Ideographs + Extension A + Compatibility + Hiragana/Katakana
        if (0x4E00 <= code <= 0x9FFF) or (0x3400 <= code <= 0x4DBF) or (0xF900 <= code <= 0xFAFF) \
           or (0x3040 <= code <= 0x30FF):
            return True
    return False

def contains_hangul(text: str) -> bool:
    for ch in text:
        code = ord(ch)
        # Hangul Syllables + Jamo
        if (0xAC00 <= code <= 0xD7AF) or (0x1100 <= code <= 0x11FF) or (0x3130 <= code <= 0x318F):
            return True
    return False

def contains_cyrillic(text: str) -> bool:
    for ch in text:
        code = ord(ch)
        if (0x0400 <= code <= 0x04FF) or (0x0500 <= code <= 0x052F) or (0x2DE0 <= code <= 0x2DFF) \
           or (0xA640 <= code <= 0xA69F):
            return True
    return False

from functools import lru_cache

OSWALD_PATH = "static/Oswald-Medium.ttf"
NOTO_BASE   = "static/fonts/NotoSans-Regular.ttf"
NOTO_KR     = "static/fonts/NotoSansKR-Regular.ttf"
NOTO_JP     = "static/fonts/NotoSansJP-Regular.ttf"
NOTO_SC     = "static/fonts/NotoSansSC-Regular.ttf"

def is_non_latin_glyph(ch: str) -> bool:
    code = ord(ch)

    if (0xAC00 <= code <= 0xD7AF) or (0x1100 <= code <= 0x11FF) or (0x3130 <= code <= 0x318F):
        return True
    if 0x3040 <= code <= 0x30FF:
        return True
    if (0x4E00 <= code <= 0x9FFF) or (0x3400 <= code <= 0x4DBF) or (0xF900 <= code <= 0xFAFF):
        return True
    if (0x0400 <= code <= 0x04FF) or (0x0500 <= code <= 0x052F):
        return True

    return False

@lru_cache(maxsize=256)
def load_font(path: str, size: int):
    return ImageFont.truetype(path, size)

def text_width(draw, txt: str, font) -> int:
    l, t, r, b = draw.textbbox((0, 0), txt, font=font)
    return r - l

def pick_alt_font_for_char(ch: str, size: int):
    code = ord(ch)
    if (0xAC00 <= code <= 0xD7AF) or (0x1100 <= code <= 0x11FF) or (0x3130 <= code <= 0x318F):
        return load_font(NOTO_KR, size)
    if 0x3040 <= code <= 0x30FF:
        return load_font(NOTO_JP, size)
    if (0x4E00 <= code <= 0x9FFF) or (0x3400 <= code <= 0x4DBF) or (0xF900 <= code <= 0xFAFF):
        return load_font(NOTO_SC, size)
    if (0x0400 <= code <= 0x04FF) or (0x0500 <= code <= 0x052F):
        return load_font(NOTO_BASE, size)
    return load_font(NOTO_BASE, size)

def mixed_text_width(draw, text: str, latin_font, size: int) -> int:
    if not text:
        return 0

    total = 0
    run = ""
    run_is_alt = None

    for ch in text:
        ch_is_alt = is_non_latin_glyph(ch)
        if run == "" or ch_is_alt == run_is_alt:
            run += ch
            run_is_alt = ch_is_alt
        else:
            font = pick_alt_font_for_char(run[0], size) if run_is_alt else latin_font
            total += text_width(draw, run, font)
            run = ch
            run_is_alt = ch_is_alt

    if run:
        font = pick_alt_font_for_char(run[0], size) if run_is_alt else latin_font
        total += text_width(draw, run, font)

    return total

def draw_mixed_text(draw, xy, text: str, latin_font, size: int, fill, fake_bold_px: int = 0):
    x0, y0 = xy

    def draw_pass(dx: int):
        x = x0
        run = ""
        run_is_alt = None

        def flush_run():
            nonlocal x, run, run_is_alt
            if not run:
                return
            font = pick_alt_font_for_char(run[0], size) if run_is_alt else latin_font
            draw.text((x + dx, y0), run, font=font, fill=fill)
            x += text_width(draw, run, font)
            run = ""

        for ch in text:
            ch_is_alt = is_non_latin_glyph(ch)
            if run == "" or ch_is_alt == run_is_alt:
                run += ch
                run_is_alt = ch_is_alt
            else:
                flush_run()
                run = ch
                run_is_alt = ch_is_alt

        flush_run()

    draw_pass(0)
    if fake_bold_px and fake_bold_px > 0:
        draw_pass(fake_bold_px)


# Resolution presets - all maintain 740:1200 aspect ratio (0.617)
# Base dimensions are used for proportional calculations
RESOLUTION_PRESETS = {
    'low': {'width': 370, 'height': 600, 'scale': 0.5},
    'medium': {'width': 740, 'height': 1200, 'scale': 1.0},
    'high': {'width': 1480, 'height': 2400, 'scale': 2.0},
    'ultra': {'width': 2220, 'height': 3600, 'scale': 3.0},
}

# Base dimensions (medium/original)
BASE_WIDTH = 740
BASE_HEIGHT = 1200

# Available poster styles
POSTER_STYLES = ['classic', 'standard', 'frame', 'basic', 'fullcover']


class Utility:
    def __init__(self, album, resolution='medium', style='classic'):
        self.album = album
        self.resolution = resolution
        self.style = style if style in POSTER_STYLES else 'classic'
        self.custom_tracks = {}
        self.custom_date = None
        self.custom_label = None

        # Get scale factor from preset
        preset = RESOLUTION_PRESETS.get(resolution, RESOLUTION_PRESETS['medium'])
        self.scale = preset['scale']
        self.width = preset['width']
        self.height = preset['height']
        
        # All base values (at scale 1.0 / medium resolution)
        # These will be multiplied by scale factor when used
        self._base_below_pic_h = 710
        self._base_margin = 50
        self._base_artist_font_size = 30
        self._base_album_font_size = 40
        self._base_date_font_size = 30
        self._base_runtime_font_size = 30
        self._base_label_font_size = 30
        self._base_color_square_size = 30
        self._base_color_square_spacing = 30
        self._base_banner_width = 300
        self._base_banner_height = 75
        self._base_track_font_max = 30
        self._base_track_font_min = 10
        self._base_line_spacing = 5
        
        # Scaled values (computed properties)
        self.below_pic_h = self._scale(self._base_below_pic_h)
        self.margin = self._scale(self._base_margin)
        
        self.text_color = self.album.text_color
        self.background = self.album.background
        self.full_page_track_count = 12
        self.tabulated = self.album.tabulated
        self.dotted = self.album.dotted
        
        # For SVG generation - store drawing commands
        self.svg_elements = []
        
    def _scale(self, value):
        """Scale a base value according to resolution"""
        return int(value * self.scale)
    
    def _scale_font(self, base_size):
        """Scale font size - returns integer"""
        return max(int(base_size * self.scale), 8)  # Minimum 8px font

    # ─── Shared helpers for all styles ───

    def _hex_to_rgba(self, hex_color):
        """Convert hex color string to RGBA tuple"""
        h = hex_color.lstrip('#')
        if len(h) >= 6:
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (255,)
        return (255, 255, 255, 255)

    def _create_vertical_gradient(self, width, height, start_alpha=0, end_alpha=255):
        """Create a vertical gradient mask (top=start_alpha, bottom=end_alpha)"""
        gradient = np.linspace(start_alpha, end_alpha, height, dtype=np.uint8)
        gradient = np.tile(gradient.reshape(-1, 1), (1, width))
        return Image.fromarray(gradient, mode='L')

    def _get_album_name(self):
        if hasattr(self, 'custom_album') and self.custom_album is not None:
            return self.custom_album
        return self.album.album_name

    def _get_artist_name(self):
        if hasattr(self, 'custom_artist') and self.custom_artist is not None:
            return self.custom_artist
        return self.album.artist_name

    def _get_date_string(self):
        if hasattr(self, 'custom_date') and self.custom_date is not None:
            return self.custom_date
        return self.album.getReleaseDate()

    def _get_label_string(self):
        if hasattr(self, 'custom_label') and self.custom_label is not None:
            return self.custom_label
        return "Released by " + self.album.getLabel().split(',')[0]

    def _fit_text_to_width(self, text, font_path, max_size, max_width):
        """Return a font sized so text fits within max_width"""
        size = max_size
        min_size = self._scale_font(12)
        while size > min_size:
            font = load_font(font_path, size)
            bbox = font.getbbox(text)
            if (bbox[2] - bbox[0]) <= max_width:
                return font
            size -= 1
        return load_font(font_path, min_size)

    def _clean_track_name(self, value):
        """Clean up track name — remove remastered, feat., etc."""
        value = re.sub(r'\s*[-–—]\s*remaster(ed)?\s*\d*\s*', '', value, flags=re.IGNORECASE)
        value = re.sub(r'\s*[-–—]\s*\d+\s*remaster(ed)?\s*', '', value, flags=re.IGNORECASE)
        value = re.sub(r'\(.*?remaster(ed)?.*?\)', '', value, flags=re.IGNORECASE)
        value = re.sub(r'\[.*?remaster(ed)?.*?\]', '', value, flags=re.IGNORECASE)
        value = re.sub(r'\s*[-–—]\s*(mono|stereo|deluxe|bonus|extended|anniversary|edition).*$', '', value, flags=re.IGNORECASE)
        value = re.sub(r'\(.*?(mono|stereo|deluxe|bonus|extended|anniversary|edition).*?\)', '', value, flags=re.IGNORECASE)
        value = re.split(r'\s+feat\.', value, flags=re.IGNORECASE)[0]
        value = re.split(r'\s+featuring\s+', value, flags=re.IGNORECASE)[0]
        value = re.split(r'\s+ft\.', value, flags=re.IGNORECASE)[0]
        value = re.sub(r'\(.*?\)', '', value)
        value = re.sub(r'\[.*?\]', '', value)
        value = re.sub(r'\s*[-–—]\s*$', '', value)
        return value.strip()

    def _get_processed_tracks(self):
        """Return list of (original_tracknum, display_text) with removals and customs applied"""
        tracks = self.album.getTracks()
        removed = getattr(self, 'removed_tracks', set())
        items = []
        for i, track in enumerate(tracks, 1):
            if str(i) in removed:
                continue
            if hasattr(self, 'custom_tracks') and str(i) in self.custom_tracks:
                val = self.custom_tracks[str(i)]
                val = val if val is not None else ''
            else:
                val = self._clean_track_name(track)
            if val and not any(is_non_latin_glyph(ch) for ch in val):
                val = val.upper()
            items.append((i, val))
        return items

    def _fetch_cover(self):
        """Fetch the album cover image"""
        cover_url = self.album.getCoverArt()[0]['url']
        fallback_url = self.album.getSpotifyCoverUrl()
        return self.fetch_album_cover(cover_url, fallback_url=fallback_url)

    def _draw_tracks_columns(self, draw, start_y, x_start, available_width, available_height, num_cols=2):
        """Draw tracklist in multiple columns"""
        items = self._get_processed_tracks()
        if not items:
            return

        tracks_per_col = max((len(items) + num_cols - 1) // num_cols, 1)
        max_line_h = available_height / max(tracks_per_col, 1)
        base_fs = int(max_line_h / self.scale) - 3 if self.scale > 0 else int(max_line_h) - 3
        base_fs = min(base_fs, self._base_track_font_max)
        base_fs = max(base_fs, self._base_track_font_min)
        font_size = self._scale_font(base_fs)
        font = load_font(OSWALD_PATH, font_size)
        col_width = available_width // num_cols

        for idx, (tnum, val) in enumerate(items):
            col = idx // tracks_per_col
            row = idx % tracks_per_col
            x = x_start + col * col_width
            y = start_y + int(row * max_line_h)

            prefix = f"{tnum}." if self.dotted else f"{tnum}"
            sep = "  "
            display = f"{prefix}{sep}{val}"
            w = mixed_text_width(draw, display, font, font_size)
            while w > col_width - self._scale(10) and len(val) > 1:
                val = val[:-1].rstrip()
                display = f"{prefix}{sep}{val}..."
                w = mixed_text_width(draw, display, font, font_size)

            draw_mixed_text(draw, (x, y), display, font, font_size, self.album.text_color)

    # ─── Style dispatcher ───

    def buildPoster(self):
        """Build poster with the configured style"""
        if self.style == 'standard':
            return self._build_standard()
        elif self.style == 'frame':
            return self._build_frame()
        elif self.style == 'basic':
            return self._build_basic()
        elif self.style == 'fullcover':
            return self._build_fullcover()
        return self._build_classic()

    # ─── Classic (original layout) ───

    def _build_classic(self):
        """Original poster layout"""
        poster = self.create_poster(self.width, self.height, self.album.background)

        cover_url = self.album.getCoverArt()[0]['url']
        fallback_url = self.album.getSpotifyCoverUrl()
        album_img = self.fetch_album_cover(cover_url, fallback_url=fallback_url)

        cover_size = self._scale(640)
        album_img_resized = album_img.resize((cover_size, cover_size), Image.LANCZOS)

        self.overlay_album_cover(poster, album_img_resized)
        self.overlay_code_banner(poster)
        draw = ImageDraw.Draw(poster)
        self._precompute_label_extent(draw)
        self.draw_artist_name(draw)
        self.draw_album_name(draw)
        self.draw_tracks(draw)
        self.draw_release_date(draw)
        self.draw_runtime(draw)
        self.draw_label(draw)
        self.draw_color_squares(draw, album_img)
        return poster

    # ─── Standard (Posterfy-style: full-width cover + gradient fade) ───

    def _build_standard(self):
        poster = self.create_poster(self.width, self.height, self.album.background)
        album_img = self._fetch_cover()

        sm = self._scale(30)  # small margin
        cover_w = self.width - 2 * sm
        cover_h = cover_w
        cover_resized = album_img.resize((cover_w, cover_h), Image.LANCZOS)
        poster.paste(cover_resized, (sm, sm), cover_resized)

        # Gradient fade bottom of cover into background
        fade_h = self._scale(180)
        bg_rgba = self._hex_to_rgba(self.album.background)
        bg_strip = Image.new('RGBA', (cover_w, fade_h), bg_rgba)
        fade_mask = self._create_vertical_gradient(cover_w, fade_h, 0, 255)
        poster.paste(bg_strip, (sm, sm + cover_h - fade_h), fade_mask)

        draw = ImageDraw.Draw(poster)
        tc = self.album.text_color
        y = sm + cover_h + self._scale(20)

        # Album name — large, left-aligned
        album_name = (self._get_album_name() or '').upper()
        if album_name:
            font = self._fit_text_to_width(album_name, OSWALD_PATH, self._scale_font(42), cover_w)
            draw_mixed_text(draw, (sm, y), album_name, font, font.size, tc)
            bb = draw.textbbox((0, 0), album_name, font=font)
            y += (bb[3] - bb[1]) + self._scale(12)

        # Artist name
        artist_name = (self._get_artist_name() or '').upper()
        if artist_name:
            afont = load_font(OSWALD_PATH, self._scale_font(24))
            draw_mixed_text(draw, (sm, y), artist_name, afont, afont.size, tc)
            bb = draw.textbbox((0, 0), artist_name, font=afont)
            y += (bb[3] - bb[1]) + self._scale(22)

        # Tracklist — 2 columns
        track_area_h = self.height - y - self._scale(130)
        self._draw_tracks_columns(draw, y, sm, cover_w, track_area_h, num_cols=2)

        # Bottom bar — date, runtime, barcode, color squares
        bot_y = self.height - self._scale(110)
        info_font = load_font(OSWALD_PATH, self._scale_font(22))
        lbl_font = load_font(OSWALD_PATH, self._scale_font(14))

        # Date label + value (left)
        date_str = self._get_date_string()
        if date_str:
            draw.text((sm, bot_y), "RELEASE DATE", font=lbl_font, fill=tc)
            draw.text((sm, bot_y + self._scale(18)), date_str, font=info_font, fill=tc)

        # Runtime label + value (center-left)
        runtime_str = self.album.getRuntime()
        rt_x = sm + self._scale(200)
        if runtime_str:
            draw.text((rt_x, bot_y), "RUNTIME", font=lbl_font, fill=tc)
            draw.text((rt_x, bot_y + self._scale(18)), runtime_str, font=info_font, fill=tc)

        # Color squares (bottom right, aligned with bottom bar)
        self.draw_color_squares(draw, album_img, y_override=bot_y, margin_override=sm)

        # Spotify barcode (bottom right, below color squares)
        banner_w = self._scale(self._base_banner_width)
        self.overlay_code_banner(poster,
                                x_override=self.width - sm - banner_w,
                                y_override=self.height - self._scale(65))

        return poster

    # ─── Frame (bordered poster, clean separation) ───

    def _build_frame(self):
        poster = self.create_poster(self.width, self.height, self.album.background)
        album_img = self._fetch_cover()
        tc = self.album.text_color
        draw = ImageDraw.Draw(poster)

        border = self._scale(5)
        pad = self._scale(30)
        inner_x = border + pad
        inner_w = self.width - 2 * inner_x

        # Draw frame border
        draw.rectangle(
            [(border, border), (self.width - border - 1, self.height - border - 1)],
            outline=tc, width=max(border, 1)
        )

        # Cover — inside frame
        cover_size = inner_w
        cover_resized = album_img.resize((cover_size, cover_size), Image.LANCZOS)
        poster.paste(cover_resized, (inner_x, inner_x), cover_resized)

        # Thin separator line below cover
        sep_y = inner_x + cover_size + self._scale(15)
        draw.line([(inner_x, sep_y), (inner_x + inner_w, sep_y)], fill=tc, width=max(self._scale(2), 1))

        y = sep_y + self._scale(20)

        # Album name
        album_name = (self._get_album_name() or '').upper()
        if album_name:
            font = self._fit_text_to_width(album_name, OSWALD_PATH, self._scale_font(38), inner_w)
            draw_mixed_text(draw, (inner_x, y), album_name, font, font.size, tc)
            bb = draw.textbbox((0, 0), album_name, font=font)
            y += (bb[3] - bb[1]) + self._scale(12)

        # Artist name
        artist_name = (self._get_artist_name() or '').upper()
        if artist_name:
            afont = load_font(OSWALD_PATH, self._scale_font(22))
            draw_mixed_text(draw, (inner_x, y), artist_name, afont, afont.size, tc)
            bb = draw.textbbox((0, 0), artist_name, font=afont)
            y += (bb[3] - bb[1]) + self._scale(20)

        # Tracklist — 2 columns
        track_area_h = self.height - y - self._scale(130) - border
        self._draw_tracks_columns(draw, y, inner_x, inner_w, track_area_h, num_cols=2)

        # Bottom — date, runtime
        bot_y = self.height - self._scale(100) - border
        info_font = load_font(OSWALD_PATH, self._scale_font(22))
        lbl_font = load_font(OSWALD_PATH, self._scale_font(14))

        date_str = self._get_date_string()
        if date_str:
            draw.text((inner_x, bot_y), "RELEASE DATE", font=lbl_font, fill=tc)
            draw.text((inner_x, bot_y + self._scale(18)), date_str, font=info_font, fill=tc)

        runtime_str = self.album.getRuntime()
        rt_x = inner_x + self._scale(200)
        if runtime_str:
            draw.text((rt_x, bot_y), "RUNTIME", font=lbl_font, fill=tc)
            draw.text((rt_x, bot_y + self._scale(18)), runtime_str, font=info_font, fill=tc)

        # Color squares and barcode
        self.draw_color_squares(draw, album_img, y_override=bot_y, margin_override=inner_x)
        banner_w = self._scale(self._base_banner_width)
        self.overlay_code_banner(poster,
                                x_override=self.width - inner_x - banner_w,
                                y_override=self.height - self._scale(60) - border)

        return poster

    # ─── Basic (minimal — no tracklist) ───

    def _build_basic(self):
        poster = self.create_poster(self.width, self.height, self.album.background)
        album_img = self._fetch_cover()
        tc = self.album.text_color

        sm = self._scale(30)
        cover_w = self.width - 2 * sm
        cover_h = cover_w
        cover_resized = album_img.resize((cover_w, cover_h), Image.LANCZOS)
        poster.paste(cover_resized, (sm, sm), cover_resized)

        # Gradient fade
        fade_h = self._scale(200)
        bg_rgba = self._hex_to_rgba(self.album.background)
        bg_strip = Image.new('RGBA', (cover_w, fade_h), bg_rgba)
        fade_mask = self._create_vertical_gradient(cover_w, fade_h, 0, 255)
        poster.paste(bg_strip, (sm, sm + cover_h - fade_h), fade_mask)

        draw = ImageDraw.Draw(poster)
        center_x = self.width // 2
        # Push text down — use the space between cover bottom and poster bottom
        text_zone_top = sm + cover_h + self._scale(30)
        text_zone_bot = self.height - self._scale(130)
        zone_h = text_zone_bot - text_zone_top
        # Center the text block vertically in the available zone
        # Estimate block height: ~50+14+28+14+24+10+24 = ~164 base px
        block_est = self._scale(170)
        y = text_zone_top + max((zone_h - block_est) // 2, 0)

        # Album name — centered, large
        album_name = (self._get_album_name() or '').upper()
        if album_name:
            font = self._fit_text_to_width(album_name, OSWALD_PATH, self._scale_font(46), cover_w)
            bb = draw.textbbox((0, 0), album_name, font=font)
            tw = bb[2] - bb[0]
            draw_mixed_text(draw, (center_x - tw // 2, y), album_name, font, font.size, tc)
            y += (bb[3] - bb[1]) + self._scale(14)

        # Artist name — centered
        artist_name = (self._get_artist_name() or '').upper()
        if artist_name:
            afont = load_font(OSWALD_PATH, self._scale_font(26))
            bb = draw.textbbox((0, 0), artist_name, font=afont)
            tw = bb[2] - bb[0]
            draw_mixed_text(draw, (center_x - tw // 2, y), artist_name, afont, afont.size, tc)
            y += (bb[3] - bb[1]) + self._scale(35)

        # Date — centered
        date_str = self._get_date_string()
        if date_str:
            dfont = load_font(OSWALD_PATH, self._scale_font(22))
            bb = draw.textbbox((0, 0), date_str, font=dfont)
            tw = bb[2] - bb[0]
            draw.text((center_x - tw // 2, y), date_str, font=dfont, fill=tc)
            y += (bb[3] - bb[1]) + self._scale(12)

        # Runtime — centered
        runtime_str = self.album.getRuntime()
        if runtime_str:
            rfont = load_font(OSWALD_PATH, self._scale_font(22))
            bb = draw.textbbox((0, 0), runtime_str, font=rfont)
            tw = bb[2] - bb[0]
            draw.text((center_x - tw // 2, y), runtime_str, font=rfont, fill=tc)

        # Color squares & barcode — centered-ish near bottom
        sq_y = self.height - self._scale(120)
        self.draw_color_squares(draw, album_img, y_override=sq_y, margin_override=sm)
        banner_w = self._scale(self._base_banner_width)
        banner_x = center_x - banner_w // 2
        self.overlay_code_banner(poster, x_override=banner_x,
                                y_override=self.height - self._scale(75))

        return poster

    # ─── Full Cover (album art fills poster, text overlaid) ───

    def _build_fullcover(self):
        poster = self.create_poster(self.width, self.height, self.album.background)
        album_img = self._fetch_cover()

        # Scale cover to fill entire poster (crop to fit)
        img_ratio = album_img.width / album_img.height
        poster_ratio = self.width / self.height
        if img_ratio > poster_ratio:
            new_h = self.height
            new_w = int(album_img.width * self.height / album_img.height)
        else:
            new_w = self.width
            new_h = int(album_img.height * self.width / album_img.width)
        cover_scaled = album_img.resize((new_w, new_h), Image.LANCZOS)
        left = (new_w - self.width) // 2
        top = (new_h - self.height) // 2
        cover_cropped = cover_scaled.crop((left, top, left + self.width, top + self.height))
        poster.paste(cover_cropped, (0, 0))

        # Dark gradient overlay on bottom 55%
        overlay_h = int(self.height * 0.55)
        dark_strip = Image.new('RGBA', (self.width, overlay_h), (0, 0, 0, 255))
        grad_mask = self._create_vertical_gradient(self.width, overlay_h, 0, 190)
        poster.paste(dark_strip, (0, self.height - overlay_h), grad_mask)

        draw = ImageDraw.Draw(poster)
        tc = self.album.text_color
        sm = self._scale(40)
        y = self.height - overlay_h + self._scale(60)

        # Album name — large, left-aligned on overlay
        album_name = (self._get_album_name() or '').upper()
        avail_w = self.width - 2 * sm
        if album_name:
            font = self._fit_text_to_width(album_name, OSWALD_PATH, self._scale_font(44), avail_w)
            draw_mixed_text(draw, (sm, y), album_name, font, font.size, tc)
            bb = draw.textbbox((0, 0), album_name, font=font)
            y += (bb[3] - bb[1]) + self._scale(12)

        # Artist name
        artist_name = (self._get_artist_name() or '').upper()
        if artist_name:
            afont = load_font(OSWALD_PATH, self._scale_font(24))
            draw_mixed_text(draw, (sm, y), artist_name, afont, afont.size, tc)
            bb = draw.textbbox((0, 0), artist_name, font=afont)
            y += (bb[3] - bb[1]) + self._scale(22)

        # Tracklist — 2 columns
        track_area_h = self.height - y - self._scale(120)
        self._draw_tracks_columns(draw, y, sm, avail_w, track_area_h, num_cols=2)

        # Bottom: date + runtime
        bot_y = self.height - self._scale(90)
        info_font = load_font(OSWALD_PATH, self._scale_font(20))
        date_str = self._get_date_string()
        if date_str:
            draw.text((sm, bot_y), date_str, font=info_font, fill=tc)
        runtime_str = self.album.getRuntime()
        if runtime_str:
            bb = draw.textbbox((0, 0), runtime_str, font=info_font)
            rw = bb[2] - bb[0]
            draw.text((self.width - sm - rw, bot_y), runtime_str, font=info_font, fill=tc)

        # Color squares (bottom left, above date)
        self.draw_color_squares(draw, album_img, y_override=bot_y - self._scale(40), margin_override=sm)
        # Barcode (bottom right) — transparent bg so album art shows through
        banner_w = self._scale(self._base_banner_width)
        self.overlay_code_banner(poster,
                                x_override=self.width - sm - banner_w,
                                y_override=self.height - self._scale(65),
                                transparent_bg=True)

        return poster

    def create_poster(self, width, height, background):
        """Create the blank canvas of the poster"""
        return Image.new(mode="RGBA", size=(width, height), color=background)

    def fetch_album_cover(self, url, fallback_url=None):
        """Return the image of the album cover. If url fails, try fallback_url."""
        try:
            if not url or len(url.strip()) == 0:
                raise ValueError("Empty URL provided")

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            return Image.open(BytesIO(response.content)).convert("RGBA")
        except Exception as e:
            print(f"Error fetching album cover from {url}: {e}")
            # Try fallback URL (original Spotify cover) if available
            if fallback_url and fallback_url != url:
                try:
                    print(f"Falling back to original cover: {fallback_url}")
                    response = requests.get(fallback_url, timeout=10)
                    response.raise_for_status()
                    return Image.open(BytesIO(response.content)).convert("RGBA")
                except Exception as e2:
                    print(f"Error fetching fallback cover: {e2}")
            # Return a placeholder image (solid color) as last resort
            placeholder = Image.new('RGBA', (640, 640), (128, 128, 128, 255))
            return placeholder

    def overlay_album_cover(self, poster, album_img):
        """Paste the album cover onto the image"""
        poster.paste(album_img, (self.margin, self.margin), album_img)

    def overlay_code_banner(self, poster, x_override=None, y_override=None, transparent_bg=False):
        """Overlay the Spotify code banner, scaled appropriately"""
        banner_width = self._scale(self._base_banner_width)
        banner_height = self._scale(self._base_banner_height)

        code_banner = return_banner(
            self.album.album_id,
            self.album.background,
            self.album.text_color,
            size=(banner_width, banner_height),
            transparent_bg=transparent_bg,
        )

        banner_x = x_override if x_override is not None else self._scale(440 - 50 + 15)
        banner_y = y_override if y_override is not None else self._scale(1125)

        poster.paste(code_banner, (banner_x, banner_y), code_banner)

    def _precompute_label_extent(self, draw):
        """Pre-compute the label text's leftmost x so draw_tracks can avoid overlapping."""
        if hasattr(self, 'custom_label') and self.custom_label is not None:
            label_string = self.custom_label
        else:
            label_string = "Released by " + self.album.getLabel().split(',')[0]

        if not label_string:
            self.label_left_x = self.width
            return

        font_size = self._scale_font(self._base_label_font_size)
        label_font = ImageFont.truetype('static/Oswald-Medium.ttf', font_size)
        max_text_w = int(self.width * 0.55)
        lines = self._pixel_wrap(draw, label_string, label_font, max_text_w)

        min_x = self.width
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=label_font)
            w = bbox[2] - bbox[0]
            x = self.width - w - self.margin
            min_x = min(min_x, x)

        self.label_left_x = min_x

    def _pixel_wrap(self, draw, text, font, max_width):
        """Wrap text by pixel width. Returns list of lines that each fit within max_width."""
        words = text.split()
        if not words:
            return []
        lines = []
        current = words[0]
        for word in words[1:]:
            test = current + ' ' + word
            bbox = draw.textbbox((0, 0), test, font=font)
            if (bbox[2] - bbox[0]) <= max_width:
                current = test
            else:
                lines.append(current)
                current = word
        lines.append(current)
        return lines

    def _fit_right_text(self, draw, text, base_font_size):
        """Wrap and measure right-aligned text using pixel-based wrapping, auto-scaling
        font if it extends past center.
        Returns (lines, font, font_size, min_x) where min_x is the leftmost x position."""
        font_size = self._scale_font(base_font_size)
        # The right-side text should not extend past 45% from the left edge
        min_allowed_x = int(self.width * 0.45)
        # Max pixel width: from the min_allowed_x to the right edge minus margin
        max_pixel_w = self.width - self.margin - min_allowed_x

        for attempt in range(5):  # Try up to 5 reductions
            font = ImageFont.truetype('static/Oswald-Medium.ttf', font_size)
            lines = self._pixel_wrap(draw, text, font, max_pixel_w)
            min_x = self.width - self.margin

            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_w = bbox[2] - bbox[0]
                x = self.width - text_w - self.margin
                min_x = min(min_x, x)

            if min_x >= min_allowed_x or font_size <= self._scale_font(16):
                break
            # Reduce font size to fit
            font_size = max(font_size - self._scale(2), self._scale_font(16))

        return lines, font, font_size, min_x

    def draw_artist_name(self, draw):
        # Check for custom artist (can be empty string to hide)
        if hasattr(self, 'custom_artist') and self.custom_artist is not None:
            artist_name = self.custom_artist.upper() if self.custom_artist else ''
        else:
            artist_name = self.album.artist_name.upper()

        y_offset = self.below_pic_h + self._scale(30)
        x_coordinate = self.width - self.margin  # Default if no text

        if artist_name:
            lines, artist_font, font_size, x_coordinate = self._fit_right_text(
                draw, artist_name, self._base_artist_font_size)

            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=artist_font)
                text_w = bbox[2] - bbox[0]
                line_x = self.width - text_w - self.margin
                x_coordinate = min(x_coordinate, line_x)
                draw.text((line_x, y_offset), line, font=artist_font, fill=self.album.text_color)
                line_height = bbox[3] - bbox[1]
                y_offset += line_height + self._scale(self._base_line_spacing)

        self.y_offset = y_offset
        self.x_artist = x_coordinate

    def draw_album_name(self, draw):
        # Check for custom album (can be empty string to hide)
        if hasattr(self, 'custom_album') and self.custom_album is not None:
            album_name = self.custom_album.upper() if self.custom_album else ''
        else:
            album_name = self.album.album_name.upper()

        y_offset = self.y_offset
        x_coordinate = self.width - self.margin  # Default if no text

        if album_name:
            lines, album_font, font_size, x_coordinate = self._fit_right_text(
                draw, album_name, self._base_album_font_size)

            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=album_font)
                text_w = bbox[2] - bbox[0]
                line_x = self.width - text_w - self.margin
                x_coordinate = min(x_coordinate, line_x)
                draw.text((line_x, y_offset), line, font=album_font, fill=self.album.text_color)
                line_height = bbox[3] - bbox[1]
                y_offset += line_height + self._scale(self._base_line_spacing)

        self.x_album = x_coordinate
        self.start_date = y_offset

    def draw_tracks(self, draw):
        tracks = self.album.getTracks()

        # Track which tracks were truncated (for UI toggle state)
        self.truncated_tracks = set()

        # Filter out removed tracks if any
        removed_tracks = getattr(self, 'removed_tracks', set())
        if removed_tracks:
            # Create new list excluding removed tracks
            filtered_tracks = []
            for i, track in enumerate(tracks, 1):
                if str(i) not in removed_tracks:
                    filtered_tracks.append((i, track))
            tracks_with_nums = filtered_tracks
        else:
            tracks_with_nums = [(i, track) for i, track in enumerate(tracks, 1)]

        num_tracks = len(tracks_with_nums)
        if num_tracks == 0:
            return

        # Calculate track height based on available space (all scaled)
        base_bottom_margin = 50
        max_track_height = (self.height - self._scale(base_bottom_margin) - self.below_pic_h) / max(num_tracks, self.full_page_track_count)

        # Scale font size properly
        base_font_size = int(max_track_height / self.scale) - 5 if self.scale > 0 else int(max_track_height) - 5
        base_font_size = min(base_font_size, self._base_track_font_max)
        base_font_size = max(base_font_size, self._base_track_font_min)
        font_size = self._scale_font(base_font_size)

        latin_font = load_font(OSWALD_PATH, font_size)

        # Calculate available text width — tracks must not extend into right-side text
        # Account for artist name, album name, AND label text extents
        label_left = getattr(self, 'label_left_x', self.width)
        right_boundary = min(self.x_artist, self.x_album, label_left)
        available_text_width = max(
            right_boundary - (2 * self.margin),
            self._scale(120)
        )

        # Start offset at the scaled position (710 is the base value at 740x1200)
        offset = self.below_pic_h  # Use already-scaled below_pic_h
        no_truncate = getattr(self, 'no_truncate_tracks', set())

        for original_tracknum, value in tracks_with_nums:
            # Check if there's a custom track text override (including empty string)
            if hasattr(self, 'custom_tracks') and str(original_tracknum) in self.custom_tracks:
                custom_value = self.custom_tracks[str(original_tracknum)]
                # Use custom value as-is (allows empty strings to hide track text)
                value = custom_value if custom_value is not None else ''
            else:
                # --- cleanup rules ---
                # Remove remastered variations: "- Remastered", "- Remaster 2023", "(Remastered)", etc.
                value = re.sub(r'\s*[-–—]\s*remaster(ed)?\s*\d*\s*', '', value, flags=re.IGNORECASE)
                value = re.sub(r'\s*[-–—]\s*\d+\s*remaster(ed)?\s*', '', value, flags=re.IGNORECASE)
                value = re.sub(r'\(.*?remaster(ed)?.*?\)', '', value, flags=re.IGNORECASE)
                value = re.sub(r'\[.*?remaster(ed)?.*?\]', '', value, flags=re.IGNORECASE)
                # Remove other common suffixes
                value = re.sub(r'\s*[-–—]\s*(mono|stereo|deluxe|bonus|extended|anniversary|edition).*$', '', value, flags=re.IGNORECASE)
                value = re.sub(r'\(.*?(mono|stereo|deluxe|bonus|extended|anniversary|edition).*?\)', '', value, flags=re.IGNORECASE)
                # Remove feat./featuring
                value = re.split(r'\s+feat\.', value, flags=re.IGNORECASE)[0]
                value = re.split(r'\s+featuring\s+', value, flags=re.IGNORECASE)[0]
                value = re.split(r'\s+ft\.', value, flags=re.IGNORECASE)[0]
                # Remove remaining parentheses/brackets content
                value = re.sub(r'\(.*?\)', '', value)
                value = re.sub(r'\[.*?\]', '', value)
                # Clean up extra whitespace and dashes at the end
                value = re.sub(r'\s*[-–—]\s*$', '', value)
                value = value.strip()

            # Uppercase only if *all* characters are Latin-ish
            if value and not any(is_non_latin_glyph(ch) for ch in value):
                value = value.upper()

            # Measure mixed width
            w = mixed_text_width(draw, value, latin_font, font_size)

            # Truncate — strip the actual text (not the ellipsis) then re-append
            should_truncate = str(original_tracknum) not in no_truncate
            if w > available_text_width and len(value) > 1 and should_truncate:
                # Remove characters from the core text, then measure with ellipsis
                core = value
                ellipsis = "..."
                while len(core) > 1:
                    space_index = core.rfind(" ", 0, len(core) - 1)
                    if space_index > 0:
                        core = core[:space_index].rstrip()
                    else:
                        core = core[:-1].rstrip()
                    candidate = core + ellipsis
                    w = mixed_text_width(draw, candidate, latin_font, font_size)
                    if w <= available_text_width:
                        break
                value = core + ellipsis if len(core) > 0 else ellipsis
                w = mixed_text_width(draw, value, latin_font, font_size)
                self.truncated_tracks.add(str(original_tracknum))
            elif w > available_text_width and len(value) > 1:
                # Track would have been truncated but user disabled it
                self.truncated_tracks.add(str(original_tracknum))

            # formatting
            space = "     "
            display_tracknum = original_tracknum
            if self.dotted:
                display_tracknum = f"{original_tracknum}."
                space += " "

            if self.tabulated:
                if len(tracks_with_nums) >= 10 or any(tn >= 10 for tn, _ in tracks_with_nums):
                    space += " "

                # number is Oswald
                draw.text((self.margin, offset), f"{display_tracknum}", font=latin_font, fill=self.album.text_color)

                # title is mixed (English Oswald, non-Latin Noto)
                draw_mixed_text(
                    draw,
                    (self.margin, offset),
                    f"{space}{value}",
                    latin_font=latin_font,
                    size=font_size,
                    fill=self.album.text_color,
                    fake_bold_px=0  # set to 1 later if you still want thicker
                )
            else:
                draw_mixed_text(
                    draw,
                    (self.margin, offset),
                    f"{display_tracknum}  {value}",
                    latin_font=latin_font,
                    size=font_size,
                    fill=self.album.text_color,
                    fake_bold_px=0
                )

            offset += max_track_height

        # Record where the track list ends so label can avoid overlapping
        self.tracks_end_y = offset


    def draw_release_date(self, draw):
        # Check for custom date override (can be empty string to hide)
        if hasattr(self, 'custom_date') and self.custom_date is not None:
            date_string = self.custom_date
        else:
            date_string = self.album.getReleaseDate()

        if not date_string:
            # Still set y position for subsequent elements
            self.date_end_y = max(
                getattr(self, 'start_date', self.below_pic_h) + self._scale(20),
                self.below_pic_h + self._scale(230)
            )
            return

        # Use scaled font size
        font_size = self._scale_font(self._base_date_font_size)
        date_font = ImageFont.truetype('static/Oswald-Medium.ttf', font_size)

        # Use textbbox for accurate width measurement
        bbox = draw.textbbox((0, 0), date_string, font=date_font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        # Dynamic y: use start_date with gap, but never higher than the original fixed offset
        y_offset = max(
            getattr(self, 'start_date', self.below_pic_h) + self._scale(20),
            self.below_pic_h + self._scale(230)
        )
        draw.text((self.width - w - self.margin, y_offset),
                date_string, font=date_font, fill=self.album.text_color)
        self.date_end_y = y_offset + h + self._scale(self._base_line_spacing)

    

    def draw_runtime(self, draw):
        runtime_string = self.album.getRuntime()
        font_size = self._scale_font(self._base_runtime_font_size)
        runtime_font = ImageFont.truetype('static/Oswald-Medium.ttf', font_size)

        bbox = draw.textbbox((0, 0), runtime_string, font=runtime_font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        # Dynamic y: use date_end_y if available, otherwise fall back to fixed offset
        y_offset = max(
            getattr(self, 'date_end_y', self.below_pic_h + self._scale(270)),
            self.below_pic_h + self._scale(270)
        )

        draw.text(
            (self.width - w - self.margin, y_offset),
            runtime_string,
            font=runtime_font,
            fill=self.album.text_color
        )
        self.runtime_end_y = y_offset + h + self._scale(self._base_line_spacing)

    def draw_label(self, draw):
        # Check for custom label override (can be empty string to hide)
        if hasattr(self, 'custom_label') and self.custom_label is not None:
            label_string = self.custom_label
        else:
            label_string = "Released by " + self.album.getLabel().split(',')[0]

        if not label_string:
            return

        # Use scaled font size
        font_size = self._scale_font(self._base_label_font_size)
        label_font = ImageFont.truetype('static/Oswald-Medium.ttf', font_size)
        ascent, descent = label_font.getmetrics()

        # Wrap so text never exceeds ~55% of poster width (pixel-based)
        max_text_w = int(self.width * 0.55)
        label_list = self._pixel_wrap(draw, label_string, label_font, max_text_w)

        # Dynamic y: use runtime_end_y if available, otherwise fall back to fixed offset
        current_y = max(
            getattr(self, 'runtime_end_y', self.below_pic_h + self._scale(310)),
            self.below_pic_h + self._scale(310)
        )
        max_y = self.height - self._scale(90)
        line_spacing = self._scale(5)
        g = 0

        for string in label_list:
            if current_y + g <= max_y:
                bbox = draw.textbbox((0, 0), string, font=label_font)
                w = bbox[2] - bbox[0]
                draw.text((self.width - w - self.margin, current_y + g),
                        string, font=label_font, fill=self.album.text_color)
                g += ascent + descent + line_spacing
            else:
                break

    def draw_color_squares(self, draw, album_img, y_override=None, margin_override=None):
        colors = self.get_colors(album_img, 5, 250)

        square_size = self._scale(self._base_color_square_size)
        spacing = self._scale(self._base_color_square_spacing)
        y = y_override if y_override is not None else self.below_pic_h
        m = margin_override if margin_override is not None else self.margin

        offset = 0
        for color in colors:
            draw.rectangle([
                (self.width - m - offset - square_size, y),
                (self.width - m - offset, y + square_size)
            ], fill=color, outline=color)
            offset += spacing

    def get_colors(self, image, numcolors=6, resize=150):
        img = image.copy()
        img.thumbnail((resize, resize))

        paletted = img.convert('P', palette=Image.ADAPTIVE, colors=numcolors)

        palette = paletted.getpalette()
        color_counts = sorted(paletted.getcolors(), reverse=True)
        colors = []

        num_colors_to_return = min(numcolors, len(color_counts))
        
        for i in range(num_colors_to_return):
            palette_index = color_counts[i][1]
            dominant_color = palette[palette_index*3:palette_index*3+3]
            colors.append(tuple(dominant_color))

        return colors

    def encodeImage(self, image, dpi=300):
        """Encode image to base64 with specified DPI"""
        data = io.BytesIO()
        image.save(data, "PNG", dpi=(dpi, dpi))
        encoded_img_data = base64.b64encode(data.getvalue())
        decoded_img = encoded_img_data.decode('utf-8')
        img_data = f"data:image/png;base64,{decoded_img}"
        return img_data

    def getImageBytes(self, image, format='PNG', dpi=300):
        """Get raw image bytes for download"""
        data = io.BytesIO()
        if format.upper() == 'PNG':
            image.save(data, "PNG", dpi=(dpi, dpi))
        elif format.upper() == 'JPEG':
            # Convert to RGB for JPEG (no alpha)
            rgb_image = Image.new('RGB', image.size, (255, 255, 255))
            rgb_image.paste(image, mask=image.split()[3] if image.mode == 'RGBA' else None)
            rgb_image.save(data, "JPEG", quality=95, dpi=(dpi, dpi))
        data.seek(0)
        return data

    def generateSVG(self):
        """Generate an SVG version of the poster"""
        # Collect all the data needed for SVG
        svg_data = {
            'width': self.width,
            'height': self.height,
            'background': self.album.background,
            'text_color': self.album.text_color,
            'artist_name': self.album.artist_name.upper(),
            'album_name': self.album.album_name.upper(),
            'release_date': self.album.getReleaseDate(),
            'runtime': self.album.getRuntime(),
            'label': "Released by " + self.album.getLabel().split(',')[0],
            'tracks': self.album.getTracks()[:30],
            'album_cover_url': self.album.getCoverArt()[0]['url'],
            'margin': self.margin,
            'below_pic_h': self.below_pic_h,
        }
        
        return self._buildSVG(svg_data)
    
    def _buildSVG(self, data):
        """Build SVG string from poster data"""
        w = data['width']
        h = data['height']
        margin = data['margin']
        below_pic_h = data['below_pic_h']
        bg = data['background']
        text_color = data['text_color']
        
        # Font sizes scaled
        artist_font = self._scale_font(self._base_artist_font_size)
        album_font = self._scale_font(self._base_album_font_size)
        track_font = self._scale_font(20)  # Average track font
        info_font = self._scale_font(self._base_date_font_size)
        
        # Album cover size
        cover_size = self._scale(640)
        
        # Build SVG
        svg_parts = []
        svg_parts.append(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" 
     width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500&amp;display=swap');
      .artist {{ font-family: 'Oswald', sans-serif; font-size: {artist_font}px; font-weight: 500; fill: {text_color}; }}
      .album {{ font-family: 'Oswald', sans-serif; font-size: {album_font}px; font-weight: 500; fill: {text_color}; }}
      .track {{ font-family: 'Oswald', sans-serif; font-size: {track_font}px; font-weight: 500; fill: {text_color}; }}
      .info {{ font-family: 'Oswald', sans-serif; font-size: {info_font}px; font-weight: 500; fill: {text_color}; }}
    </style>
  </defs>
  
  <!-- Background -->
  <rect width="{w}" height="{h}" fill="{bg}"/>
  
  <!-- Album Cover (embedded as image) -->
  <image x="{margin}" y="{margin}" width="{cover_size}" height="{cover_size}" 
         xlink:href="{data['album_cover_url']}" preserveAspectRatio="xMidYMid slice"/>
''')
        
        # Artist name (right aligned)
        y_pos = below_pic_h + self._scale(50)
        svg_parts.append(f'  <text x="{w - margin}" y="{y_pos}" class="artist" text-anchor="end">{self._escape_xml(data["artist_name"])}</text>')
        
        # Album name
        y_pos += self._scale(50)
        svg_parts.append(f'  <text x="{w - margin}" y="{y_pos}" class="album" text-anchor="end">{self._escape_xml(data["album_name"])}</text>')
        
        # Tracks
        track_y = below_pic_h + self._scale(10)
        track_spacing = self._scale(35)
        for i, track in enumerate(data['tracks'][:15], 1):  # Limit for SVG
            track_clean = re.sub(r'\(.*?\)', '', track).strip()
            if not any(is_non_latin_glyph(ch) for ch in track_clean):
                track_clean = track_clean.upper()
            svg_parts.append(f'  <text x="{margin}" y="{track_y}" class="track">{i}  {self._escape_xml(track_clean)}</text>')
            track_y += track_spacing
        
        # Release date and runtime
        info_y = below_pic_h + self._scale(240)
        svg_parts.append(f'  <text x="{w - margin}" y="{info_y}" class="info" text-anchor="end">{self._escape_xml(data["release_date"])}</text>')
        info_y += self._scale(40)
        svg_parts.append(f'  <text x="{w - margin}" y="{info_y}" class="info" text-anchor="end">{data["runtime"]}</text>')
        
        # Label
        info_y += self._scale(50)
        svg_parts.append(f'  <text x="{w - margin}" y="{info_y}" class="info" text-anchor="end">{self._escape_xml(data["label"])}</text>')
        
        svg_parts.append('</svg>')
        
        return '\n'.join(svg_parts)
    
    def _escape_xml(self, text):
        """Escape special XML characters"""
        return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;'))

    def scaleDown(self, text, x1, y1, x2, y2, font, font_size):
        im = Image.new("RGB", (x2-x1, y2-y1), "#fff")
        box = ((x1, y1, x2, y2))
        print(box)
        draw = ImageDraw.Draw(im)
        draw.rectangle(box, outline="#000")
        font_size = 40
        size = None
        while (size is None or size[0] > box[2] - box[0] or size[1] > box[3] - box[1]) and font_size > 0:
            font = ImageFont.truetype('static/Oswald-Medium.ttf', font_size)
            size = font.getsize_multiline(text)
            font_size -= 1
        draw.multiline_text((box[0], box[1]), text, "#000", font)

    def get_scaled_font(self, text, font_path, max_width, max_size):
        """Dynamically scale the font size to fit the text within the max_width."""
        font_size = max_size
        while font_size > 10:
            font = ImageFont.truetype(font_path, font_size)
            bbox = font.getbbox(text)
            text_w = bbox[2] - bbox[0]
            if text_w <= max_width:
                return font
            font_size -= 1
        return ImageFont.truetype(font_path, 10)