#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi
import sqlite3

print("Content-Type: text/html; charset=utf-8")
print()

form = cgi.FieldStorage()
name = form.getvalue("name")
station_id = form.getvalue("station_id")
orbit_type = form.getvalue("orbit_type")

if name and station_id and orbit_type:
    conn = sqlite3.connect("space.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Satellites (name, station_id, orbit_type) VALUES (?, ?, ?)",
                   (name, int(station_id), orbit_type))
    conn.commit()
    conn.close()
    print("<p>Новая запись успешно добавлена!</p>")

print("""
<html>
<head><title>Добавить спутник</title></head>
<body>
<h1>Добавить запись в таблицу Satellites</h1>
<form method="post">
    <label>Название спутника:</label> <input type="text" name="name"><br>
    <label>ID станции:</label> <input type="text" name="station_id"><br>
    <label>Тип орбиты:</label> <input type="text" name="orbit_type"><br>
    <input type="submit" value="Добавить">
</form>
<br>
<a href="/cgi-bin/show_tables.py">Назад к списку данных</a>
</body>
</html>
""")
