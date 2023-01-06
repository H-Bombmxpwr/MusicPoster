from album import Album
from helper import Utility

album = "sublime"
artist = "sublime"

dan = Album(artist,album)
dan.setColors("white",(0,0,0))
poster = Utility(dan).buildPoster()
poster.show()