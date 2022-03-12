import sqlite3
from datetime import datetime
import os
conn = sqlite3.connect('alarm.db')

cur = conn.cursor()

"""req="DROP table users"
cur.execute(req)
req="create table users (id integer primary key autoincrement, name varchar(20) not null, email varchar(20) not null, password varchar(15) not null, telephone varchar(15) not null, avatar varchar(15) default 'user.png', created_at timestamp not null, deleted_at timestamp)"
cur.execute(req)"""

"""req = "INSERT INTO users (name, email, password, telephone, created_at) VALUES('nelson', 'nelson@gmail.com', 'password', '243020071', '2022-03-10')"
cur.execute(req)"""

"""req="DROP table alarms"
cur.execute(req)
req="create table alarms (id integer primary key autoincrement, name varchar(20) not null, heure date not null, is_active boolean not null, created_at timestamp not null)"
cur.execute(req)"""

"""req = "INSERT INTO alarms (name, heure, statut, created_at) VALUES('ecole', '06:00', 'active', '2022-03-10')"
cur.execute(req)"""

"""req = "DELETE FROM alarms WHERE id = 9"
cur.execute(req)"""

"""req = "UPDATE users SET avatar='user.png' WHERE id=5 "
cur.execute(req)"""

"""request = "SELECT avatar, name, email , telephone FROM users "
donnees = cur.execute( request )
donnees = donnees.fetchall()
title=['avatar', 'name', 'email', 'telephone']

c={}
a = []
for row in donnees:
    for i in range(len(row)):
        c[title[i]] = row[i]
    a.append(c.copy())


print(a)
print(len(a))
for row in a:
    print(row['avatar'])
"""





conn.commit()
conn.close()

print(datetime.now())