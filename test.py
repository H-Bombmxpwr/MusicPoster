from album import Album
from helper import Utility

artist = "ariana grande"
album = "positions"

dan = Album(artist,album)
poster = Utility(dan).buildPoster()
poster.show()