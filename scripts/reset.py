import os
import shutil
import datetime
import subprocess

# Define the paths to the database and outputs directory
DB_PATH = 'radar_images.db'
OUTPUTS_PATH = 'outputs'

# Define the path to the archive directory
ARCHIVE_PATH = 'archive'

# Get the current date in YYYYMMDD format
date_str = datetime.datetime.now().strftime('%Y%m%d')

# Create the archive directory if it doesn't exist
if not os.path.exists(ARCHIVE_PATH):
    os.mkdir(ARCHIVE_PATH)

# Create the dated directory within the archive directory
archive_dir = os.path.join(ARCHIVE_PATH, date_str)
if not os.path.exists(archive_dir):
    os.mkdir(archive_dir)

# Archive the images in the outputs directory to the dated directory
for filename in os.listdir(OUTPUTS_PATH):
    src_path = os.path.join(OUTPUTS_PATH, filename)
    dst_path = os.path.join(archive_dir, filename)
    shutil.move(src_path, dst_path)

# Delete the database
os.remove(DB_PATH)

# Invoke setup.py to instantiate a new database
subprocess.run(['python', 'setup.py'])