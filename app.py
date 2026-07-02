from src.album import Album
from src.helper import Utility, RESOLUTION_PRESETS, POSTER_STYLES, FONT_CHOICES, TEXTURES, ASPECT_PRESETS
from src.auto import AutoFill
from src.surprise import SurpriseMe
from src.collage import build_collage
from src.spotify_client import get_spotify
from src import top50
from flask import Flask, render_template, send_file, make_response, url_for, Response, redirect, request, jsonify, session, abort
import os
import re
import hashlib
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
import random
import base64
import json

# Google changes
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
import io
from dotenv import load_dotenv

load_dotenv(dotenv_path='keys.env')
DRIVE_FOLDER_ID = os.getenv('DRIVE_FOLDER_ID')


app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-prod')

# ── Feature flag: set to True to enable Posterfy-style poster variants ──
POSTERFY_ENABLED = True

autofill = AutoFill()

# ── Thumbnail cache: resizes images to small WebP on first request, then serves cached ──
THUMB_CACHE_DIR = os.path.join('static', 'thumbs')
os.makedirs(THUMB_CACHE_DIR, exist_ok=True)

# ── Gallery cache: Drive submissions proxied + resized to disk ──
GALLERY_CACHE_DIR = os.path.join('static', 'gallery_cache')
os.makedirs(GALLERY_CACHE_DIR, exist_ok=True)


# ── Shared helpers for poster routes ──

def _poster_options(src):
    """Extract style/font/texture/aspect from a form or JSON dict"""
    return {
        'style': src.get('style', 'classic') or 'classic',
        'font': src.get('font', 'oswald') or 'oswald',
        'texture': src.get('texture', 'none') or 'none',
        'aspect': src.get('aspect', 'poster') or 'poster',
    }


def _parse_offsets(raw):
    """Sanitize client-sent drag offsets: {'tracks': [dx, dy], ...} in base units"""
    out = {}
    if isinstance(raw, dict):
        for key, val in raw.items():
            if isinstance(val, (list, tuple)) and len(val) == 2:
                try:
                    dx, dy = float(val[0]), float(val[1])
                    # Clamp to one canvas in any direction
                    out[str(key)] = [max(-740, min(740, dx)), max(-1316, min(1316, dy))]
                except (TypeError, ValueError):
                    continue
    return out


def render_result_page(**kwargs):
    """Render result.html with safe defaults for every template variable"""
    defaults = dict(
        img_data=None, found=False,
        text_colors=['#000000'], background_colors=['#FFFFFF'],
        artist_name='', album_name='', album_id='',
        background_color='#FFFFFF', text_color='#000000',
        resolution_presets=RESOLUTION_PRESETS,
        num_tracks=0, tracks=[], release_date='', label='',
        musichoarders_url='', poster_style='classic',
        truncated_tracks=[],
        poster_font='oswald', poster_texture='none', poster_aspect='poster',
        font_choices=FONT_CHOICES, textures=TEXTURES, aspect_presets=ASPECT_PRESETS,
        element_boxes={}, spotify_type='album',
    )
    defaults.update(kwargs)
    return render_template("poster/result.html", **defaults)


@app.route("/thumb/<path:img_path>")
def serve_thumbnail(img_path):
    """Serve a small WebP thumbnail of any static image. Cached to disk."""
    width = request.args.get('w', 200, type=int)
    width = min(max(width, 50), 400)  # clamp between 50-400

    source = os.path.join('static', img_path)
    if not os.path.isfile(source):
        abort(404)

    # Cache key: hash of path + width
    cache_key = hashlib.md5(f"{img_path}:{width}".encode()).hexdigest()
    cached_path = os.path.join(THUMB_CACHE_DIR, f"{cache_key}.webp")

    if not os.path.isfile(cached_path):
        from PIL import Image
        try:
            img = Image.open(source)
            # Calculate proportional height (posters are 740:1200 ratio)
            ratio = img.height / img.width
            height = int(width * ratio)
            img = img.resize((width, height), Image.LANCZOS)
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            img.save(cached_path, 'WEBP', quality=75)
        except Exception:
            abort(500)

    response = send_file(cached_path, mimetype='image/webp')
    response.cache_control.max_age = 86400 * 30  # cache 30 days
    response.cache_control.public = True
    return response


