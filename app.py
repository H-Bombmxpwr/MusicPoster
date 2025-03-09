from src.album import Album
from src.helper import Utility
from src.auto import AutoFill
from src.surprise import SurpriseMe
from src.infinity import InfinityPoster
from flask import Flask, render_template, send_file, make_response, url_for, Response, redirect, request,jsonify
import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import random
import base64
import json

#google changes 
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
from dotenv import load_dotenv

load_dotenv(dotenv_path='keys.env')
DRIVE_FOLDER_ID = os.getenv('DRIVE_FOLDER_ID')



app = Flask(__name__)

#decorator for homepage 
@app.route("/")
@app.route("/home")
def home():
    return render_template("home/index.html")


@app.route("/result", methods = ['POST','GET'])
def result():
    output = request.form.to_dict()
    bcolor = output.get("background", None)
    tcolor = output.get("text", None)
    artist = output.get("artist", "")
    album_name = output.get("album", "")

    #nonsense to fix the title savign as a spotify url
    artist_query = output.get("artist", "")  # May be empty
    album_query = output.get("album", "")  # May still be a URL
    album = Album(artist, album_query)  # Album class fetches real name
    if album.album_found:
        artist = album.artist_name  # ✅ Fix: Use the artist name from Spotify API
        album_name = album.album_name  # ✅ Fix: Use correct album name
    else:
        artist = artist_query  # Keep input if album fetch fails
        album_name = album_query  # Keep input if album fetch fails

    img_data = None
    text_colors = None
    album_img = None
    album_found = album.album_found

    if album_found:  # only build the poster if the album was found, otherwise just pass the error message
        album.setColors(bcolor, tcolor)
        utility = Utility(album)
        poster = utility.buildPoster()
        img_data = utility.encodeImage(poster)
        album_img = utility.fetch_album_cover(album.getCoverArt()[0]['url'])
        colors = utility.get_colors(album_img, 5)  # Adjust number of colors as needed
        # Discard the first color and convert the rest to hex
        text_colors = ['#' + ''.join(['{:02x}'.format(int(c)) for c in color]) for color in reversed(colors)]

    # Prepare variables for rendering; if not found, these will remain None or use defaults
    return render_template("poster/result.html", 
                           img_data=img_data, 
                           found=album_found, 
                           text_colors=text_colors or ['#000000'],  # Provide a default color if not found
                           background_colors=text_colors or ['#FFFFFF'],  # Provide a default color if not found
                           artist_name=artist, 
                           album_name=album_name,
                           background_color=bcolor or '#FFFFFF',  # Provide a default background color
                           text_color=tcolor or '#000000')  # Provide a default text color

    
@app.route("/about")
def about():
    return render_template("about/about.html")


@app.route("/artist-suggestions")
def artist_suggestions():
    query = request.args.get('q', '')
    autofill = AutoFill()
    artists = autofill.search_artists(query)
    return jsonify(artists)

@app.route("/album-suggestions")
def album_suggestions():
    artist_name = request.args.get('artist', '')
    query = request.args.get('q', '')
    autofill = AutoFill()
    albums = autofill.search_albums(query,artist_name)
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
    background_color = data['background']  # Provided from the AJAX call
    text_color = data['text']  # Provided from the AJAX call
    tabulated = data['tabulated']
    dotted = data['dotted']

    # Instantiate your Album object
    album = Album(artist, album_data)


    # Assuming setColors is a method that updates colors of the Album instance
    album.setColors(background_color, text_color)

    # Update the tracklist format
    album.setTracklistFormat(tabulated, dotted)
    
    # Rebuild the poster with the new colors
    utility = Utility(album)
    poster = utility.buildPoster()
    
    img_data = utility.encodeImage(poster)
    return jsonify({'img_data': img_data})


@app.route("/surprise", methods=["GET"])
def surprise():
    surprise_me = SurpriseMe()
    img_data, album_name, artist_name = surprise_me.generate_random_poster()

    if img_data:
        # Recalculate dominant colors for the album art
        album = Album(artist_name, album_name)
        utility = Utility(album)
        album_img = utility.fetch_album_cover(album.getCoverArt()[0]['url'])
        colors = utility.get_colors(album_img, 5)  # Extract 5 colors from album art
        text_colors = ['#' + ''.join(['{:02x}'.format(int(c)) for c in color]) for color in reversed(colors)]
        background_colors = text_colors  # Use the same colors for background options

        return render_template(
            "poster/result.html",
            img_data=img_data,
            found=True,
            artist_name=artist_name,
            album_name=album_name,
            background_colors=background_colors,  # Pass background colors
            text_colors=text_colors,  # Pass text colors
            background_color="#FFFFFF",  # Default background color
            text_color="#000000",  # Default text color
        )
    else:
        return render_template(
            "poster/result.html",
            found=False,
            error_message="Could not generate a random poster. Please try again.",
        )
    

@app.route("/api/generate-posters", methods=['GET'])
def generate_posters_api():
    infinity = InfinityPoster()
    posters = infinity.generate_posters(limit=5)  # Generate 5 posters per API call
    return jsonify(posters)

# Authenticate using the service account
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
# Load from environment variable
base64_creds = os.getenv("GOOGLE_SERVICE_ACCOUNT_BASE64")

if base64_creds:
    creds_json = base64.b64decode(base64_creds).decode("utf-8")
    creds_dict = json.loads(creds_json)  # Convert to dictionary

    credentials = service_account.Credentials.from_service_account_info(
        creds_dict, scopes=SCOPES
    )
else:
    raise Exception("❌ GOOGLE_SERVICE_ACCOUNT_BASE64 environment variable not set!")

drive_service = build("drive", "v3", credentials=credentials)

def upload_poster_to_drive(img_data, artist_name, album_name):
    """ Uploads a poster image to Google Drive and returns the file link """
    try:
        # Decode base64 image
        img_bytes = base64.b64decode(img_data.split(",")[1])  # Remove 'data:image/png;base64,' prefix
        img_stream = io.BytesIO(img_bytes)

        # Define file metadata
        file_name = f"{artist_name}_{album_name}.png".replace(" ", "_")
        file_metadata = {
            "name": file_name,
            "parents": [DRIVE_FOLDER_ID]
        }

        # Upload file to Google Drive
        media = MediaIoBaseUpload(img_stream, mimetype="image/png")
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
        ).execute()

        # Get shareable link
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

        print(f"🔍 Received Data in /submit-poster:")
        print(f"   - img_data: {'Yes' if img_data else 'No'}")
        print(f"   - artist_name: {artist_name}")
        print(f"   - album_name: {album_name}")

        if not img_data or not artist_name or not album_name:
            print("🚨 Missing data in request")
            return jsonify({"success": False, "message": "Missing data"}), 400

        # Upload poster to Google Drive
        file_link = upload_poster_to_drive(img_data, artist_name, album_name)

        if file_link:
            return jsonify({
                "success": True,
                "message": "Poster uploaded successfully!"
            })
        else:
            print("🚨 Google Drive upload failed")
            return jsonify({"success": False, "message": "Upload failed"}), 500

    except Exception as e:
        print(f"Error in /submit-poster: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


# if __name__ == '__main__':
#     app.run(debug = True, host = "0.0.0.0",port = 80)

if __name__ == '__main__':
    import os
    port = int(os.getenv("PORT", 5000))  # Use PORT from Railway or default to 5000
    app.run(debug=False, host='0.0.0.0', port=port)
