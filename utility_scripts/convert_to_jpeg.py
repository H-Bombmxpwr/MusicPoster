"""
Convert all PNG poster images to JPEG to reduce disk usage.

Scans static/posters_generated/ and static/posters_resized/,
converts PNGs to JPEGs (quality 85), and deletes the original PNGs.

Usage:
    python utility_scripts/convert_to_jpeg.py
"""

import os
from PIL import Image

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

POSTER_DIRS = [
    os.path.join(ROOT_DIR, "static", "posters_generated"),
    os.path.join(ROOT_DIR, "static", "posters_resized"),
]

JPEG_QUALITY = 85


def convert_folder(folder):
    converted = 0
    saved_bytes = 0

    for root, _, files in os.walk(folder):
        for f in files:
            if not f.lower().endswith(".png"):
                continue

            png_path = os.path.join(root, f)
            jpg_path = os.path.splitext(png_path)[0] + ".jpg"

            png_size = os.path.getsize(png_path)

            try:
                img = Image.open(png_path)
                if img.mode == "RGBA":
                    bg = Image.new("RGB", img.size, (255, 255, 255))
                    bg.paste(img, mask=img.split()[3])
                    img = bg
                elif img.mode != "RGB":
                    img = img.convert("RGB")

                img.save(jpg_path, "JPEG", quality=JPEG_QUALITY)
                jpg_size = os.path.getsize(jpg_path)

                os.remove(png_path)

                saved_bytes += png_size - jpg_size
                converted += 1
            except Exception as e:
                print(f"  Error converting {png_path}: {e}")

    return converted, saved_bytes


def main():
    total_converted = 0
    total_saved = 0

    for folder in POSTER_DIRS:
        if not os.path.isdir(folder):
            continue

        label = os.path.relpath(folder, ROOT_DIR)
        print(f"Converting {label}...")
        converted, saved = convert_folder(folder)
        total_converted += converted
        total_saved += saved
        print(f"  {converted} images converted, {saved / (1024*1024):.1f} MB saved")

    print(f"\nTotal: {total_converted} images converted, {total_saved / (1024*1024):.1f} MB saved")


if __name__ == "__main__":
    main()
