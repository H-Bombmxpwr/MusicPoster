from album import Album
from helper import Utility

artist = "berhana"
album = "han"

album = Album(artist,album)
album.setColors("#FFFFFF","#000000")
poster = Utility(album).buildPoster()
poster.show()