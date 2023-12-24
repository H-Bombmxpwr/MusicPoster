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
        poster = Utility(album).buildPoster()
        img_data = Utility(album).encodeImage(poster)
    return render_template("poster/result.html", img_data=img_data, found=album.album_found)
    
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

if __name__ == '__main__':
    app.run(debug = True, host = "0.0.0.0",port = 80)