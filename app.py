from src.album import Album
from src.helper import Utility
from flask import Flask, render_template, send_file, make_response, url_for, Response, redirect, request 

app = Flask(__name__)

#decorator for homepage 
@app.route("/")
@app.route("/home")
def home():
    return render_template("poster/index.html")


@app.route("/result", methods = ['POST','GET'])
def result():
    output = request.form.to_dict()
    artist = output["artist"]
    album = output["album"]
    bcolor = output["background"]
    tcolor = output["text"]
    album = Album(artist,album)
    album.setColors(bcolor,tcolor)
    poster = Utility(album).buildPoster()
    img_data = Utility(album).encodeImage(poster)
    return render_template("poster/index.html", img_data=img_data)
    


if __name__ == '__main__':
    app.run(debug = True, host = "0.0.0.0",port = 80)