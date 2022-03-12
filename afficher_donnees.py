import sqlite3
conn = sqlite3.connect('nel.db')
cur = conn.cursor()
req = "SELECT * FROM eleve "
result = cur.execute(req)
for row in result :
    print(row)

