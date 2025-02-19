#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3

def fetch_table_data(table_name):
    conn = sqlite3.connect("space.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    conn.close()
    return column_names, rows

def generate_html_table(table_name, column_names, rows):
    html = f"<h2>{table_name}</h2>"
    html += '<table border="1" cellpadding="5" cellspacing="0">'
    html += "<tr>" + "".join(f"<th>{col}</th>" for col in column_names) + "</tr>"
    for row in rows:
        html += "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
    html += "</table>"
    html += f'<a href="/cgi-bin/add_to_{table_name.lower()}.py">Добавить запись в {table_name}</a>'
    return html

print("Content-Type: text/html; charset=utf-8")
print()

table_names = ["SpaceStations", "Satellites", "Astronauts"]

print("""
<html>
<head><title>Данные таблиц</title></head>
<body>
<h1>Содержимое базы данных</h1>
""")

for table in table_names:
    column_names, rows = fetch_table_data(table)
    print(generate_html_table(table, column_names, rows))

print("</body></html>")
