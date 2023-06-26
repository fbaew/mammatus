import os
import sqlite3
from flask import Flask, render_template, send_from_directory, url_for

app = Flask(__name__)

@app.route('/')
def index():
    # Get the list of images from the database
    conn = sqlite3.connect('radar_images.db')
    cursor = conn.execute('SELECT city, zoom, filename, source FROM radar_images WHERE (city, zoom, created_at) IN (SELECT city, zoom, MAX(created_at) FROM radar_images GROUP BY city, zoom, source) ORDER BY city, zoom')
    images = [{'city': row[0], 'zoom': row[1], 'filename': row[2], 'source': row[3]} for row in cursor.fetchall()]
    conn.close()

    # Generate URLs for the scaled images and full-size images
    for image in images:
        image['scaled_url'] = url_for('outputs', filename=get_scaled_filename(image['filename']))
        image['full_url'] = url_for('outputs', filename=image['filename'])

    # Render the template with the list of images
    return render_template('index.html', images=images)

@app.route('/outputs/<path:filename>')
def outputs(filename):
    # Serve the static files from the outputs directory
    return send_from_directory('outputs', filename)

def get_scaled_filename(filename):
    return os.path.splitext(filename)[0] + '_scaled.gif'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)