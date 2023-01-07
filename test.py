from album import Album
from helper import Utility

artist = "beck"
album = "guero"

dan = Album(artist,album)
dan.setColors("#FFFFFF","#000000")
poster = Utility(dan).buildPoster()
poster.show()