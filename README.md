# Album Poster
[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/H-Bombmxpwr/MusicPoster)
[![Website](https://img.shields.io/badge/Website-AlbumPoster-brightgreen)](https://album.hxr.life/)

Creates stunning posters for any queried album that display:
- The album cover art
- Every track on the album (up to 50)
- Recording artist
- Name of the album
- Release date (Month Day, Year -> June 29, 1973)
- Total runtime of the album (minutes:seconds -> 33:29)
- Label the album was released under
- A scannable Spotify code that links to the album

You can customize the text color, the background color, and the format of the tracks on the poster.

# Website
You can make your own posters at the website [![Website](https://img.shields.io/badge/Website-AlbumPoster-brightgreen)](https://album.hxr.life/). Enter an artist and album to get started. Suggestions will autofill as you type. If you cannot get the search to work, pasting the Spotify album link into the album box will work 100% of the time.

### Surprise Me!
Not sure where to start? Use the **Surprise Me** button on the homepage to generate a random album poster instantly.

---

# Examples
Some examples are available in [EXAMPLES.md](EXAMPLES.md). A more extensive list can be found on the [Mosaic Page](https://album.hxr.life/mosaic). Note: The examples are of lower quality to save space.

---

# Printing
Almost all posters generated by this program feature copyrighted material, which may be illegal to print and resell. Proceed at your own risk.

---

# Requirements
This project is built using **Python 3.11.5**.  
Using other versions, especially **Python 3.12+,** may cause compatibility issues with dependencies.

To check your Python version:
```bash
python --version
```

# Local Usage and Contribution
To generate posters locally:
1. Clone the repository.
2. Obtain a `SPOTIPY_CLIENT_ID` and `SPOTIPY_CLIENT_SECRET` from [Spotify for Developers](https://developer.spotify.com/documentation/general/guides/authorization/).
3. Remove the `.example` from [keys.env.example](keys.env.example) and add your Spotify keys.

### 🐍 Set Up a Python Virtual Environment (Recommended)
To avoid dependency issues and keep your system clean, create and activate a virtual environment:

```bash
# Create a virtual environment named `.venv`
python -m venv .venv

# Activate it
# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate
```

Once activated, install the required dependencies:
```bash
pip install -r requirements.txt
```

Run the app:
- Use [app.py](app.py) to launch a localhosted website.
- Use [local.py](local.py) to create posters without hosting a site (you can specify the album and artist directly in the script).

Simply provide an artist and album name (with close enough spelling), and the program does the rest!

---

# In the Future
- Enhanced mobile support for the website.

---

# Special Thanks
A heartfelt thanks to:
- **Noah Sprovieri** for providing graphic design support.
- **Katie Ulinski** for providing graphic design support.
- **Contributors** who have submitted custom posters or code contributions to the project. Your efforts have made this project even better!

