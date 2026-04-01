import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

POSTER_DIRS = [
    os.path.join(ROOT_DIR, "static", "posters"),
    os.path.join(ROOT_DIR, "static", "posters_generated"),
    os.path.join(ROOT_DIR, "static", "posters_resized"),
]

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tiff"}

total_bytes = 0
total_files = 0

for folder in POSTER_DIRS:
    folder_bytes = 0
    folder_files = 0
    for root, _, files in os.walk(folder):
        for f in files:
            if os.path.splitext(f)[1].lower() in IMAGE_EXTS:
                size = os.path.getsize(os.path.join(root, f))
                folder_bytes += size
                folder_files += 1
    total_bytes += folder_bytes
    total_files += folder_files
    label = os.path.relpath(folder, ROOT_DIR)
    print(f"{label}: {folder_files} images, {folder_bytes / (1024*1024):.2f} MB")

print(f"\nTotal: {total_files} images, {total_bytes / (1024*1024):.2f} MB")
