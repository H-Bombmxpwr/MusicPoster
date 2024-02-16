from src.album import Album
from src.helper import Utility
from src.auto import AutoFill
from flask import Flask, render_template, send_file, make_response, url_for, Response, redirect, request,jsonify
import os

app = Flask(__name__)

#decorator for homepage 
@app.route("/")
@app.route("/home")
def home():
    return render_template("home/index.html")


@app.route("/result", methods = ['POST','GET'])
def result():
    output = request.form.to_dict()
    bcolor = output["background"]
    tcolor = output["text"]
    artist = output["artist"]
    album = output["album"]
    album = Album(artist,album)
    img_data = None
    if album.album_found: #only build the poster if the album was found, otherwise just pass the error message
        album.setColors(bcolor,tcolor)
        utility = Utility(album)
        poster = utility.buildPoster()
        img_data = Utility(album).encodeImage(poster)
        album_img = utility.fetch_album_cover(album.getCoverArt()[0]['url'])
        colors = utility.get_colors(album_img, 5)  # Adjust number of colors as needed
        # For simplicity, using the same colors for both. Adjust based on your requirements
    # Discard the first color and convert the rest to hex
    text_colors = ['#' + ''.join(['{:02x}'.format(int(c)) for c in color]) for color in reversed(colors)]


    return render_template("poster/result.html", 
                           img_data=img_data, 
                           found=album.album_found, 
                           text_colors=text_colors, 
                           background_colors=text_colors, 
                           artist_name=artist, 
                           album_name=album.album_name,
                           background_color=bcolor,
                           text_color=tcolor)
    
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
    return render_template('poster/mosaic.html', posters=posters)

@app.route("/update-poster", methods=['POST'])
def update_poster():
    data = request.json
    artist = data['artist']
    album_data = data['album']
    new_color = data['color']
    is_background = data['is_background']
    background_color = data['background']  # Provided from the AJAX call
    text_color = data['text']  # Provided from the AJAX call

    # Instantiate your Album object
    album = Album(artist, album_data)

    # Update the colors based on the provided data
    if is_background:
        background_color = new_color
    else:
        text_color = new_color
    # Assuming setColors is a method that updates colors of the Album instance
    album.setColors(background_color, text_color)

    # Rebuild the poster with the new colors
    utility = Utility(album)
    poster = utility.buildPoster()
    
    img_data = utility.encodeImage(poster)
    return jsonify({'img_data': img_data})


if __name__ == '__main__':
    app.run(debug = True, host = "0.0.0.0",port = 80)