def get_spotify_oauth():
    return SpotifyOAuth(
        scope='user-top-read',
        redirect_uri=os.getenv('SPOTIPY_REDIRECT_URI', 'http://127.0.0.1:5000/callback'),
        show_dialog=True,
        cache_handler=FlaskSessionCacheHandler(session)
    )

# Decorator for homepage
@app.route("/")
@app.route("/home")
def home():
    # Gather poster paths from all directories for the side-scroll
    scroll_posters = []
    # Legacy posters
    legacy_dir = 'static/posters_resized'
    if os.path.isdir(legacy_dir):
        scroll_posters += [f'posters_resized/{f}' for f in os.listdir(legacy_dir)
                           if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    # Generated posters from each style
    gen_dir = 'static/posters_generated'
    if os.path.isdir(gen_dir):
        for style in POSTER_STYLES:
            style_dir = os.path.join(gen_dir, style)
            if os.path.isdir(style_dir):
                scroll_posters += [f'posters_generated/{style}/{f}' for f in os.listdir(style_dir)
                                   if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    random.shuffle(scroll_posters)
    # Only need ~30 for the scroll effect
    scroll_posters = scroll_posters[:30]
    return render_template("home/index.html", posterfy_enabled=POSTERFY_ENABLED, scroll_posters=scroll_posters)


@app.route("/result", methods=['POST', 'GET'])
def result():
    output = request.form.to_dict()
    bcolor = output.get("background", None)
    tcolor = output.get("text", None)
    artist = output.get("artist", "")
    album_name = output.get("album", "")
    selected_album_id = output.get("album_id", "")
    item_type = output.get("spotify_type", "album")
    opts = _poster_options(output)

    # Fix for title saving as a spotify url
    artist_query = output.get("artist", "")
    album_query = output.get("album", "")
    # Use album_id from dropdown selection if available for exact match
    album = Album(artist, album_query,
                  album_id=selected_album_id if selected_album_id else None,
                  item_type=item_type)

    if album.album_found:
        artist = album.artist_name
        album_name = album.album_name
    else:
        artist = artist_query
        album_name = album_query

    if not album.album_found:
        return render_result_page(found=False, artist_name=artist, album_name=album_name)

    album.setColors(bcolor or '#FFFFFF', tcolor or '#000000')
    # Use medium resolution for preview
    utility = Utility(album, resolution='medium', **opts)
    poster = utility.buildPoster()
    img_data = utility.encodeImage(poster, format='WEBP')
    colors = utility.get_cover_colors(5)
    text_colors = ['#' + ''.join(['{:02x}'.format(int(c)) for c in color]) for color in reversed(colors)]

    return render_result_page(
        img_data=img_data,
        found=True,
        text_colors=text_colors,
        background_colors=text_colors,
        artist_name=artist,
        album_name=album_name,
        album_id=album.album_id,
        background_color=bcolor or '#FFFFFF',
        text_color=tcolor or '#000000',
        num_tracks=album.getNumTracks(),
        tracks=album.getTracks(),
        release_date=album.getReleaseDate(),
        label=album.getLabel(),
        musichoarders_url=album.getMusicHoardersUrl(),
        poster_style=utility.style,
        poster_font=utility.font,
        poster_texture=utility.texture,
        poster_aspect=utility.aspect,
        truncated_tracks=list(getattr(utility, 'truncated_tracks', set())),
        element_boxes=utility.get_normalized_boxes(),
        spotify_type=album.spotify_type,
    )


# ── Shareable poster links ──

@app.route("/p/<item_id>")
def share_poster(item_id):
    """Rebuild a poster entirely from URL params — a shareable permalink."""
    if not re.match(r'^[A-Za-z0-9]+$', item_id):
        abort(404)

    item_type = request.args.get('type', 'album')
    if item_type == 'playlist':
        album = Album('', f'https://open.spotify.com/playlist/{item_id}')
    else:
        album = Album('', '', album_id=item_id)

    if not album.album_found:
        return render_result_page(found=False)

    def _hex_param(name, default=None):
        val = request.args.get(name, '')
        val = val.lstrip('#')
        if re.match(r'^[0-9a-fA-F]{6}$', val):
            return f'#{val}'
        return default

    opts = _poster_options(request.args)
    utility = Utility(album, resolution='medium', **opts)

    bcolor = _hex_param('bg')
    tcolor = _hex_param('text')
    if not bcolor or not tcolor:
        # Auto-pick colors from the cover like Surprise Me does
        colors = utility.get_cover_colors(6)
        surprise = SurpriseMe()
        bg = colors[0]
        txt = surprise.find_contrasting_color(colors[1:], bg)
        bcolor = bcolor or f"#{bg[0]:02x}{bg[1]:02x}{bg[2]:02x}"
        tcolor = tcolor or f"#{txt[0]:02x}{txt[1]:02x}{txt[2]:02x}"

    album.setColors(bcolor, tcolor)
    utility.text_color = tcolor
    utility.background = bcolor
    poster = utility.buildPoster()
    img_data = utility.encodeImage(poster, format='WEBP')
    colors = utility.get_cover_colors(5)
    text_colors = ['#' + ''.join(['{:02x}'.format(int(c)) for c in color]) for color in reversed(colors)]

    return render_result_page(
        img_data=img_data,
        found=True,
        text_colors=text_colors,
        background_colors=text_colors,
        artist_name=album.artist_name,
        album_name=album.album_name,
        album_id=album.album_id,
        background_color=bcolor,
        text_color=tcolor,
        num_tracks=album.getNumTracks(),
        tracks=album.getTracks(),
        release_date=album.getReleaseDate(),
        label=album.getLabel(),
        musichoarders_url=album.getMusicHoardersUrl(),
        poster_style=utility.style,
        poster_font=utility.font,
        poster_texture=utility.texture,
        poster_aspect=utility.aspect,
        truncated_tracks=list(getattr(utility, 'truncated_tracks', set())),
        element_boxes=utility.get_normalized_boxes(),
        spotify_type=album.spotify_type,
    )


# ── Posterfy style picker ──

@app.route("/choose-style", methods=['POST'])
def choose_style():
    """Show all poster style variants for user to pick from"""
    if not POSTERFY_ENABLED:
        return redirect(url_for('result'), code=307)  # forward POST

    output = request.form.to_dict()
    artist = output.get("artist", "")
    album_name = output.get("album", "")
    album_id = output.get("album_id", "")
    item_type = output.get("spotify_type", "album")

    album = Album(artist, album_name, album_id=album_id if album_id else None,
                  item_type=item_type)
    if not album.album_found:
        # Fall back to result page which shows the error
        return render_result_page(found=False, artist_name=artist, album_name=album_name)

    return render_template("poster/choose_style.html",
                           artist_name=album.artist_name,
                           album_name=album.album_name,
                           album_id=album.album_id,
                           spotify_type=album.spotify_type,
                           styles=POSTER_STYLES)


@app.route("/generate-style-preview", methods=['POST'])
def generate_style_preview():
    """AJAX: generate a single poster style preview at low resolution"""
    data = request.json
    artist = data.get('artist', '')
    album_name = data.get('album_name', '')
    album_id = data.get('album_id', '')
    style = data.get('style', 'classic')
    item_type = data.get('type', 'album')

    album = Album(artist, album_name, album_id=album_id if album_id else None,
                  item_type=item_type)
    if not album.album_found:
        return jsonify({'error': 'Album not found'}), 404

    try:
        surprise = SurpriseMe()
        utility = Utility(album, resolution='low', style=style)
        colors = utility.get_cover_colors(6)

        bg_color = colors[0]
        txt_color = surprise.find_contrasting_color(colors[1:], bg_color)

        bg_hex = f"#{bg_color[0]:02x}{bg_color[1]:02x}{bg_color[2]:02x}"
        txt_hex = f"#{txt_color[0]:02x}{txt_color[1]:02x}{txt_color[2]:02x}"

        album.setColors(bg_hex, txt_hex)
        poster = utility.buildPoster()
        img_data = utility.encodeImage(poster, format='WEBP')

        return jsonify({
            'img_data': img_data,
            'background': bg_hex,
            'text': txt_hex,
            'style': style,
            'artist': album.artist_name,
            'album_name': album.album_name,
            'album_id': album.album_id,
        })
    except Exception as e:
        print(f"Style preview error ({style}): {e}")
        return jsonify({'error': str(e)}), 500


@app.route("/spotify-login")
def spotify_login():
    sp_oauth = get_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route("/callback")
def spotify_callback():
    sp_oauth = get_spotify_oauth()
    code = request.args.get('code')
    error = request.args.get('error')

    if error or not code:
        return redirect(url_for('home'))

    # get_access_token exchanges the code AND saves to FlaskSessionCacheHandler
    sp_oauth.get_access_token(code)
    return redirect(url_for('top_albums'))


@app.route("/logout")
def spotify_logout():
    session.pop('token_info', None)  # FlaskSessionCacheHandler uses 'token_info' key
    return redirect(url_for('home'))


@app.route("/my-top-albums")
def top_albums():
    sp_oauth = get_spotify_oauth()
    token_info = sp_oauth.validate_token(sp_oauth.cache_handler.get_cached_token())
    if not token_info:
        return redirect(url_for('spotify_login'))

    sp = Spotify(auth=token_info['access_token'])

    try:
        user_info = sp.current_user()
        display_name = user_info.get('display_name') or 'You'

        top_tracks = sp.current_user_top_tracks(limit=50, time_range='medium_term')
        albums = []
        seen = set()
        for item in top_tracks['items']:
            album_id = item['album']['id']
            if album_id not in seen:
                seen.add(album_id)
                images = item['album'].get('images') or []
                albums.append({
                    'id': album_id,
                    'name': item['album']['name'],
                    'artist': item['album']['artists'][0]['name'],
                    'image': images[0]['url'] if images else None,
                })
            if len(albums) >= 8:
                break

        # Fall back to long_term if not enough from medium_term
        if len(albums) < 8:
            top_albums_data = sp.current_user_top_tracks(limit=50, time_range='long_term')
            for item in top_albums_data['items']:
                album_id = item['album']['id']
                if album_id not in seen:
                    seen.add(album_id)
                    images = item['album'].get('images') or []
                    albums.append({
                        'id': album_id,
                        'name': item['album']['name'],
                        'artist': item['album']['artists'][0]['name'],
                        'image': images[0]['url'] if images else None,
                    })
                if len(albums) >= 8:
                    break

    except Exception as e:
        print(f"Spotify API error: {e}")
        return redirect(url_for('spotify_login'))

    return render_template('home/top_albums.html', albums=albums, display_name=display_name)


# ── Today's Top Albums: cached poster wall with background refresh ──

@app.route("/top-50")
def top50_page():
    manifest = top50.ensure_top50()
    status = top50.get_status()
    return render_template('home/top50.html', manifest=manifest, status=status)


@app.route("/top50-status")
def top50_status():
    return jsonify(top50.get_status())


@app.route("/top50-refresh", methods=["GET", "POST"])
def top50_refresh():
    """Force a regeneration — point a scheduler (e.g. Heroku Scheduler) here.
    Set TOP50_REFRESH_KEY to require ?key=... on this endpoint."""
    required_key = os.getenv('TOP50_REFRESH_KEY')
    if required_key and request.args.get('key') != required_key:
        abort(403)
    top50.ensure_top50(force=True)
    return jsonify({'started': True})


@app.route("/collage-poster", methods=["POST"])
def collage_poster():
    """Build a single collage poster from the user's top albums"""
    data = request.get_json(silent=True) or {}
    albums = data.get('albums') or []
    display_name = (data.get('display_name') or 'Your')[:40]

    # Sanitize: only keep expected fields, cap at 8
    clean = []
    for a in albums[:8]:
        if isinstance(a, dict) and a.get('image'):
            clean.append({
                'name': str(a.get('name', ''))[:80],
                'artist': str(a.get('artist', ''))[:80],
                'image': str(a.get('image', '')),
            })

    if not clean:
        return jsonify({'error': 'No albums provided'}), 400

    try:
        poster = build_collage(clean, display_name)
        buf = io.BytesIO()
        poster.save(buf, 'PNG')
        encoded = base64.b64encode(buf.getvalue()).decode('utf-8')
        return jsonify({
            'img_data': f"data:image/png;base64,{encoded}",
            'filename': f"{display_name.replace(' ', '_')}_top_albums.png",
        })
    except Exception as e:
        print(f"Collage error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route("/generate-album-poster", methods=["POST"])
def generate_album_poster():
    data = request.json
    artist = data.get('artist', '')
    album_name = data.get('album_name', '')
    album_id = data.get('album_id', '')

    album = Album(artist, album_name, album_id=album_id if album_id else None)
    if not album.album_found:
        return jsonify({'error': 'Album not found'}), 404

    try:
        surprise = SurpriseMe()
        utility = Utility(album, resolution='medium')
        colors = utility.get_cover_colors(6)

        background_color = colors[0]
        text_color = surprise.find_contrasting_color(colors[1:], background_color)

        background_hex = f"#{background_color[0]:02x}{background_color[1]:02x}{background_color[2]:02x}"
        text_hex = f"#{text_color[0]:02x}{text_color[1]:02x}{text_color[2]:02x}"

        album.setColors(background_hex, text_hex)
        poster = utility.buildPoster()
        img_data = utility.encodeImage(poster, format='WEBP')

        return jsonify({
            'img_data': img_data,
            'artist': album.artist_name,
            'album_name': album.album_name,
            'album_id': album.album_id,
            'background': background_hex,
            'text': text_hex,
        })
    except Exception as e:
        print(f"Poster generation error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route("/about")
def about():
    return render_template("about/about.html")


@app.route("/artist-suggestions")
def artist_suggestions():
    query = request.args.get('q', '')
    if not query or len(query) < 2:
        return jsonify([])
    artists = autofill.search_artists(query)
    return jsonify(artists)


@app.route("/album-suggestions")
def album_suggestions():
    artist_name = request.args.get('artist', '')
    query = request.args.get('q', '')
    if not query or len(query) < 2:
        return jsonify([])
    albums = autofill.search_albums(query, artist_name if artist_name else None)
    return jsonify(albums)


@app.route("/search-suggestions")
def search_suggestions():
    """Mixed album + playlist suggestions for the home search box"""
    query = request.args.get('q', '')
    if not query or len(query) < 2:
        return jsonify([])
    return jsonify(autofill.search_mixed(query))


@app.route("/link-preview")
def link_preview():
    """Resolve a pasted Spotify album/playlist link into a preview card"""
    url = request.args.get('q', '')
    match = re.search(r'open\.spotify\.com/(album|playlist)/([A-Za-z0-9]+)', url)
    if not match:
        return jsonify({'error': 'Not a Spotify album or playlist link'}), 400

    item_type, item_id = match.group(1), match.group(2)
    item = Album('', '', album_id=item_id, item_type=item_type)
    if not item.album_found:
        hint = ('Spotify-made playlists (like Top 50) are blocked from the API — '
                'try a user-created playlist.') if item_type == 'playlist' else ''
        return jsonify({'error': f'Could not load that {item_type}. {hint}'.strip()}), 404

    images = item.getCoverArt()
    return jsonify({
        'name': item.album_name,
        'artist': (f"Playlist · {item.artist_name}" if item.spotify_type == 'playlist'
                   else item.artist_name),
        'raw_artist': item.artist_name,
        'image': images[-1]['url'] if images else None,
        'album_id': item.album_id,
        'type': item.spotify_type,
    })


@app.route("/mosaic")
def mosaic():
    # Legacy posters
    legacy_posters = os.listdir('static/posters_resized')
    random.shuffle(legacy_posters)

    # Generated posters organized by style
    generated_dir = 'static/posters_generated'
    style_posters = {}
    for style in POSTER_STYLES:
        style_dir = os.path.join(generated_dir, style)
        if os.path.isdir(style_dir):
            files = [f for f in os.listdir(style_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            random.shuffle(files)
            style_posters[style] = files
        else:
            style_posters[style] = []

    return render_template('poster/mosaic.html',
                           legacy_posters=legacy_posters,
                           style_posters=style_posters,
                           styles=POSTER_STYLES)


@app.route("/update-poster", methods=['POST'])
def update_poster():
    data = request.json
    artist = data['artist']
    album_data = data['album']
    background_color = data['background']
    text_color = data['text']
    tabulated = data.get('tabulated', False)
    dotted = data.get('dotted', False)
    album_id = data.get('album_id', None)
    opts = _poster_options(data)

    album = Album(artist, album_data, album_id=album_id if album_id else None,
                  item_type=data.get('spotify_type', 'album'))
    album.setColors(background_color, text_color)
    album.setTracklistFormat(tabulated, dotted)

    # Use medium resolution for preview
    utility = Utility(album, resolution='medium', **opts)
    poster = utility.buildPoster()

    img_data = utility.encodeImage(poster, format='WEBP')
    return jsonify({'img_data': img_data})


@app.route("/update-poster-custom", methods=['POST'])
def update_poster_custom():
    """Update poster with custom text edits"""
    data = request.json
    artist = data['artist']
    album_data = data['album']
    background_color = data['background']
    text_color = data['text']
    tabulated = data.get('tabulated', False)
    dotted = data.get('dotted', False)
    opts = _poster_options(data)

    # Get custom text fields
    custom_artist = data.get('custom_artist', None)
    custom_album = data.get('custom_album', None)
    custom_tracks = data.get('custom_tracks', {})
    custom_date = data.get('custom_date', None)
    custom_label = data.get('custom_label', None)
    removed_tracks = set(data.get('removed_tracks', []))
    no_truncate_tracks = set(data.get('no_truncate_tracks', []))
    custom_cover_url = data.get('custom_cover_url', None)
    album_id = data.get('album_id', None)
    offsets = _parse_offsets(data.get('offsets', {}))

    # Instantiate Album object - use album_id if available to avoid re-search ambiguity
    album = Album(artist, album_data, album_id=album_id,
                  item_type=data.get('spotify_type', 'album'))

    if not album.album_found:
        return jsonify({'error': 'Album not found'}), 404

    # Override text fields if custom values provided (use 'is not None' to allow empty strings)
    if custom_artist is not None:
        album.artist_name = custom_artist
    if custom_album is not None:
        album.album_name = custom_album

    # Set colors and format
    album.setColors(background_color, text_color)
    album.setTracklistFormat(tabulated, dotted)

    # Set custom cover if provided (and not empty)
    if custom_cover_url and len(custom_cover_url.strip()) > 0:
        album.setCustomCover(custom_cover_url.strip())

    # Build poster with custom utility that supports text overrides
    utility = Utility(album, **opts)
    utility.custom_artist = custom_artist
    utility.custom_album = custom_album
    utility.custom_tracks = custom_tracks
    utility.custom_date = custom_date
    utility.custom_label = custom_label
    utility.removed_tracks = removed_tracks
    utility.no_truncate_tracks = no_truncate_tracks
    utility.element_offsets = offsets

    poster = utility.buildPoster()
    img_data = utility.encodeImage(poster, format='WEBP')

    # Extract colors from the current album cover (cached per cover URL)
    colors = utility.get_cover_colors(5)
    hex_colors = ['#' + ''.join(['{:02x}'.format(int(c)) for c in color]) for color in reversed(colors)]

    return jsonify({
        'img_data': img_data,
        'colors': hex_colors,
        'truncated_tracks': list(getattr(utility, 'truncated_tracks', set())),
        'boxes': utility.get_normalized_boxes(),
    })


@app.route("/download-poster", methods=['POST'])
def download_poster():
    """Generate and return poster for download at specified resolution/format"""
    data = request.json
    artist = data.get('artist')
    album_data = data.get('album')
    background_color = data.get('background', '#FFFFFF')
    text_color = data.get('text', '#000000')
    tabulated = data.get('tabulated', False)
    dotted = data.get('dotted', False)
    resolution = data.get('resolution', 'high')
    format_type = data.get('format', 'png')
    dpi = data.get('dpi', 300)
    opts = _poster_options(data)

    # Validate resolution
    if resolution not in RESOLUTION_PRESETS:
        resolution = 'high'

    # Validate DPI
    try:
        dpi = int(dpi)
        dpi = max(72, min(600, dpi))
    except:
        dpi = 300

    # Get custom cover, removed tracks, and truncation overrides
    custom_cover_url = data.get('custom_cover_url', None)
    removed_tracks = set(data.get('removed_tracks', []))
    no_truncate_tracks = set(data.get('no_truncate_tracks', []))
    album_id = data.get('album_id', None)
    offsets = _parse_offsets(data.get('offsets', {}))

    album = Album(artist, album_data, album_id=album_id,
                  item_type=data.get('spotify_type', 'album'))

    if not album.album_found:
        return jsonify({'error': 'Album not found'}), 404

    # Set custom cover if provided (and not empty)
    if custom_cover_url and len(custom_cover_url.strip()) > 0:
        album.setCustomCover(custom_cover_url.strip())

    album.setColors(background_color, text_color)
    album.setTracklistFormat(tabulated, dotted)

    utility = Utility(album, resolution=resolution, **opts)
    utility.removed_tracks = removed_tracks
    utility.no_truncate_tracks = no_truncate_tracks
    utility.element_offsets = offsets

    # Apply the same custom text overrides the preview uses
    if data.get('custom_artist') is not None:
        utility.custom_artist = data['custom_artist']
        album.artist_name = data['custom_artist']
    if data.get('custom_album') is not None:
        utility.custom_album = data['custom_album']
        album.album_name = data['custom_album']
    utility.custom_tracks = data.get('custom_tracks', {})
    utility.custom_date = data.get('custom_date', None)
    utility.custom_label = data.get('custom_label', None)

    if format_type.lower() == 'svg':
        svg_content = utility.generateSVG()
        return jsonify({
            'type': 'svg',
            'data': svg_content,
            'filename': f"{album.album_name.replace(' ', '_')}_{utility.style}_{resolution}.svg"
        })
    else:
        poster = utility.buildPoster()
        img_bytes = utility.getImageBytes(poster, format='PNG', dpi=dpi)

        encoded = base64.b64encode(img_bytes.getvalue()).decode('utf-8')

        return jsonify({
            'type': 'png',
            'data': f"data:image/png;base64,{encoded}",
            'filename': f"{album.album_name.replace(' ', '_')}_{utility.style}_{resolution}_{dpi}dpi.png",
            'width': utility.width,
            'height': utility.height
        })


@app.route("/surprise", methods=["GET"])
def surprise():
    surprise_me = SurpriseMe()

    # When Posterfy styles enabled, go through style picker
    if POSTERFY_ENABLED:
        artist_name, album_name = surprise_me.get_random_album()
        album = Album(artist_name, album_name)
        if album.album_found:
            return render_template("poster/choose_style.html",
                                   artist_name=album.artist_name,
                                   album_name=album.album_name,
                                   album_id=album.album_id,
                                   styles=POSTER_STYLES)

    # Fallback / POSTERFY_ENABLED=False: generate classic poster directly
    img_data, album_name, artist_name, background_color, text_color = surprise_me.generate_random_poster()

    if img_data:
        album = Album(artist_name, album_name)
        utility = Utility(album)
        colors = utility.get_cover_colors(5)
        text_colors = ['#' + ''.join(['{:02x}'.format(int(c)) for c in color]) for color in reversed(colors)]

        return render_result_page(
            img_data=img_data,
            found=True,
            artist_name=artist_name,
            album_name=album_name,
            album_id=album.album_id,
            background_colors=text_colors,
            text_colors=text_colors,
            background_color=background_color,
            text_color=text_color,
            num_tracks=album.getNumTracks(),
            tracks=album.getTracks(),
            release_date=album.getReleaseDate(),
            label=album.getLabel(),
            musichoarders_url=album.getMusicHoardersUrl(),
        )
    else:
        return render_result_page(found=False)


# Authenticate using the service account
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
base64_creds = os.getenv("GOOGLE_SERVICE_ACCOUNT_BASE64")

if base64_creds:
    creds_json = base64.b64decode(base64_creds).decode("utf-8")
    creds_dict = json.loads(creds_json)

    credentials = service_account.Credentials.from_service_account_info(
        creds_dict, scopes=SCOPES
    )
else:
    raise Exception("GOOGLE_SERVICE_ACCOUNT_BASE64 environment variable not set!")

drive_service = build("drive", "v3", credentials=credentials)


def upload_poster_to_drive(img_data, artist_name, album_name, style='classic'):
    """Uploads a poster image to Google Drive and returns the file link"""
    try:
        header, b64_payload = img_data.split(",", 1)
        img_bytes = base64.b64decode(b64_payload)
        img_stream = io.BytesIO(img_bytes)

        # Previews may be WebP now — keep the mimetype/extension honest
        mime_match = re.match(r'data:([^;]+);', header)
        mimetype = mime_match.group(1) if mime_match else "image/png"
        ext = 'webp' if 'webp' in mimetype else 'png'

        file_name = f"{artist_name}_{album_name}_{style}.{ext}".replace(" ", "_")
        file_metadata = {
            "name": file_name,
            "parents": [DRIVE_FOLDER_ID]
        }

        media = MediaIoBaseUpload(img_stream, mimetype=mimetype)
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
        ).execute()

        file_id = file.get("id")
        file_link = f"https://drive.google.com/file/d/{file_id}/view"

        return file_link

    except Exception as e:
        print("Error uploading to Google Drive:", e)
        return None


@app.route("/submit-poster", methods=["POST"])
def submit_poster():
    try:
        data = request.get_json(silent=True) or {}
        img_data = data.get("img_data")
        artist_name = data.get("artist_name")
        album_name = data.get("album_name")
        poster_style = data.get("style", "classic")

        print(f"Received Data in /submit-poster:")
        print(f"   - img_data: {'Yes' if img_data else 'No'}")
        print(f"   - artist_name: {artist_name}")
        print(f"   - album_name: {album_name}")

        if not img_data or not artist_name or not album_name:
            print("Missing data in request")
            return jsonify({"success": False, "message": "Missing data"}), 400

        file_link = upload_poster_to_drive(img_data, artist_name, album_name, style=poster_style)

        if file_link:
            return jsonify({
                "success": True,
                "message": "Poster uploaded successfully!"
            })
        else:
            print("Google Drive upload failed")
            return jsonify({"success": False, "message": "Upload failed"}), 500

    except Exception as e:
        print(f"Error in /submit-poster: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


# ── Community gallery: submissions straight from the Drive folder ──

@app.route("/gallery")
def gallery():
    try:
        results = drive_service.files().list(
            q=f"'{DRIVE_FOLDER_ID}' in parents and trashed=false and mimeType contains 'image/'",
            fields="files(id, name, createdTime)",
            orderBy="createdTime desc",
            pageSize=60,
        ).execute()
        files = results.get('files', [])
    except Exception as e:
        print(f"Gallery listing error: {e}")
        files = []

    return render_template('poster/gallery.html', files=files)


@app.route("/gallery-image/<file_id>")
def gallery_image(file_id):
    """Proxy a Drive submission through the service account, cached to disk."""
    if not re.match(r'^[A-Za-z0-9_-]+$', file_id):
        abort(404)

    width = request.args.get('w', 0, type=int)
    width = min(max(width, 0), 800)

    original_path = os.path.join(GALLERY_CACHE_DIR, f"{file_id}.bin")
    if not os.path.isfile(original_path):
        try:
            # Confirm the file actually lives in the submissions folder
            meta = drive_service.files().get(fileId=file_id, fields="parents").execute()
            if DRIVE_FOLDER_ID not in (meta.get('parents') or []):
                abort(404)

            request_media = drive_service.files().get_media(fileId=file_id)
            buf = io.BytesIO()
            downloader = MediaIoBaseDownload(buf, request_media)
            done = False
            while not done:
                _, done = downloader.next_chunk()
            with open(original_path, 'wb') as f:
                f.write(buf.getvalue())
        except Exception as e:
            print(f"Gallery image fetch error: {e}")
            abort(404)

    serve_path = original_path
    mimetype = 'image/png'
    if width:
        resized_path = os.path.join(GALLERY_CACHE_DIR, f"{file_id}_{width}.webp")
        if not os.path.isfile(resized_path):
            from PIL import Image
            try:
                img = Image.open(original_path)
                ratio = img.height / img.width
                img = img.resize((width, int(width * ratio)), Image.LANCZOS)
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                img.save(resized_path, 'WEBP', quality=78)
            except Exception as e:
                print(f"Gallery resize error: {e}")
                abort(500)
        serve_path = resized_path
        mimetype = 'image/webp'

    response = send_file(serve_path, mimetype=mimetype)
    response.cache_control.max_age = 86400 * 7
    response.cache_control.public = True
    return response


if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
