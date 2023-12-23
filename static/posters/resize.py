from PIL import Image
import os

# Directory where the images are located (assuming the current working directory)
image_directory = '\static\posters'

# The target dimensions
target_width = 740 // 5
target_height = 1200 // 5

# Iterate over the files in the directory
for filename in os.listdir(image_directory):
    if filename.endswith('.png'):
        # Construct the full file path
        file_path = os.path.join(image_directory, filename)
        # Open the image
        image = Image.open(file_path)
        # Check if the image is already the target size
        if image.size == (target_width, target_height):
            print(f"{filename} is already at the target size.")
            continue

        # Resize the image
        resized_image = image.resize((target_width, target_height), Image.ANTIALIAS)
        # Save the resized image in the same directory with a suffix to indicate it's resized
        
        resized_image.save(os.path.join('static\posters_resized', filename))
        print(f"Resized and saved {new_filename}.")

# List the contents of the directory after resizing to confirm the operation
os.listdir(image_directory)