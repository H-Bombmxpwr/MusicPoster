"""
Sync posters from Google Drive to local directories.

Downloads new poster submissions from the shared Google Drive folder,
detects their style from the filename, resizes them, and saves them
into the correct directory:

  - Styled posters (e.g. Artist_Album_standard.png)
      → static/posters_generated/{style}/
  - Legacy posters (no style suffix)
      → static/posters_resized/

Also updates static/js/random.js with the current legacy poster list.

Usage:
    python utility_scripts/sync_drive_posters.py
"""

import os
import sys
import io
import re
import json
import base64
from datetime import datetime
from PIL import Image
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account

# ── Paths ──
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from src.helper import POSTER_STYLES

LEGACY_DIR = os.path.join(ROOT_DIR, 'static', 'posters_resized')
GENERATED_DIR = os.path.join(ROOT_DIR, 'static', 'posters_generated')
TEMP_DIR = os.path.join(ROOT_DIR, 'static', 'posters')  # temp download location
LOG_FILE = os.path.join(ROOT_DIR, 'static', 'posters', 'log.txt')

# Legacy thumbnail dimensions (740/5 x 1200/5)
LEGACY_WIDTH = 148
LEGACY_HEIGHT = 240

# Generated poster thumbnail dimensions (larger since they display bigger)
GENERATED_WIDTH = 370
GENERATED_HEIGHT = 600


def get_drive_service():
    """Authenticate with Google Drive using either base64 env var or JSON file."""
    load_dotenv(dotenv_path=os.path.join(ROOT_DIR, 'keys.env'))
    scopes = ["https://www.googleapis.com/auth/drive.file"]

    # Try base64-encoded credentials first (production / env var)
    b64_creds = os.getenv("GOOGLE_SERVICE_ACCOUNT_BASE64")
    if b64_creds:
        creds_dict = json.loads(base64.b64decode(b64_creds).decode("utf-8"))
        credentials = service_account.Credentials.from_service_account_info(creds_dict, scopes=scopes)
        return build("drive", "v3", credentials=credentials)

    # Fall back to JSON file (local dev)
    json_path = os.path.join(TEMP_DIR, "album-poster-ee299da3386a.json")
    if os.path.exists(json_path):
        credentials = service_account.Credentials.from_service_account_file(json_path, scopes=scopes)
        return build("drive", "v3", credentials=credentials)

    raise Exception("No Google service account credentials found. "
                    "Set GOOGLE_SERVICE_ACCOUNT_BASE64 env var or place the JSON key file in static/posters/.")


def sanitize_filename(filename):
    """Remove characters illegal in Windows/macOS/Linux filenames."""
    name, ext = os.path.splitext(filename)
    name = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', name)
    name = re.sub(r'_+', '_', name).strip('_')
    return f"{name}{ext}"


def detect_style(filename):
    """Detect poster style from filename suffix.

    Files from Task #11 are named like: Artist_Album_standard_high_300dpi.png
    or from Drive submissions: Artist_Album_standard.png

    Returns (clean_name, style) or (clean_name, None) if no style detected.
    """
    name = os.path.splitext(filename)[0]

    # Try matching style as the last meaningful segment before resolution/dpi info
    # Pattern: ..._<style>_<resolution>_<dpi>dpi  or  ..._<style>
    for style in POSTER_STYLES:
        # Check if style appears as a segment (surrounded by underscores or at end)
        pattern = rf'^(.+?)_{re.escape(style)}(?:_\w+)?$'
        match = re.match(pattern, name)
        if match:
            return match.group(1), style

    return name, None


def get_existing_files():
    """Build a set of all filenames (without extension) across all poster directories."""
    existing = set()

    # Legacy posters
    if os.path.isdir(LEGACY_DIR):
        for f in os.listdir(LEGACY_DIR):
            existing.add(os.path.splitext(f)[0])

    # Generated posters in each style subdirectory
    if os.path.isdir(GENERATED_DIR):
        for style in POSTER_STYLES:
            style_dir = os.path.join(GENERATED_DIR, style)
            if os.path.isdir(style_dir):
                for f in os.listdir(style_dir):
                    existing.add(os.path.splitext(f)[0])

    return existing


def resize_image(image, width, height):
    """Resize a PIL Image to target dimensions."""
    return image.resize((width, height), Image.LANCZOS)


def log_action(message):
    """Append a timestamped line to the log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {message}\n")


def main():
    load_dotenv(dotenv_path=os.path.join(ROOT_DIR, 'keys.env'))
    drive_folder_id = os.getenv("DRIVE_FOLDER_ID")
    if not drive_folder_id:
        print("Error: DRIVE_FOLDER_ID not set in keys.env")
        return

    # Ensure directories exist
    os.makedirs(LEGACY_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)
    for style in POSTER_STYLES:
        os.makedirs(os.path.join(GENERATED_DIR, style), exist_ok=True)

    print("Connecting to Google Drive...")
    drive_service = get_drive_service()

    print("Fetching file list from Drive...")
    query = f"'{drive_folder_id}' in parents and (mimeType='image/png' or mimeType='image/jpeg')"
    results = drive_service.files().list(q=query, fields="files(id, name)", pageSize=1000).execute()
    drive_files = results.get("files", [])
    print(f"  Found {len(drive_files)} files on Drive")

    # Build set of everything we already have
    existing = get_existing_files()
    print(f"  {len(existing)} posters already downloaded")

    downloaded = 0
    styled_count = 0
    legacy_count = 0

    log_action("--- Sync started ---")

    for file_info in drive_files:
        raw_name = file_info["name"]
        safe_name = sanitize_filename(raw_name)
        name_no_ext = os.path.splitext(safe_name)[0]

        # Skip if we already have this file
        if name_no_ext in existing:
            continue

        # Download to temp
        print(f"  Downloading: {raw_name}")
        request = drive_service.files().get_media(fileId=file_info["id"])
        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

        buffer.seek(0)
        try:
            img = Image.open(buffer)
        except Exception as e:
            print(f"    Skipped (not a valid image): {e}")
            log_action(f"Skipped {raw_name}: {e}")
            continue

        # Convert to RGB if needed (for PNG save)
        if img.mode == 'RGBA':
            bg = Image.new('RGB', img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            img = bg
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Detect style from filename
        clean_name, style = detect_style(safe_name)

        if style:
            # Save to generated/{style}/ directory
            dest_dir = os.path.join(GENERATED_DIR, style)
            out_name = f"{clean_name}.png"
            out_path = os.path.join(dest_dir, out_name)

            resized = resize_image(img, GENERATED_WIDTH, GENERATED_HEIGHT)
            resized.save(out_path, 'PNG')
            styled_count += 1
            print(f"    -> {style}/{out_name}")
            log_action(f"Saved styled poster: {style}/{out_name}")
        else:
            # Save to legacy posters_resized/
            out_name = f"{name_no_ext}.png"
            out_path = os.path.join(LEGACY_DIR, out_name)

            resized = resize_image(img, LEGACY_WIDTH, LEGACY_HEIGHT)
            resized.save(out_path, 'PNG')
            legacy_count += 1
            print(f"    -> legacy/{out_name}")
            log_action(f"Saved legacy poster: {out_name}")

        downloaded += 1

    print(f"\nDownloaded {downloaded} new posters ({styled_count} styled, {legacy_count} legacy)")
    log_action(f"Sync complete: {downloaded} new ({styled_count} styled, {legacy_count} legacy)")

    print("Done!")
    log_action("--- Sync finished ---\n")


if __name__ == '__main__':
    main()
