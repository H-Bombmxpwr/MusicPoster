# MusicPoster
Makes a Music Poster given an album and an artist

# About
This project takes in the name of an artist and album and using the spotify API returns a lot of information about the album and proesents it in a modern looking poster. You can choose the text color and background color in [local.py](local.py) or within the local hosted website as well using the HTML color picker. The poster will also output the spotify code of the album which can be scanned by any phone with the spotify app, and it will bring your straight to that album. 

# Website
You can make your own posters at the webiste [here](https://trevorg73.web.illinois.edu/musicposter/home). 

# Local Usage
To generate the poster clone the code. You will need a `SPOTIPY_CLIENT_ID` and `SPOTIPY_CLIENT_SECRET` which are the same as the spotify ones which you can get from spotify for developers [here](https://developer.spotify.com/documentation/general/guides/authorization/). 
Create a keys.env file in the main directory and set these two variables there.

There is also a `requirements.txt` file to install the right dependencies using 
```console
pip install -r requirements.txt
```

Once this is done you can run [app.py](app.py) to get a localhosted site, or run [local.py](local.py) to make a poster without hosting a wesbite. You can change the album and artist in [local.py](local.py) as well. 

All that is required is to send in an artist and album(with close enough spelling) and the program will do the rest

# Examples
A lot of example are in [EXAMPLES.md](EXAMPLES.md)
Here is one example:
HAN by Berhana
![image](https://user-images.githubusercontent.com/97134010/213099523-be8b207b-3bec-4e89-abad-ea35648f0bdf.png)


# In the future
Stronger mobile support for the website

