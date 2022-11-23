from album import Album
from helper import Utility

print("Enter an Artist: ")
artist = input()
print("Enter an Album by " + artist)
album = input()

select = Album(artist,album)
Utility(select).buildPoster().show()