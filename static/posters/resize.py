from PIL import Image
import os
import json
from datetime import datetime

# Get the directory of the script being executed (`static/posters/`)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # `static/posters/`
BASE_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))  # Move up to `MusicPoster/`

# Paths to directories and files
image_directory = os.path.join(BASE_DIR, 'static', 'posters')
resized_directory = os.path.join(BASE_DIR, 'static', 'posters_resized')
log_file_path = os.path.join(BASE_DIR, 'static', 'posters', 'log.txt')

# Ensure the resized directory exists
if not os.path.exists(resized_directory):
    os.makedirs(resized_directory)

# Target dimensions
target_width = 740 // 5
target_height = 1200 // 5

# List to hold the names of newly resized images
new_image_names = []

# Function to log the resize action
def log_resize_action(log_path, image_names, deleted_files):
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, 'a', encoding = 'utf-8') as log_file:
        log_file.write(f"Resize action performed on {current_datetime}:\n")
        for name in image_names:
            log_file.write(f"✅ Resized: {name}\n")
        for name in deleted_files:
            log_file.write(f"🗑️ Deleted Original: {name}\n")
        log_file.write("\n")

# Resize and save the image
def resize_and_save(image, filename, format=None):
    resized_image = image.resize((target_width, target_height), Image.LANCZOS)
    save_path = os.path.join(resized_directory, filename)
    resized_image.save(save_path, format=format)
    print(f"Resized and saved {filename} in {resized_directory}.")
    new_image_names.append(filename)

deleted_files = []

# Iterate over the files in the directory
for filename in os.listdir(image_directory):
    if filename.endswith('.png') or filename.endswith('.jpg'):
        file_path = os.path.join(image_directory, filename)
        image = Image.open(file_path)

        # Skip if the image is already the target size
        if image.size == (target_width, target_height):
            continue

        # Determine new filename and format
        new_filename = os.path.splitext(filename)[0] + '.png'
        format = 'PNG' if filename.endswith('.jpg') else None

        # Resize and save the image
        resize_and_save(image, new_filename, format=format)

        # Delete the original file after resizing
        os.remove(file_path)
        deleted_files.append(filename)

# Log resizing and deletion
if new_image_names or deleted_files:
    log_resize_action(log_file_path, new_image_names, deleted_files)
    print(f"✅ Resize complete. {len(new_image_names)} images processed.")

else:
    print("⚠️ No new images to resize.")
