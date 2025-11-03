import sqlite3

conn = sqlite3.connect('/Users/elijahshackleford/Webscrapin/TheAlgoritihim/DanganRP bot/messages.db')
cursor = conn.cursor()



cursor.execute("SELECT rowid, content FROM messages")
rows = cursor.fetchall()

total_checked = 0
total_cleaned = 0
#cursor.execute("SELECT rowid, content FROM messages WHERE content LIKE '> [Reply to]%' LIMIT 1")
#rows = cursor.fetchall()
for rowid, content in rows: 
    lines = content.split('\n')
    total_checked += 1
                    
    if len(lines) >= 2 and lines[0].startswith('> [Reply to]'):
        cleaned_content = '\n'.join(lines[2:])

        cursor.execute("UPDATE messages SET content = ? WHERE rowid = ?", (cleaned_content, rowid))
        total_cleaned += 1 
        if total_cleaned % 100 == 0:
            print(f"Cleaned {total_cleaned} messages so far...")
    

print(total_checked)
print(total_cleaned) 

conn.commit()
conn.close()