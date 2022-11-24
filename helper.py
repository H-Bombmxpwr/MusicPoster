from album import Album
from PIL import Image, ImageDraw, ImageFont, ImageColor
import requests
from io import BytesIO
import textwrap
from collections import Counter

import numpy as np
import scipy
import scipy.misc
import scipy.cluster

import base64
import io


class Utility:
    def __init__(self,album):
        self.album = album

    def buildPoster(self,text_color = (0,0,0),background = "white"):
        #create a blank canvas
        width = 740
        height = 1200
        below_pic_h = 710
        margin = 50
        poster = Image.new(mode="RGBA", size=(width, height),color = background)
        
        #add the album cover to the top
        album_image_url = self.album.getCoverArt()[0]['url']
        response = requests.get(album_image_url)
        album_img = Image.open(BytesIO(response.content)).convert("RGBA")

        #overlay the album cover
        poster.paste(album_img, (margin, margin), album_img)

        #draw object creation
        draw = ImageDraw.Draw(poster)

        #artist name text
        artist_name = self.album.artist_name.upper()
        artist_font = ImageFont.truetype('static\Oswald-Medium.ttf', 35)

        #dimensions of artist text
        ascent, descent = artist_font.getmetrics()
        (w, baseline), (offset_x, offset_y) = artist_font.font.getsize(artist_name)

        draw.text((width - w - margin, below_pic_h + 30), artist_name, font=artist_font, fill=text_color)


        #album name text
        album_name = self.album.album_name.upper()
        album_font = ImageFont.truetype('static\Oswald-Medium.ttf', 40)

        #dimenstions of album text
        ascent, descent = album_font.getmetrics()
        (w, baseline), (offset_x, offset_y) = album_font.font.getsize(album_name)

        draw.text((width - w - margin, below_pic_h + (offset_y) + (ascent - offset_y) + descent), album_name, font=album_font, fill=text_color)

        #tracks text
        tracks = self.album.getTracks().values()
        
        if(height - 50 - below_pic_h) > 35 * self.album.getNumTracks():
            increment = 35
            font = 30
        else:
            increment = (height - 50 - below_pic_h)/self.album.getNumTracks()  #taking the height, subtracting 50 for margin and then 710 for the starting height
            font = int((height - 50 - below_pic_h)/self.album.getNumTracks()) - 5

        track_font = ImageFont.truetype('static\Oswald-Medium.ttf', font)

        offset = 0
        tracknum = 1
        space = '  '
        for value in tracks:
            draw.text((margin, 710 + offset), str(tracknum) + space + value.upper(), font=track_font, fill=text_color)
            offset = offset + increment
            tracknum = tracknum + 1
            if tracknum == 10:
                space = ' '

        

        #release date text

        date_string = self.album.getReleaseDate() 
        date_font = ImageFont.truetype('static\Oswald-Medium.ttf', 30)

        #get dimensions of date_font
        ascent, descent = date_font.getmetrics()
        (w, baseline), (offset_x, offset_y) = date_font.font.getsize(date_string)

        draw.text((width - w - margin, below_pic_h + 200),  date_string, font=date_font, fill=text_color)


        #label text
        label_string = "Released by " + self.album.getLabel() 
        label_font = ImageFont.truetype('static\Oswald-Medium.ttf', 30)

        #get dimensions of label_font
        ascent, descent = label_font.getmetrics()
        (w, baseline), (offset_x, offset_y) = label_font.font.getsize(label_string)

        #offset = below_pic_h + 240
        #for line in textwrap.wrap(label_string, width=40):
         #   draw.text((width - margin - 300,offset), line, font=label_font, fill=text_color)
          #  offset += 35

        draw.text((width - w - margin, below_pic_h + 240),  label_string, font=label_font, fill=text_color)

        #Display runtime with release year
        runtime_string = self.album.getRuntime() + " / " + str(self.album.getReleaseYear())
        runtime_font = ImageFont.truetype('static\Oswald-Medium.ttf', 30)

        #get dimensions of runtime font
        ascent, descent = runtime_font.getmetrics()
        (w, baseline), (offset_x, offset_y) = runtime_font.font.getsize(runtime_string)

        draw.text((width - w - margin, below_pic_h + 280),  runtime_string, font=runtime_font, fill=text_color)


        #get color squares using helper function to get most vibrant colors of image
        colors = self.get_colors(poster,5,250)
        
        offset = 0
        spacing = 60
        for color in colors:
            draw.rectangle([(width - margin - offset, below_pic_h), (width - margin - offset - 30, below_pic_h + 30)],fill=color, outline = color)
            offset += spacing

        return poster
        

    def get_colors(self,image, numcolors=5, resize=150):
    # Resize image to speed up processing
        img = image.copy()
        img.thumbnail((resize, resize))

        # Reduce to palette
        paletted = img.convert('P', palette=Image.ADAPTIVE, colors=numcolors)

        # Find dominant colors
        palette = paletted.getpalette()
        color_counts = sorted(paletted.getcolors(), reverse=True)
        colors = list()
        for i in range(numcolors):
            palette_index = color_counts[i][1]
            dominant_color = palette[palette_index*3:palette_index*3+3]
            colors.append(tuple(dominant_color))

        return colors

    def encodeImage(self,image):
        data = io.BytesIO()
        image.save(data, "PNG")
        encoded_img_data = base64.b64encode(data.getvalue())
        decoded_img=encoded_img_data.decode('utf-8')
        img_data = f"data:image/png;base64,{decoded_img}"
        return img_data





    
