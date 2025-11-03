import sqlite3

# Connect to the database
conn = sqlite3.connect('messages.db')
cursor = conn.cursor()

# Step 1: Drop the existing table if it exists
cursor.execute("DROP TABLE IF EXISTS messages")

# Step 2: Create the new table with the desired structure
cursor.execute('''
    CREATE TABLE messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        char_name TEXT,
        content TEXT,
        timestamp TEXT,
        channel_name TEXT
    )
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Table 'messages' has been replaced with a new one.")
