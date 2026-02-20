from src.album import Album
from src.helper import Utility, RESOLUTION_PRESETS
from src.auto import AutoFill
from src.surprise import SurpriseMe
from flask import Flask, render_template, send_file, make_response, url_for, Response, redirect, request, jsonify
import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import random
import base64
import json

# Google changes 
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
from dotenv import load_dotenv

load_dotenv(dotenv_path='keys.env')
DRIVE_FOLDER_ID = os.getenv('DRIVE_FOLDER_ID')


app = Flask(__name__)

autofill = AutoFill()

# Decorator for homepage 
@app.route("/")
@app.route("/home")
def home():
    return render_template("home/index.html")


@app.route("/result", methods=['POST', 'GET'])
def result():
    output = request.form.to_dict()
    bcolor = output.get("background", None)
    tcolor = output.get("text", None)
    artist = output.get("artist", "")
    album_name = output.get("album", "")
    selected_album_id = output.get("album_id", "")

    # Fix for title saving as a spotify url
    artist_query = output.get("artist", "")
    album_query = output.get("album", "")
    # Use album_id from dropdown selection if available for exact match
    album = Album(artist, album_query, album_id=selected_album_id if selected_album_id else None)
    
    if album.album_found:
        artist = album.artist_name
        album_name = album.album_name
    else:
        artist = artist_query
        album_name = album_query

    img_data = None
    text_colors = None
    album_img = None
    album_found = album.album_found
    num_tracks = 0
    tracks_dict = []
    release_date = ""
    label = ""

    if album_found:
        album.setColors(bcolor or '#FFFFFF', tcolor or '#000000')
        # Use medium resolution for preview
        utility = Utility(album, resolution='medium')
        poster = utility.buildPoster()
        img_data = utility.encodeImage(poster)
        album_img = utility.fetch_album_cover(album.getCoverArt()[0]['url'])
        colors = utility.get_colors(album_img, 5)
        text_colors = ['#' + ''.join(['{:02x}'.format(int(c)) for c in color]) for color in reversed(colors)]
        
        # Get additional data for pre-filling edit fields
        num_tracks = album.getNumTracks()
        tracks_dict = album.getTracks()
        release_date = album.getReleaseDate()
        label = album.getLabel()
        musichoarders_url = album.getMusicHoardersUrl()

    return render_template("poster/result.html",
                           img_data=img_data,
                           found=album_found,
                           text_colors=text_colors or ['#000000'],
                           background_colors=text_colors or ['#FFFFFF'],
                           artist_name=artist,
                           album_name=album_name,
                           album_id=album.album_id if album_found else '',
                           background_color=bcolor or '#FFFFFF',
                           text_color=tcolor or '#000000',
                           resolution_presets=RESOLUTION_PRESETS,
                           num_tracks=num_tracks,
                           tracks=tracks_dict,
                           release_date=release_date,
                           label=label,
                           musichoarders_url=musichoarders_url if album_found else '')

    
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


@app.route("/mosaic")
def mosaic():
    posters = os.listdir('static/posters_resized')
    random.shuffle(posters)
    return render_template('poster/mosaic.html', posters=posters)


