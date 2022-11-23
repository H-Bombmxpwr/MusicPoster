from album import Album
from PIL import Image, ImageDraw, ImageFont, ImageColor
import requests
from io import BytesIO


class Utility:
    def __init__(self,album):
        self.album = album

    def buildPoster(self):
        #create a blank canvas
        poster = Image.new(mode="RGBA", size=(740, 1200),color = "white")
        
        #add the album cover to the top
        album_image_url = self.album.getCoverArt()[0]['url']
        response = requests.get(album_image_url)
        album_img = Image.open(BytesIO(response.content)).convert("RGBA")

        #overlay the album cover
        poster.paste(album_img, (50, 50), album_img)

        #draw object creation
        draw = ImageDraw.Draw(poster)

        #artist name text
        artist = self.album.artist_name.upper()
        artist_font = ImageFont.truetype('arial.ttf', 30)
        draw.text((520, 740), artist,font=artist_font, fill=(0, 0, 0))

        #album name text
        album_name = self.album.album_name.upper()
        album_font = ImageFont.truetype('arial.ttf', 30)
        draw.text((520, 770), album_name,font=album_font, fill=(0, 0, 0))

        #tracks text
        tracks = self.album.getTracks().values()
        track_font = ImageFont.truetype('arial.ttf', 30)
        offset = 0
        for value in tracks:
            draw.text((10, 770 + offset), value,font=track_font, fill=(0, 0, 0))
            offset = offset + 35
        
        poster.show()
        


snoh = Album("primitive radio gods","rocket")
Utility(snoh).buildPoster()
    
