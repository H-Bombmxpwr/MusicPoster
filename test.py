from album import Album
from helper import Utility

artist = "the weeknd"
album = "after hours"
color = "white"

dan = Album(artist,album,color)
poster = Utility(dan).buildPoster()
poster.show()