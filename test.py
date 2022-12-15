from album import Album
from helper import Utility

artist = "anderson paak"
album = "oxnard"

dan = Album(artist,album)
dan.setColors("white",(0,0,0))
poster = Utility(dan).buildPoster()
poster.show()