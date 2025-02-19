#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi
import sqlite3

print("Content-Type: text/html; charset=utf-8")
print()

form = cgi.FieldStorage()
name = form.getvalue("name")
station_id = form.getvalue("station_id")
missions_count = form.getvalue("missions_count")

if name and station_id and missions_count:
    conn = sqlite3.connect("space.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Astronauts (name, station_id, missions_count) VALUES (?, ?, ?)",
                   (name, int(station_id), int(missions_count)))
    conn.commit()
    conn.close()
    print("<p>Новая запись успешно добавлена!</p>")

print("""
<html>
<head><title>Добавить астронавта</title></head>
<body>
<h1>Добавить запись в таблицу Astronauts</h1>
<form method="post">
    <label>Имя астронавта:</label> <input type="text" name="name"><br>
    <label>ID станции:</label> <input type="text" name="station_id"><br>
    <label>Количество миссий:</label> <input type="text" name="missions_count"><br>
    <input type="submit" value="Добавить">
</form>
<br>
<a href="/cgi-bin/show_tables.py">Назад к списку данных</a>
</body>
</html>
""")
