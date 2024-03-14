from src.album import Album
from src.helper import Utility

artist = "berhana" #change the artist here
album = "han" #change the album here 

album = Album(artist,album)
album.setColors("#FFFFFF","#000000") # change the background and text colors here, respectively
poster = Utility(album).buildPoster()
poster.show()