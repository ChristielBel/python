#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi
import sqlite3

print("Content-Type: text/html; charset=utf-8")
print()

form = cgi.FieldStorage()
name = form.getvalue("name")
launch_year = form.getvalue("launch_year")
country = form.getvalue("country")

if name and launch_year and country:
    conn = sqlite3.connect("space.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO SpaceStations (name, launch_year, country) VALUES (?, ?, ?)",
                   (name, int(launch_year), country))
    conn.commit()
    conn.close()
    print("<p>Новая запись успешно добавлена!</p>")

print("""
<html>
<head><title>Добавить станцию</title></head>
<body>
<h1>Добавить запись в таблицу SpaceStations</h1>
<form method="post">
    <label>Название станции:</label> <input type="text" name="name"><br>
    <label>Год запуска:</label> <input type="text" name="launch_year"><br>
    <label>Страна:</label> <input type="text" name="country"><br>
    <input type="submit" value="Добавить">
</form>
<br>
<a href="/cgi-bin/show_tables.py">Назад к списку данных</a>
</body>
</html>
""")
