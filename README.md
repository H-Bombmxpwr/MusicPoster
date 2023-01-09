# MusicPoster
Makes a Music Poster given an album and an artist

# About
This project takes in the name of an artist and album and using the spotify API returns a lot of information about the album and proesents it in a modern looking poster. You can choose the text color and background color in [test.py](test.py) or within the local hosted website as well using the HTML color picker. The poster will also output the spotify code of the album which can be scanned by any phone with the spotify app, and it will bring your straight to that album. 

# Usage
To generate the poster clone the code. You will need a `SPOTIPY_CLIENT_ID` and `SPOTIPY_CLIENT_SECRET` which are the same as the spotify ones which you can get from spotify for developers [here](https://developer.spotify.com/documentation/general/guides/authorization/). 
Create a keys.env file in the main directory and set these two variables there.

There is also a `requirements.txt` file to install the right dependencies using 
```console
pip install -r requirements.txt
```

Once this is done you can run [app.py](app.py) to get a localhosted site, or run [test.py](test.py) to make a poster without hosting a wesbite. You can change the album and artist in [test.py](test.py) as well. 

All that is required is to send in an artist and album(with close enough spelling) and the program will do the rest

# Examples
If you don't want to do this all yourself it will be published to a website soon, but in the mean time you can see some examples in [EXAMPLES.md](EXAMPLES.md)
Here is one example:
HAN by Berhana
![image](https://user-images.githubusercontent.com/97134010/211364264-d18a2fe4-d9d9-4139-b03b-7541a69f2566.png)


# In the future
Trying to add it to a website. Also want to improve the color changing algorithm to remove some of the blurriness from the scannable spotify codes. 

