from album import Album
from helper import Utility

artist = "the weeknd"
album = "starboy"

dan = Album(artist,album)
poster = Utility(dan).buildPoster()
poster.show()