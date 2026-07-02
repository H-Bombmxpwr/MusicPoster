"""Today's Top Albums: a poster wall generated in the background and cached.

Posters are rendered once (random style, auto colors from the cover) and
written to static/top50/. The manifest carries a timestamp; after TTL_DAYS a
visit kicks off a background regeneration while the stale wall keeps serving.

Chart source: tries the configured playlist first (Spotify blocked their own
editorial playlists — including Top 50 USA — from the API in Nov 2024, so
that only works if TOP50_PLAYLIST_ID points at a user-maintained mirror).
Falls back to Spotify's US New Releases, which client credentials can read.
"""
import json
import os
import random
import threading
import time
from datetime import datetime, timezone

from src.spotify_client import get_spotify
from src.album import Album
from src.helper import Utility, POSTER_STYLES
from src.surprise import SurpriseMe

CACHE_DIR = os.path.join('static', 'top50')
MANIFEST_PATH = os.path.join(CACHE_DIR, 'manifest.json')
TTL_SECONDS = 5 * 24 * 3600  # regenerate every 5 days
PLAYLIST_ID = os.getenv('TOP50_PLAYLIST_ID', '37i9dQZEVXbLRQDuF5jeBp')

_status = {'running': False, 'done': 0, 'total': 0, 'error': None}
_lock = threading.Lock()


def _fetch_chart_albums():
    """Return (source_label, [{'id','name','artist'}, ...]) — up to 50 unique albums."""
    sp = get_spotify()
    try:
        items = sp.playlist_items(PLAYLIST_ID, limit=50)['items']
        albums, seen = [], set()
        for it in items or []:
            track = (it or {}).get('track') or {}
            al = track.get('album') or {}
            if al.get('id') and al['id'] not in seen:
                seen.add(al['id'])
                albums.append({
                    'id': al['id'],
                    'name': al.get('name', ''),
                    'artist': al['artists'][0]['name'] if al.get('artists') else '',
                })
        if albums:
            return 'Top 50 · USA', albums
    except Exception as e:
        print(f"Top50 playlist unavailable ({e}); falling back to US new releases")

    releases = sp.new_releases(country='US', limit=50)['albums']['items']
    albums = [{
        'id': a['id'],
        'name': a.get('name', ''),
        'artist': a['artists'][0]['name'] if a.get('artists') else '',
    } for a in releases if a]
    return 'New Releases · USA', albums


def load_manifest():
    try:
        with open(MANIFEST_PATH, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def manifest_fresh(manifest):
    return bool(manifest) and (time.time() - manifest.get('generated_at', 0)) < TTL_SECONDS


def get_status():
    status = dict(_status)
    manifest = load_manifest()
    status['ready'] = bool(manifest)
    status['fresh'] = manifest_fresh(manifest)
    return status


def _generate():
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        source, albums = _fetch_chart_albums()
        _status.update(done=0, total=len(albums), error=None)
        surprise = SurpriseMe()
        items = []

        for entry in albums:
            try:
                album = Album('', '', album_id=entry['id'])
                if not album.album_found:
                    continue

                style = random.choice(POSTER_STYLES)
                utility = Utility(album, resolution='low', style=style)
                colors = utility.get_cover_colors(6)
                bg = colors[0]
                txt = surprise.find_contrasting_color(colors[1:], bg)
                bg_hex = '#%02x%02x%02x' % tuple(bg[:3])
                txt_hex = '#%02x%02x%02x' % tuple(txt[:3])

                album.setColors(bg_hex, txt_hex)
                poster = utility.buildPoster()
                filename = f"{album.album_id}.webp"
                poster.convert('RGB').save(
                    os.path.join(CACHE_DIR, filename), 'WEBP', quality=80)

                items.append({
                    'id': album.album_id,
                    'name': album.album_name,
                    'artist': album.artist_name,
                    'style': style,
                    'background': bg_hex,
                    'text': txt_hex,
                    'file': filename,
                })
            except Exception as e:
                print(f"Top50 poster failed for {entry.get('name')}: {e}")
            finally:
                _status['done'] += 1

        manifest = {
            'generated_at': time.time(),
            'generated_iso': datetime.now(timezone.utc).strftime('%B %d, %Y'),
            'source': source,
            'items': items,
        }
        tmp = MANIFEST_PATH + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(manifest, f)
        os.replace(tmp, MANIFEST_PATH)
        print(f"Top50 wall generated: {len(items)} posters from {source}")
    except Exception as e:
        _status['error'] = str(e)
        print(f"Top50 generation failed: {e}")
    finally:
        _status['running'] = False


def ensure_top50(force=False):
    """Return the current manifest (possibly stale or None). If it's missing,
    stale, or force=True, kick off a background regeneration — the caller
    keeps serving whatever exists meanwhile."""
    manifest = load_manifest()
    if not force and manifest_fresh(manifest):
        return manifest

    with _lock:
        if not _status['running']:
            _status['running'] = True
            _status['done'] = 0
            _status['total'] = 0
            threading.Thread(target=_generate, daemon=True).start()

    return manifest
