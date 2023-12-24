#function just locally to resize all images in posters directory, save to resized posters, and also update random.js accordingly

from PIL import Image
import os
import re
import json

# Paths to directories and files
image_directory = 'MusicPoster\static\posters'
resized_directory = 'MusicPoster\static\posters_resized'
js_file_path = 'MusicPoster\\static\\js\\random.js'

# Ensure the resized directory exists
if not os.path.exists(resized_directory):
    os.makedirs(resized_directory)

# Target dimensions
target_width = 740 // 5
target_height = 1200 // 5

# List to hold the names of newly resized images
new_image_names = []

# Resize and save the image
def resize_and_save(image, filename, format=None):
    resized_image = image.resize((target_width, target_height), Image.ANTIALIAS)
    save_path = os.path.join(resized_directory, filename)
    resized_image.save(save_path, format=format)
    print(f"Resized and saved {filename} in {resized_directory}.")
    new_image_names.append(filename)

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

        # Delete the original file
        os.remove(file_path)

# Append new image names to the JavaScript array
def append_to_js(js_path, new_images):
    # Read the content of the JavaScript file
    with open(js_path, 'r') as file:
        content = file.read()

    # Find the array using regex and convert it to a Python list
    array_match = re.search(r'const posters = (\[.*?\]);', content, re.DOTALL)
    if not array_match:
        return

    posters_array_str = array_match.group(1)
    posters_array = json.loads(posters_array_str)

    # Add the new images to the list and remove duplicates
    updated_posters = list(set(posters_array + new_images))

    # Replace the old array with the new one
    updated_content = re.sub(
        r'const posters = \[.*?\];',
        'const posters = ' + json.dumps(updated_posters, indent=4) + ';',
        content,
        flags=re.DOTALL
    )

    # Write the updated content back to the file
    with open(js_path, 'w') as file:
        file.write(updated_content)

# Call the function to append to the JavaScript array if there are new images
if new_image_names:
    append_to_js(js_file_path, new_image_names)
