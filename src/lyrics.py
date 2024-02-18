import os
import requests
import random
from dotenv import load_dotenv

# Load Musixmatch API Key from environment variable
load_dotenv(dotenv_path='keys.env')
# MUSIXMATCH_API = os.getenv("MUSIXMATCH_API")
MUSIXMATCH_API = 'af876107ed6e73a65ea28ccbae408427'
print("key")
print(MUSIXMATCH_API)

def search_album_tracks(artist: str, album: str):
    """
    Search for tracks in an album by a given artist.
    """
    print(f"Searching for tracks by {artist} in the album {album}.")
    endpoint = f"http://api.musixmatch.com/ws/1.1/album.tracks.get"
    params = {
        "q_artist": artist,
        "q_album": album,
        "apikey": MUSIXMATCH_API,
    }
    response = requests.get(endpoint, params=params)
    response.raise_for_status()  # Will raise an error for bad status codes
    album_data = response.json()
    track_list = album_data["message"]["body"]["track_list"]
    if not track_list:
        print("No tracks found in album.")
    return track_list

def get_lyrics(track_id):
    """
    Get lyrics for a track by its Musixmatch track ID.
    """
    print(f"Retrieving lyrics for track ID: {track_id}.")
    endpoint = f"http://api.musixmatch.com/ws/1.1/track.lyrics.get"
    params = {
        "track_id": track_id,
        "apikey": MUSIXMATCH_API,
    }
    response = requests.get(endpoint, params=params)
    response.raise_for_status()
    lyrics_data = response.json()
    if not lyrics_data["message"]["body"]:
        print("No lyrics found for track.")
    lyrics = lyrics_data["message"]["body"]["lyrics"]["lyrics_body"]
    return lyrics

def select_random_lines(lyrics: str, num_lines: int = 4):
    """
    Select a random sequence of consecutive lines from the lyrics.
    """
    print("Selecting random lines from the lyrics.")
    lines = lyrics.strip().split("\n")
    if len(lines) < num_lines:
        print("Not enough lines to select from.")
        return None  # Not enough lines to extract the desired number of lines
    start_index = random.randint(0, len(lines) - num_lines)
    return "\n".join(lines[start_index:start_index + num_lines])

def get_popular_lines_from_album(artist: str, album: str):
    """
    Get the most popular lines from a random song in the album.
    """
    print(f"Getting popular lines from the album {album} by {artist}.")
    try:
        tracks = search_album_tracks(artist, album)
        if not tracks:
            raise ValueError("No tracks found for this album.")
        print(f"Tracks found: {tracks}")  # Debugging line
        random_track = random.choice(tracks)  # Pick a random track from the album
        print(f"Selected track: {random_track}")  # Debugging line
        track_id = random_track["track"]["track_id"]
        lyrics = get_lyrics(track_id)
        if not lyrics:
            raise ValueError("No lyrics found for this track.")
        selected_lines = select_random_lines(lyrics)
        if not selected_lines:
            raise ValueError("Couldn't select random lines from the lyrics.")
        return selected_lines
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Example usage:
artist_name = "steely dan"  # Replace with actual artist name
album_name = "aja"  # Replace with actual album name
popular_lines = get_popular_lines_from_album(artist_name, album_name)
if popular_lines:
    print(popular_lines)
else:
    print("Could not retrieve popular lines.")
