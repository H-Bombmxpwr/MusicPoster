from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
import os
import io
from dotenv import load_dotenv

# ** Load environment variables from the root directory **
script_dir = os.path.dirname(os.path.abspath(__file__))  # Current script location
root_dir = os.path.join(script_dir, "..", "..")  # Move two levels up to reach the root
dotenv_path = os.path.join(root_dir, "keys.env")

load_dotenv(dotenv_path=dotenv_path)  # Load the .env file
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")

# Google Drive API setup
SERVICE_ACCOUNT_FILE = os.path.join(script_dir, "album-poster-ee299da3386a.json")  # Ensure correct path
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive_service = build("drive", "v3", credentials=credentials)

# ** Paths **
posters_directory = script_dir  # Save in the same directory as the script
resized_directory = os.path.join(script_dir, "..", "posters_resized")  # Move one level up to access `posters_resized`

# Ensure the resized directory exists
os.makedirs(resized_directory, exist_ok=True)

import re

def sanitize_filename(filename: str) -> str:
    """
    Remove characters that are illegal in Windows/macOS/Linux filenames.
    Keeps extension intact.
    """
    name, ext = os.path.splitext(filename)
    # Replace illegal characters with underscore
    name = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', name)
    # Collapse repeated underscores
    name = re.sub(r'_+', '_', name).strip('_')
    return f"{name}{ext}"


def get_existing_files(directory):
    """Returns a set of all filenames in a directory (without extensions)."""
    return {os.path.splitext(f)[0] for f in os.listdir(directory)}

def download_new_images_from_drive():
    """Downloads new images from Google Drive that are not already in posters_resized."""
    existing_files = get_existing_files(resized_directory)  # Existing resized images

    # Get a list of files in Google Drive folder
    query = f"'{DRIVE_FOLDER_ID}' in parents and (mimeType='image/png' or mimeType='image/jpeg')"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])

    new_images_downloaded = 0

    for file in files:
        file_name, ext = os.path.splitext(file["name"])
        if file_name not in existing_files:  # Only download if not already resized
            print(f"📥 Downloading new image: {file['name']}")
            request = drive_service.files().get_media(fileId=file["id"])
            safe_name = sanitize_filename(file["name"])
            file_path = os.path.join(posters_directory, safe_name)


            with open(file_path, "wb") as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()
            
            new_images_downloaded += 1

    if new_images_downloaded == 0:
        print("✅ No new images found. Posters directory is up to date.")
    else:
        print(f"✅ {new_images_downloaded} new images downloaded to {posters_directory}")

### **🚀 Run the Script**
if __name__ == "__main__":
    print("🔍 Checking Google Drive for new images...")
    download_new_images_from_drive()
    print("✅ Done!")
