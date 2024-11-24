import sqlite3
from xml.dom.minidom import Document, parse
import os
from http.server import HTTPServer, CGIHTTPRequestHandler


# ====== Создание и заполнение базы данных ======
def create_database():
    conn = sqlite3.connect("space.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS SpaceStations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        launch_year INTEGER NOT NULL,
        country TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Satellites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        station_id INTEGER NOT NULL,
        orbit_type TEXT NOT NULL,
        FOREIGN KEY (station_id) REFERENCES SpaceStations(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Astronauts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        station_id INTEGER NOT NULL,
        missions_count INTEGER NOT NULL,
        FOREIGN KEY (station_id) REFERENCES SpaceStations(id)
    )
    """)

    conn.commit()
    conn.close()


def populate_data():
    conn = sqlite3.connect("space.db")
    cursor = conn.cursor()

    space_stations = [
        ("International Space Station", 1998, "International"),
        ("Mir", 1986, "Russia"),
        ("Tiangong", 2021, "China"),
    ]
    satellites = [
        ("Hubble", 1, "Low Earth Orbit"),
        ("Sputnik", 2, "Low Earth Orbit"),
        ("Tianhe Core", 3, "Low Earth Orbit"),
    ]
    astronauts = [
        ("Yuri Gagarin", 2, 1),
        ("Valentina Tereshkova", 2, 1),
        ("Chris Hadfield", 1, 3),
    ]

    cursor.executemany("INSERT INTO SpaceStations (name, launch_year, country) VALUES (?, ?, ?)", space_stations)
    cursor.executemany("INSERT INTO Satellites (name, station_id, orbit_type) VALUES (?, ?, ?)", satellites)
    cursor.executemany("INSERT INTO Astronauts (name, station_id, missions_count) VALUES (?, ?, ?)", astronauts)

    conn.commit()
    conn.close()

def run_queries():
    conn = sqlite3.connect("space.db")
    cursor = conn.cursor()

    # Пример запросов
    print("Список всех космических станций:")
    for row in cursor.execute("SELECT * FROM SpaceStations"):
        print(row)

    print("\nСпутники станции ISS:")
    for row in cursor.execute("""
        SELECT Satellites.name
        FROM Satellites
        JOIN SpaceStations ON Satellites.station_id = SpaceStations.id
        WHERE SpaceStations.name = 'International Space Station'
    """):
        print(row)

    print("\nАстронавты с более чем одной миссией:")
    for row in cursor.execute("SELECT name, missions_count FROM Astronauts WHERE missions_count > 1"):
        print(row)

    conn.close()

def export_to_xml(table_name, xml_file_name):
    conn = sqlite3.connect("space.db")
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]

    doc = Document()
    root = doc.createElement("Table")
    root.setAttribute("name", table_name)
    doc.appendChild(root)

    for row in rows:
        row_element = doc.createElement("Row")
        for col_name, col_value in zip(column_names, row):
            col_element = doc.createElement(col_name)
            col_element.appendChild(doc.createTextNode(str(col_value)))
            row_element.appendChild(col_element)
        root.appendChild(row_element)

    with open(xml_file_name, "w", encoding="utf-8") as f:
        f.write(doc.toprettyxml(indent="  "))

    print(f"Таблица {table_name} успешно экспортирована в {xml_file_name}")
    conn.close()


def import_from_xml(table_name, xml_file_name):
    conn = sqlite3.connect("space.db")
    cursor = conn.cursor()

    doc = parse(xml_file_name)
    root = doc.documentElement

    rows = root.getElementsByTagName("Row")
    if not rows:
        print(f"Файл {xml_file_name} не содержит данных для импорта.")
        return

    column_names = [child.tagName for child in rows[0].childNodes if child.nodeType == child.ELEMENT_NODE]
    placeholders = ", ".join(["?"] * len(column_names))
    query = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({placeholders})"

    for row in rows:
        values = [child.firstChild.nodeValue for child in row.childNodes if child.nodeType == child.ELEMENT_NODE]
        cursor.execute(query, values)

    conn.commit()
    print(f"Данные из {xml_file_name} успешно импортированы в таблицу {table_name}.")
    conn.close()


class CustomHandler(CGIHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/cgi-bin/" or self.path == "/cgi-bin":
            self.path = "/cgi-bin/index.py"
        super().do_GET()

if __name__ == "__main__":
    create_database()
    populate_data()
    run_queries()

    export_to_xml("SpaceStations", "space_stations.xml")
    export_to_xml("Satellites", "satellites.xml")
    export_to_xml("Astronauts", "astronauts.xml")

    conn = sqlite3.connect("space.db")
    conn.execute("DELETE FROM SpaceStations")
    conn.commit()
    conn.close()
    import_from_xml("SpaceStations", "space_stations.xml")

    print("Запуск CGI-сервера на http://localhost:8000/")
    server_address = ("", 8000)
    os.chdir(".")
    http_server = HTTPServer(server_address, CustomHandler)
    http_server.serve_forever()
