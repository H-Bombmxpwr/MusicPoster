from album import Album
from helper import Utility

artist = "jay z"
album = "watch the throne"

dan = Album(artist,album)
dan.setColors("white",(0,0,0))
poster = Utility(dan).buildPoster()
poster.show()