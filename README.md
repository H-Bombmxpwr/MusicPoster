# MusicPoster
Makes a Album Poster given an album and an artist

# About
This project takes in the name of an artist and album and using the spotify API returns information about the album and presents it in a modern looking poster. You can choose the text color and background color in [local.py](local.py) or within the local hosted website as well using the HTML color picker. The poster will also output the spotify code of the album which can be scanned by any phone with the spotify app, and it will bring your straight to that album. 

# Website
You can make your own posters at the webiste [here](https://trevorg73.web.illinois.edu/musicposter/home). It will prompt for an artist and album. Suggestions will autofill based on what you have already entered. If you cannot get the search to work, pasting the Spotify album link into the box will work as well. A plethora of examples can be seen [here](https://trevorg73.web.illinois.edu/musicposter/mosaic). Note the examples are of lower quality to save space. 

# Local Usage
To generate the poster clone the code. You will need a `SPOTIPY_CLIENT_ID` and `SPOTIPY_CLIENT_SECRET` which are the same as the spotify ones which you can get from spotify for developers [here](https://developer.spotify.com/documentation/general/guides/authorization/). 
Remove the `.example` from [keys.env.example](keys.env.example) and add your own keys.

There is also a `requirements.txt` file to install the right dependencies using 
```console
pip install -r requirements.txt
```

Once this is done you can run [app.py](app.py) to get a localhosted site, or run [local.py](local.py) to make a poster without hosting a wesbite. You can change the album and artist in [local.py](local.py) as well. 

All that is required is to send in an artist and album(with close enough spelling) and the program will do the rest

# Examples
Some examples are in [EXAMPLES.md](EXAMPLES.md). A more extensive list of examples can be found [here](https://trevorg73.web.illinois.edu/musicposter/mosaic). 


# Printing
Almost everything generated by this program will be copyrighted material, which may be illegal to print and resell. Do not do this.

# In the future
Stronger mobile support for the website

