import os
import re
import json
from datetime import datetime

# Get the directory of this script (`static/posters/`)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))  # Move up to `MusicPoster/`

# Paths
resized_directory = os.path.join(BASE_DIR, 'static', 'posters_resized')
js_file_path = os.path.join(BASE_DIR, 'static', 'js', 'random.js')
log_file_path = os.path.join(BASE_DIR, 'static', 'posters', 'log.txt')

# Function to log JavaScript updates
def log_js_update(log_path, updated_posters):
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, 'a', encoding='utf-8') as log_file:
        log_file.write(f"JavaScript update performed on {current_datetime}:\n")
        for name in updated_posters:
            log_file.write(f"📌 Added to `random.js`: {name}\n")
        log_file.write("\n")

# Collect all PNG files in `posters_resized/`
new_posters = [f for f in os.listdir(resized_directory) if f.endswith('.png')]

if not new_posters:
    print("🚨 No posters found in `posters_resized/`. Nothing to update.")
    exit(1)

# Read `random.js`
with open(js_file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# Find the array using regex
array_match = re.search(r'const posters = (\[.*?\]);', content, re.DOTALL)
if not array_match:
    print("🚨 ERROR: Could not find `posters` array in `random.js`!")
    exit(1)

# Extract the existing posters array
posters_array_str = array_match.group(1)
posters_array = json.loads(posters_array_str)

# Merge new posters, remove duplicates
updated_posters = sorted(set(posters_array + new_posters))

# Escape backslashes before updating JS file
updated_posters_str = json.dumps(updated_posters, indent=4).replace("\\", "\\\\")

# Replace the old array with the new one
updated_content = re.sub(
    r'const posters = \[.*?\];',
    f'const posters = {updated_posters_str};',
    content,
    flags=re.DOTALL
)

# Write back to `random.js`
with open(js_file_path, 'w', encoding='utf-8') as file:
    file.write(updated_content)

# Log the update
log_js_update(log_file_path, updated_posters)
print(f"✅ Updated `{js_file_path}` with {len(updated_posters)} posters.")
