import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute("DELETE FROM patients")
cursor.execute("DELETE FROM sqlite_sequence WHERE name='patients'")

conn.commit()
conn.close()

print("Database reset successfully!")