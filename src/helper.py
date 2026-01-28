from src.album import Album
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import textwrap
from src.codec import return_banner

import scipy
import scipy.misc
import scipy.cluster

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


class Utility:
    def __init__(self, album, resolution='medium'):
        self.album = album
        self.resolution = resolution
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

    def buildPoster(self):
        """Build poster at the configured resolution"""
        poster = self.create_poster(self.width, self.height, self.album.background)
        album_img = self.fetch_album_cover(self.album.getCoverArt()[0]['url'])
        
        # Resize album cover to fit the scaled poster
        cover_size = self._scale(640)  # Base album cover is 640x640
        album_img_resized = album_img.resize((cover_size, cover_size), Image.LANCZOS)
        
        self.overlay_album_cover(poster, album_img_resized)
        self.overlay_code_banner(poster)
        draw = ImageDraw.Draw(poster)
        self.draw_artist_name(draw)
        self.draw_album_name(draw)
        self.draw_tracks(draw)
        self.draw_release_date(draw)
        self.draw_runtime(draw)
        self.draw_label(draw)
        self.draw_color_squares(draw, album_img)
        return poster

    def create_poster(self, width, height, background):
        """Create the blank canvas of the poster"""
        return Image.new(mode="RGBA", size=(width, height), color=background)

    def fetch_album_cover(self, url):
        """Return the image of the album cover"""
        try:
            if not url or len(url.strip()) == 0:
                raise ValueError("Empty URL provided")

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            return Image.open(BytesIO(response.content)).convert("RGBA")
        except Exception as e:
            print(f"Error fetching album cover from {url}: {e}")
            # Return a placeholder image (solid color)
            placeholder = Image.new('RGBA', (640, 640), (128, 128, 128, 255))
            return placeholder

    def overlay_album_cover(self, poster, album_img):
        """Paste the album cover onto the image"""
        poster.paste(album_img, (self.margin, self.margin), album_img)

    def overlay_code_banner(self, poster):
        """Overlay the Spotify code banner, scaled appropriately"""
        banner_width = self._scale(self._base_banner_width)
        banner_height = self._scale(self._base_banner_height)
        
        code_banner = return_banner(
            self.album.album_id, 
            self.album.background, 
            self.album.text_color,
            size=(banner_width, banner_height)
        )
        
        # Calculate banner position (bottom right area)
        banner_x = self._scale(440 - 50 + 15)  # 440 - margin + 15 at base
        banner_y = self._scale(1125)
        
        poster.paste(code_banner, (banner_x, banner_y), code_banner)

    def draw_artist_name(self, draw):
        artist_name = self.album.artist_name.upper()
        font_size = self._scale_font(self._base_artist_font_size)
        artist_font = ImageFont.truetype('static/Oswald-Medium.ttf', font_size)

        # Adjust wrap width based on scale
        wrap_width = max(int(20 / self.scale), 10) if self.scale < 1 else 20
        artist_name_wrapped = textwrap.wrap(artist_name, width=wrap_width)
        y_offset = self.below_pic_h + self._scale(30)

        for line in artist_name_wrapped:
            bbox = draw.textbbox((0, 0), line, font=artist_font)
            text_w = bbox[2] - bbox[0]
            x_coordinate = self.width - text_w - self.margin
            draw.text((x_coordinate, y_offset), line, font=artist_font, fill=self.album.text_color)
            line_height = bbox[3] - bbox[1]
            y_offset += line_height + self._scale(self._base_line_spacing)
            
        self.y_offset = y_offset
        self.x_artist = x_coordinate

    def draw_album_name(self, draw):
        album_name = self.album.album_name.upper()
        font_size = self._scale_font(self._base_album_font_size)
        album_font = ImageFont.truetype('static/Oswald-Medium.ttf', font_size)

        wrap_width = max(int(16 / self.scale), 8) if self.scale < 1 else 16
        album_name_wrapped = textwrap.wrap(album_name, width=wrap_width)
        y_offset = self.y_offset

        for line in album_name_wrapped:
            bbox = draw.textbbox((0, 0), line, font=album_font)
            text_w = bbox[2] - bbox[0]
            x_coordinate = self.width - text_w - self.margin
            draw.text((x_coordinate, y_offset), line, font=album_font, fill=self.album.text_color)
            line_height = bbox[3] - bbox[1]
            y_offset += line_height + self._scale(self._base_line_spacing)

        self.x_album = x_coordinate
        self.start_date = y_offset

    def draw_tracks(self, draw):
        tracks = list(self.album.getTracks().values())[:30]

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

        # Calculate available text width using scaled values
        available_text_width = min(self.x_artist, self.x_album) - (2 * self.margin)

        # Start offset at the scaled position (710 is the base value at 740x1200)
        offset = self.below_pic_h  # Use already-scaled below_pic_h

        for original_tracknum, value in tracks_with_nums:
            # Check if there's a custom track text override
            if hasattr(self, 'custom_tracks') and str(original_tracknum) in self.custom_tracks:
                value = self.custom_tracks[str(original_tracknum)]
            else:
                # --- cleanup rules ---
                value = re.sub(r'\(.*?\)-', '', value)
                value = re.split(r' feat\.', value, flags=re.IGNORECASE)[0]
                value = re.split(r' REMASTER', value, flags=re.IGNORECASE)[0]
                value = re.split(r' \(', value, flags=re.IGNORECASE)[0]
                value = re.sub(r'\(.*?\)', '', value).strip()

            # Uppercase only if *all* characters are Latin-ish
            if value and not any(is_non_latin_glyph(ch) for ch in value):
                value = value.upper()

            # Measure mixed width
            w = mixed_text_width(draw, value, latin_font, font_size)

            # Truncate
            ellipsis = "..."
            while w > available_text_width and len(value) > 1:
                # Prefer truncating at spaces, else trim by character
                space_index = value.rfind(" ", 0, len(value) - 1)
                if space_index != -1:
                    value = value[:space_index].rstrip()
                else:
                    value = value[:-1].rstrip()

                value = value + ellipsis
                w = mixed_text_width(draw, value, latin_font, font_size)

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


    def draw_release_date(self, draw):
        # Check for custom date override
        if hasattr(self, 'custom_date') and self.custom_date:
            date_string = self.custom_date
        else:
            date_string = self.album.getReleaseDate()

        # Use scaled font size
        font_size = self._scale_font(self._base_date_font_size)
        date_font = ImageFont.truetype('static/Oswald-Medium.ttf', font_size)

        # Use textbbox for accurate width measurement
        bbox = draw.textbbox((0, 0), date_string, font=date_font)
        w = bbox[2] - bbox[0]

        # Scale the vertical offset (230 at base resolution)
        y_offset = self.below_pic_h + self._scale(230)
        draw.text((self.width - w - self.margin, y_offset),
                date_string, font=date_font, fill=self.album.text_color)

    

    def draw_runtime(self, draw):
        runtime_string = self.album.getRuntime()
        font_size = self._scale_font(self._base_runtime_font_size)
        runtime_font = ImageFont.truetype('static/Oswald-Medium.ttf', font_size)

        bbox = draw.textbbox((0, 0), runtime_string, font=runtime_font)
        w = bbox[2] - bbox[0]

        draw.text(
            (self.width - w - self.margin, self.below_pic_h + self._scale(270)),
            runtime_string, 
            font=runtime_font, 
            fill=self.album.text_color
        )

    def draw_label(self, draw):
        # Check for custom label override
        if hasattr(self, 'custom_label') and self.custom_label:
            label_string = self.custom_label
        else:
            label_string = "Released by " + self.album.getLabel().split(',')[0]

        # Use scaled font size
        font_size = self._scale_font(self._base_label_font_size)
        label_font = ImageFont.truetype('static/Oswald-Medium.ttf', font_size)
        ascent, descent = label_font.getmetrics()

        # Adjust wrap width based on scale to maintain similar appearance
        base_wrap_width = 20
        wrap_width = max(int(base_wrap_width / self.scale), 10) if self.scale < 1 else base_wrap_width
        label_list = textwrap.wrap(label_string, width=wrap_width)

        # Scale all vertical positions (310 and 90 are base values)
        current_y = self.below_pic_h + self._scale(310)
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

    def draw_color_squares(self, draw, album_img):
        colors = self.get_colors(album_img, 5, 250)
        
        square_size = self._scale(self._base_color_square_size)
        spacing = self._scale(self._base_color_square_spacing)

        offset = 0
        for color in colors:
            draw.rectangle([
                (self.width - self.margin - offset - square_size, self.below_pic_h), 
                (self.width - self.margin - offset, self.below_pic_h + square_size)
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
            'tracks': list(self.album.getTracks().values())[:30],
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