import sqlite3

# Connect to the database
conn = sqlite3.connect('radar_images.db')

# Create a table to store the images
conn.execute('''CREATE TABLE IF NOT EXISTS radar_images
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             city TEXT NOT NULL,
             zoom INTEGER NOT NULL,
             filename TEXT NOT NULL,
             source TEXT NOT NULL,
             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

# Commit the changes and close the connection
conn.commit()
conn.close()