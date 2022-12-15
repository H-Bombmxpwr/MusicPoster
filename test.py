from album import Album
from helper import Utility

album = "my beautiful dark twisted fantasy"
artist = "kanye west"

dan = Album(artist,album)
dan.setColors("white",(0,0,0))
poster = Utility(dan).buildPoster()
poster.show()