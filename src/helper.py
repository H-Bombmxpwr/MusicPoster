from src.album import Album
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import textwrap
from src.codec import return_banner

import scipy
import scipy.misc
import scipy.cluster

import base64
import io
import re

class Utility:
    def __init__(self, album):
        self.album = album
        self.width = 740
        self.height = 1200
        self.below_pic_h = 710
        self.margin = 50
        self.text_color = self.album.text_color
        self.background = self.album.background
        self.full_page_track_count = 12

    def buildPoster(self):
        poster = self.create_poster(self.width, self.height, self.album.background)
        album_img = self.fetch_album_cover(self.album.getCoverArt()[0]['url'])
        self.overlay_album_cover(poster, album_img)
        self.overlay_code_banner(poster)
        draw = ImageDraw.Draw(poster)
        self.draw_artist_name(draw)
        self.draw_album_name(draw)
        self.draw_tracks(draw)
        self.draw_release_date(draw)
        self.draw_runtime(draw)
        self.draw_label(draw)
        self.draw_color_squares(draw, album_img)
        return poster



    def create_poster(self, width, height, background): #create the blank canvas of the poster
        return Image.new(mode="RGBA", size=(width, height), color=background)

    def fetch_album_cover(self, url): #return the image of the album cover
        response = requests.get(url)
        return Image.open(BytesIO(response.content)).convert("RGBA")

    def overlay_album_cover(self, poster, album_img): #paste the album cover onto the image
        poster.paste(album_img, (self.margin, self.margin), album_img)

    def overlay_code_banner(self, poster):
        code_banner = return_banner(self.album.album_id, self.album.background, self.text_color)
        poster.paste(code_banner, (440 - self.margin + 15, 1125,
                     740 - self.margin + 15, 1200), code_banner)

    def draw_artist_name(self, draw):
        artist_name = self.album.artist_name.upper()
        artist_font = ImageFont.truetype('static/Oswald-Medium.ttf', 30)

        artist_name_wrapped = textwrap.wrap(artist_name, width=20)  # You might adjust this width
        y_offset = self.below_pic_h + 30  # Starting y-coordinate

        for line in artist_name_wrapped:
            text_width, _ = draw.textsize(line, font=artist_font)
            # Calculate x-coordinate to start drawing from the right margin
            x_coordinate = self.width - text_width - self.margin
            draw.text((x_coordinate, y_offset), line, font=artist_font, fill=self.text_color)
            y_offset += artist_font.getsize(line)[1] + 5  # Adjust for the next line
        self.y_offset = y_offset
        self.x_artist = x_coordinate

    def draw_album_name(self, draw):
        album_name = self.album.album_name.upper()
        album_font = ImageFont.truetype('static/Oswald-Medium.ttf', 40)

        album_name_wrapped = textwrap.wrap(album_name, width=16)  # You might adjust this width
        y_offset = self.y_offset   # Starting y-coordinate from the artist name

        for line in album_name_wrapped:
            text_width, _ = draw.textsize(line, font=album_font)
            # Calculate x-coordinate to start drawing from the right margin
            x_coordinate = self.width - text_width - self.margin
            draw.text((x_coordinate, y_offset), line, font=album_font, fill=self.text_color)
            y_offset += album_font.getsize(line)[1] + 5  # Adjust for the next line

        self.x_album = x_coordinate
        self.start_date = y_offset #where to start the

    def draw_tracks(self, draw):
        tracks = list(self.album.getTracks().values())
        num_tracks = self.album.getNumTracks()

        max_track_height = (self.height - 50 - self.below_pic_h) / max(num_tracks, self.full_page_track_count)
        font_size = int(max_track_height) - 5
        font_size = min(font_size, 30)

        track_font = ImageFont.truetype('static/Oswald-Medium.ttf', font_size)
        available_text_width = min(self.x_artist, self.x_album) - (2 * self.margin)
        offset = 710

        for tracknum, value in enumerate(tracks, 1):
            # Remove parentheses
            value = re.sub(r'\(.*?\)-', '', value)
            # Truncate anything after 'feat.' and "remaster"
            value = re.split(r' feat\.', value, flags=re.IGNORECASE)[0] #remove feat
            value = re.split(r' REMASTER', value, flags=re.IGNORECASE)[0] #remove remaster
            value = re.split(r' \(', value, flags=re.IGNORECASE)[0] #remove parathesis
            # value = re.split(r' \-', value, flags=re.IGNORECASE)[0] #remove -
            value = re.sub(r'\(.*?\)', '', value)
            value = f"{tracknum}  {value.upper()}"
            track_name_width, _ = draw.textsize(value, font=track_font)

            # Truncate at the last space within the available width
            while track_name_width > available_text_width:
                space_index = value.rfind(' ', 0, len(value) - 1)
                if space_index == -1:
                    value = value[:-4] + '...'  # Preserve space for ellipsis
                else:
                    value = value[:space_index] + '...'  # Truncate at the last space
                track_name_width, _ = draw.textsize(value, font=track_font)

            draw.text((self.margin, offset), value, font=track_font, fill=self.text_color)
            offset += max_track_height



    def draw_release_date(self, draw): #put the release date on the poster
        # release date text
        date_string = self.album.getReleaseDate()
        date_font = ImageFont.truetype('static\Oswald-Medium.ttf', 30)

        # get dimensions of date_font
        ascent, descent = date_font.getmetrics()
        (w, baseline), (offset_x, offset_y) = date_font.font.getsize(date_string)

        draw.text((self.width - w - self.margin, self.below_pic_h + 230),
                  date_string, font=date_font, fill=self.text_color)

    def draw_runtime(self, draw): #put the total runtime on the poster
         # Display runtime with release year
        runtime_string = self.album.getRuntime()
        runtime_font = ImageFont.truetype('static\Oswald-Medium.ttf', 30)

        # get dimensions of runtime font
        ascent, descent = runtime_font.getmetrics()
        (w, baseline), (offset_x, offset_y) = runtime_font.font.getsize(runtime_string)

        draw.text((self.width - w - self.margin, self.below_pic_h + 270),
                  runtime_string, font=runtime_font, fill=self.text_color)

    # def draw_label(self, draw):
    #     # label text
    #     # plit and take everything before first comma
    #     label_string = "Released by " + self.album.getLabel().split(',')[0]
    #     label_font = ImageFont.truetype('static\Oswald-Medium.ttf', 30)

    #     # get dimensions of label_font
    #     ascent, descent = label_font.getmetrics()
    #     (w, baseline), (offset_x, offset_y) = label_font.font.getsize(label_string)

    #     label_list = textwrap.wrap(label_string, width=20)
    #     g = 0
    #     for string in label_list:
    #         (w, baseline), (offset_x, offset_y) = label_font.font.getsize(string)
    #         draw.text((self.width - w - self.margin, self.below_pic_h + 310 + g),
    #                   string, font=label_font, fill=self.text_color)
    #         g += 30
        

    def draw_label(self, draw):
        # label text
        # split and take everything before the first comma
        label_string = "Released by " + self.album.getLabel().split(',')[0]
        label_font = ImageFont.truetype('static/Oswald-Medium.ttf', 30)

        # get dimensions of label_font
        ascent, descent = label_font.getmetrics()
        (w, baseline), (offset_x, offset_y) = label_font.font.getsize(label_string)

        label_list = textwrap.wrap(label_string, width=20)
        g = 0
        max_y = self.height - 90  # Ensure label is above banner
        current_y = self.below_pic_h + 310  # Starting y-coordinate for the label

        for string in label_list:
            # Only draw the label if there's enough space above the banner
            if current_y + g <= max_y:
                (w, baseline), (offset_x, offset_y) = label_font.font.getsize(string)
                draw.text((self.width - w - self.margin, current_y + g),
                        string, font=label_font, fill=self.text_color)
                g += ascent + descent + 5  # Line spacing
            else:
                break  # Stop drawing more lines if we've reached the banner

    def draw_color_squares(self, draw, album_img): #put the most common square colros on the poster
        colors = self.get_colors(album_img, 5, 250)

        offset = 0
        spacing = 30
        for color in colors:
            #draw.rectangle([(width - margin - offset, below_pic_h), (width -
                           #margin - offset - 30, below_pic_h + 30)], fill=color, outline=color)
            draw.rectangle([(self.width - self.margin - offset - 30, self.below_pic_h), 
                (self.width - self.margin - offset, self.below_pic_h + 30)], 
                fill=color, outline=color) #weird fix that needed to be made for some reason. Not sure how this wasnt erroring before

            offset += spacing

    def get_colors(self, image, numcolors=6, resize=150): #helper function to return the dominate colors in an image.
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

    def encodeImage(self, image): #encode the image to be sent to htrml to be displayed
        data = io.BytesIO()
        image.save(data, "PNG")
        encoded_img_data = base64.b64encode(data.getvalue())
        decoded_img = encoded_img_data.decode('utf-8')
        img_data = f"data:image/png;base64,{decoded_img}"
        return img_data

    def scaleDown(self, text, x1, y1, x2, y2, font, font_size): #used to scale down an image if need be
        im = Image.new("RGB", (x2-x1, y2-y1), "#fff")
        box = ((x1, y1, x2, y2))
        print(box)
        draw = ImageDraw.Draw(im)
        draw.rectangle(box, outline="#000")
        font_size = 40
        size = None
        while (size is None or size[0] > box[2] - box[0] or size[1] > box[3] - box[1]) and font_size > 0:
            font = ImageFont.truetype('static\Oswald-Medium.ttf', font_size)
            size = font.getsize_multiline(text)
            font_size -= 1
        draw.multiline_text((box[0], box[1]), text, "#000", font)


