import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
import datetime
import re
from flask import Flask, request, jsonify


load_dotenv(dotenv_path='keys.env')
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')



client_credentials_manager = SpotifyClientCredentials(
            SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(
            client_credentials_manager=client_credentials_manager)


def search_artists():
    query = request.args.get('q', '')
    results = sp.search(q=query, type='artist', limit=5)
    artists = results['artists']['items']
    artist_names = [artist['name'] for artist in artists]
    return jsonify(artist_names)