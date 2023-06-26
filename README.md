# Mammatus

This tool captures weather images (radar, satellite) for a specified city and
assembles them into a GIF animation. It supports multiple sources for the radar
images, including The Weather Network and Windy.com. The script uses Selenium to
automate the process of capturing the radar images from the web, and it can be
run in headless mode for automated use. The resulting GIF animation is saved
to disk, and the script also supports logging the images in a SQLite database
for later retrieval.

## TODO
Some possible future weather backends...

- earth.nullschool.net
- AccuWeather