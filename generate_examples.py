"""
Generate example posters from a Spotify playlist.

Usage:
    python generate_examples.py <playlist_url> [--resolution high] [--output static/posters_generated]

Extracts unique albums from the playlist's tracks, then prompts you to either
generate all 5 styles per album or 1 random style per album. Skips any
album+style combo that already exists on disk.
"""

import argparse
import os
import sys
import re
import random

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

from src.album import Album
from src.helper import Utility, POSTER_STYLES
from src.surprise import SurpriseMe


def extract_playlist_id(url):
    """Extract playlist ID from a Spotify URL or URI."""
    # Handle full URL: https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M?si=...
    match = re.search(r'playlist[/:]([A-Za-z0-9]+)', url)
    if match:
        return match.group(1)
    # Maybe it's just an ID already
    if re.match(r'^[A-Za-z0-9]{22}$', url):
        return url
    return None


def get_albums_from_playlist(sp, playlist_id):
    """Fetch all tracks from a playlist and return unique albums as (artist, album_name, album_id) tuples."""
    seen_album_ids = set()
    albums = []

    results = sp.playlist_tracks(playlist_id, fields='items.track.album,next')
    while True:
        for item in results.get('items', []):
            track = item.get('track')
            if not track or not track.get('album'):
                continue
            album_data = track['album']
            album_id = album_data.get('id')
            if not album_id or album_id in seen_album_ids:
                continue
            # Only include full albums (skip singles/compilations if desired)
            seen_album_ids.add(album_id)
            artist = album_data['artists'][0]['name'] if album_data.get('artists') else 'Unknown'
            album_name = album_data.get('name', 'Unknown')
            albums.append((artist, album_name, album_id))

        if results.get('next'):
            results = sp.next(results)
        else:
            break

    return albums


def get_existing_posters(output_dir):
    """Build a set of (safe_name, style) tuples for all posters already on disk."""
    existing = set()
    for style in POSTER_STYLES:
        style_dir = os.path.join(output_dir, style)
        if os.path.isdir(style_dir):
            for f in os.listdir(style_dir):
                name = os.path.splitext(f)[0]
                existing.add((name, style))
    return existing


def generate_posters(albums, output_dir, resolution, random_mode=False):
    """Generate poster styles for each album and save to disk.

    If random_mode is True, picks one random style per album instead of all 5.
    Skips any album+style combo that already exists on disk.
    """
    surprise = SurpriseMe()
    existing = get_existing_posters(output_dir)

    generated = 0
    skipped = 0

    for i, (artist, album_name, album_id) in enumerate(albums, 1):
        print(f"\n[{i}/{len(albums)}] {artist} - {album_name}")

        safe_name = re.sub(r'[^\w\-. ]+', '', f"{artist} - {album_name}").strip()

        # Decide which styles to generate
        if random_mode:
            # Pick one random style, but skip if it already exists — try others
            shuffled = random.sample(POSTER_STYLES, len(POSTER_STYLES))
            styles_to_gen = []
            for s in shuffled:
                if (safe_name, s) not in existing:
                    styles_to_gen = [s]
                    break
            if not styles_to_gen:
                print(f"  Already has a poster in every style, skipping")
                skipped += 1
                continue
        else:
            styles_to_gen = [s for s in POSTER_STYLES if (safe_name, s) not in existing]
            if not styles_to_gen:
                print(f"  All 5 styles already exist, skipping")
                skipped += 1
                continue

        album = Album(artist, album_name, album_id=album_id)

        if not album.album_found:
            print(f"  [SKIP] Album not found on Spotify")
            continue

        # Auto-pick colors from cover art
        utility_tmp = Utility(album, resolution='low')
        album_img = utility_tmp.fetch_album_cover(album.getCoverArt()[0]['url'])
        colors = utility_tmp.get_colors(album_img, 6)
        bg_color = colors[0]
        text_color = surprise.find_contrasting_color(colors[1:], bg_color)
        bg_hex = f"#{bg_color[0]:02x}{bg_color[1]:02x}{bg_color[2]:02x}"
        text_hex = f"#{text_color[0]:02x}{text_color[1]:02x}{text_color[2]:02x}"
        album.setColors(bg_hex, text_hex)

        for style in styles_to_gen:
            style_dir = os.path.join(output_dir, style)
            os.makedirs(style_dir, exist_ok=True)

            filepath = os.path.join(style_dir, f"{safe_name}.png")
            try:
                util = Utility(album, resolution=resolution, style=style)
                poster = util.buildPoster()
                poster.save(filepath, 'PNG')
                generated += 1
                print(f"  {style}: saved")
            except Exception as e:
                print(f"  {style}: FAILED - {e}")

    print(f"\nGenerated {generated} posters, skipped {skipped} albums (already existed)")


def main():
    parser = argparse.ArgumentParser(description='Generate example posters from a Spotify playlist')
    parser.add_argument('playlist_url', help='Spotify playlist URL or ID')
    parser.add_argument('--resolution', default='high', choices=['low', 'medium', 'high', 'ultra'],
                        help='Poster resolution (default: high)')
    parser.add_argument('--output', default='static/posters_generated',
                        help='Output directory (default: static/posters_generated)')
    args = parser.parse_args()

    load_dotenv(dotenv_path='keys.env')

    playlist_id = extract_playlist_id(args.playlist_url)
    if not playlist_id:
        print(f"Error: Could not parse playlist ID from '{args.playlist_url}'")
        sys.exit(1)

    print(f"Playlist ID: {playlist_id}")
    print(f"Resolution: {args.resolution}")
    print(f"Output: {args.output}")

    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

    # Fetch playlist info
    try:
        playlist_info = sp.playlist(playlist_id, fields='name,tracks.total')
        print(f"Playlist: {playlist_info['name']} ({playlist_info['tracks']['total']} tracks)")
    except Exception as e:
        print(f"Error fetching playlist: {e}")
        sys.exit(1)

    # Extract unique albums
    print("\nExtracting unique albums...")
    albums = get_albums_from_playlist(sp, playlist_id)
    print(f"Found {len(albums)} unique albums")

    if not albums:
        print("No albums found in playlist.")
        sys.exit(0)

    # Ask user: all 5 styles or random 1 per album
    print(f"\nGeneration mode:")
    print(f"  [1] All 5 styles per album ({len(albums) * 5} posters max)")
    print(f"  [2] Random 1 style per album ({len(albums)} posters max)")
    choice = input("\nChoice (1/2): ").strip()
    random_mode = choice == '2'

    if random_mode:
        print(f"\nGenerating 1 random style per album...")
    else:
        print(f"\nGenerating all 5 styles per album...")

    os.makedirs(args.output, exist_ok=True)
    generate_posters(albums, args.output, args.resolution, random_mode=random_mode)

    print("\nDone!")


if __name__ == '__main__':
    main()
