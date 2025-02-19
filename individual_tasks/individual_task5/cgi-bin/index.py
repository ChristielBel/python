#!/usr/bin/env python3
# -*- coding: utf-8 -*-
print("Content-Type: text/html; charset=utf-8")
print()

print("""
<html>
<head>
    <title>Управление базой данных</title>
</head>
<body>
    <h1>Добро пожаловать!</h1>
    <p>Выберите действие:</p>
    <ul>
        <li><a href="/cgi-bin/show_tables.py">Просмотр содержимого таблиц</a></li>
        <li><a href="/cgi-bin/add_to_spacestations.py">Добавить запись в SpaceStations</a></li>
        <li><a href="/cgi-bin/add_to_satellites.py">Добавить запись в Satellites</a></li>
        <li><a href="/cgi-bin/add_to_astronauts.py">Добавить запись в Astronauts</a></li>
    </ul>
</body>
</html>
""")
