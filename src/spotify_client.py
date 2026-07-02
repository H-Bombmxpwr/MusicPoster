"""Shared Spotify client + small in-memory caches.

Creating a new SpotifyClientCredentials per request forces a fresh token
POST to accounts.spotify.com every time. One shared client reuses the
cached token until it expires (spotipy refreshes it automatically).
"""
import os
import threading
from collections import OrderedDict

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv(dotenv_path='keys.env')

_client = None
_client_lock = threading.Lock()


def get_spotify():
    """Return the shared client-credentials Spotify client."""
    global _client
    if _client is None:
        with _client_lock:
            if _client is None:
                manager = SpotifyClientCredentials(
                    os.getenv('SPOTIPY_CLIENT_ID'),
                    os.getenv('SPOTIPY_CLIENT_SECRET'))
                _client = spotipy.Spotify(client_credentials_manager=manager)
    return _client


class LRUCache:
    """Tiny thread-safe LRU cache for API/network payloads."""

    def __init__(self, maxsize=128):
        self.maxsize = maxsize
        self._data = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key):
        with self._lock:
            if key in self._data:
                self._data.move_to_end(key)
                return self._data[key]
        return None

    def set(self, key, value):
        with self._lock:
            self._data[key] = value
            self._data.move_to_end(key)
            while len(self._data) > self.maxsize:
                self._data.popitem(last=False)