@app.route("/update-poster", methods=['POST'])
def update_poster():
    data = request.json
    artist = data['artist']
    album_data = data['album']
    background_color = data['background']
    text_color = data['text']
    tabulated = data.get('tabulated', False)
    dotted = data.get('dotted', False)

    album = Album(artist, album_data)
    album.setColors(background_color, text_color)
    album.setTracklistFormat(tabulated, dotted)
    
    # Use medium resolution for preview
    utility = Utility(album, resolution='medium')
    poster = utility.buildPoster()
    
    img_data = utility.encodeImage(poster)
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
    
    # Get custom text fields
    custom_artist = data.get('custom_artist', None)
    custom_album = data.get('custom_album', None)
    custom_tracks = data.get('custom_tracks', {})
    custom_date = data.get('custom_date', None)
    custom_label = data.get('custom_label', None)
    removed_tracks = set(data.get('removed_tracks', []))
    custom_cover_url = data.get('custom_cover_url', None)
    album_id = data.get('album_id', None)

    # Instantiate Album object - use album_id if available to avoid re-search ambiguity
    album = Album(artist, album_data, album_id=album_id)
    
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
    utility = Utility(album)
    utility.custom_artist = custom_artist
    utility.custom_album = custom_album
    utility.custom_tracks = custom_tracks
    utility.custom_date = custom_date
    utility.custom_label = custom_label
    utility.removed_tracks = removed_tracks
    
    poster = utility.buildPoster()
    img_data = utility.encodeImage(poster)

    # Extract colors from the current album cover (including custom cover)
    cover_url = album.getCoverArt()[0]['url']
    fallback_url = album.getSpotifyCoverUrl()
    album_img = utility.fetch_album_cover(cover_url, fallback_url=fallback_url)
    colors = utility.get_colors(album_img, 5)
    hex_colors = ['#' + ''.join(['{:02x}'.format(int(c)) for c in color]) for color in reversed(colors)]

    return jsonify({
        'img_data': img_data,
        'colors': hex_colors
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

    # Validate resolution
    if resolution not in RESOLUTION_PRESETS:
        resolution = 'high'
    
    # Validate DPI
    try:
        dpi = int(dpi)
        dpi = max(72, min(600, dpi))
    except:
        dpi = 300

    # Get custom cover and removed tracks
    custom_cover_url = data.get('custom_cover_url', None)
    removed_tracks = set(data.get('removed_tracks', []))
    album_id = data.get('album_id', None)

    album = Album(artist, album_data, album_id=album_id)

    if not album.album_found:
        return jsonify({'error': 'Album not found'}), 404

    # Set custom cover if provided (and not empty)
    if custom_cover_url and len(custom_cover_url.strip()) > 0:
        album.setCustomCover(custom_cover_url.strip())

    album.setColors(background_color, text_color)
    album.setTracklistFormat(tabulated, dotted)

    utility = Utility(album, resolution=resolution)
    utility.removed_tracks = removed_tracks
    
    if format_type.lower() == 'svg':
        svg_content = utility.generateSVG()
        return jsonify({
            'type': 'svg',
            'data': svg_content,
            'filename': f"{album.album_name.replace(' ', '_')}_{resolution}.svg"
        })
    else:
        poster = utility.buildPoster()
        img_bytes = utility.getImageBytes(poster, format='PNG', dpi=dpi)
        
        encoded = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
        
        return jsonify({
            'type': 'png',
            'data': f"data:image/png;base64,{encoded}",
            'filename': f"{album.album_name.replace(' ', '_')}_{resolution}_{dpi}dpi.png",
            'width': RESOLUTION_PRESETS[resolution]['width'],
            'height': RESOLUTION_PRESETS[resolution]['height']
        })


@app.route("/surprise", methods=["GET"])
def surprise():
    surprise_me = SurpriseMe()
    # Now returns 5 values including the actual colors used
    img_data, album_name, artist_name, background_color, text_color = surprise_me.generate_random_poster()

    if img_data:
        # Recalculate dominant colors for the color picker options
        album = Album(artist_name, album_name)
        utility = Utility(album)
        album_img = utility.fetch_album_cover(album.getCoverArt()[0]['url'])
        colors = utility.get_colors(album_img, 5)
        text_colors = ['#' + ''.join(['{:02x}'.format(int(c)) for c in color]) for color in reversed(colors)]
        background_colors = text_colors
        
        # Get additional data for pre-filling edit fields
        num_tracks = album.getNumTracks()
        tracks_dict = album.getTracks()
        release_date = album.getReleaseDate()
        label = album.getLabel()
        musichoarders_url = album.getMusicHoardersUrl()

        return render_template(
            "poster/result.html",
            img_data=img_data,
            found=True,
            artist_name=artist_name,
            album_name=album_name,
            album_id=album.album_id,
            background_colors=background_colors,
            text_colors=text_colors,
            # Use the ACTUAL colors from the generated poster, not defaults
            background_color=background_color,
            text_color=text_color,
            num_tracks=num_tracks,
            tracks=tracks_dict,
            release_date=release_date,
            label=label,
            musichoarders_url=musichoarders_url,
        )
    else:
        return render_template(
            "poster/result.html",
            found=False,
            error_message="Could not generate a random poster. Please try again.",
        )
    

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


def upload_poster_to_drive(img_data, artist_name, album_name):
    """Uploads a poster image to Google Drive and returns the file link"""
    try:
        img_bytes = base64.b64decode(img_data.split(",")[1])
        img_stream = io.BytesIO(img_bytes)

        file_name = f"{artist_name}_{album_name}.png".replace(" ", "_")
        file_metadata = {
            "name": file_name,
            "parents": [DRIVE_FOLDER_ID]
        }

        media = MediaIoBaseUpload(img_stream, mimetype="image/png")
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
        img_data = request.form.get("img_data")
        artist_name = request.form.get("artist_name")
        album_name = request.form.get("album_name")

        print(f"Received Data in /submit-poster:")
        print(f"   - img_data: {'Yes' if img_data else 'No'}")
        print(f"   - artist_name: {artist_name}")
        print(f"   - album_name: {album_name}")

        if not img_data or not artist_name or not album_name:
            print("Missing data in request")
            return jsonify({"success": False, "message": "Missing data"}), 400

        file_link = upload_poster_to_drive(img_data, artist_name, album_name)

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


if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)