# Mammatus

This tool captures weather images (radar, satellite) for a specified city and
assembles them into a GIF animation. It supports multiple sources for the radar
images, including The Weather Network and Windy.com. The script uses Selenium to
automate the process of capturing the radar images from the web, and it can be
run in headless mode for automated use. The resulting GIF animation is saved
to disk, and the script also supports logging the images in a SQLite database
for later retrieval.

# Usage

## CLI
You can collect imagery from the command line with main.py:

```
usage: main.py [-h] [-f FRAMES] [-z ZOOM] [-o OUTPUT] [-d DB_PATH] [-s SOURCE] [--mode MODE] [--debug] city

Capture weather radar images and assemble them into a gif.

positional arguments:
  city                  The city to capture the radar images of.

options:
  -h, --help            show this help message and exit
  -f FRAMES, --frames FRAMES
                        The number of frames to capture for the radar animation.
  -z ZOOM, --zoom ZOOM  The zoom level for radar images. Can be 0, 1, 2, 3, or 4.
  -o OUTPUT, --output OUTPUT
                        The filename to save the output gif to. If not specified, a filename will be generated based on the current time, city, and zoom level.
  -d DB_PATH, --db-path DB_PATH
                        The path to the SQLite database file to use for storing radar images.
  -s SOURCE, --source SOURCE
                        The source to use for the radar images. Can be weathernetwork, windy, or acuweather.
  --mode MODE           The mode to use for the Windy weather provider.
  --debug               If set, run the webdriver in non-headless mode for debugging purposes.
  ```

  ## Python

  You can also acheive this in Python directly by instantiating a RadarFetcher object and calling capture_radar() and write_gif() on it.

  ## Cron Job

  Experimental; Run cron.py to collect images for multiple places in parallel.

## TODO
Some possible future weather backends...

- earth.nullschool.net
- AccuWeather