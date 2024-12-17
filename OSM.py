import xml.etree.ElementTree as ET
from collections import defaultdict

def parse_osm(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    benches = []
    pharmacies = set()

    # Собираем данные о скамейках и аптеках
    for element in root.findall(".//node"):
        tags = {tag.attrib['k']: tag.attrib['v'] for tag in element.findall("tag")}

        # Если это скамейка
        if tags.get("amenity") == "bench":
            bench = {
                "id": element.attrib["id"],
                "lat": float(element.attrib["lat"]),
                "lon": float(element.attrib["lon"]),
                "type": tags.get("bench:type", "unknown")
            }
            benches.append(bench)

        # Если это аптека
        if tags.get("amenity") == "pharmacy":
            pharmacy = (float(element.attrib["lat"]), float(element.attrib["lon"]))
            pharmacies.add(pharmacy)

    return benches, pharmacies

# Проверка на близость скамейки и аптеки
def is_near(lat1, lon1, lat2, lon2, threshold=0.001):
    return abs(lat1 - lat2) <= threshold and abs(lon1 - lon2) <= threshold

def analyze_benches(file_path):
    benches, pharmacies = parse_osm(file_path)

    total_benches = len(benches)
    benches_by_type = defaultdict(int)
    benches_near_pharmacies = 0

    for bench in benches:
        benches_by_type[bench["type"]] += 1

        # Проверяем близость к аптеке
        for pharmacy in pharmacies:
            if is_near(bench["lat"], bench["lon"], pharmacy[0], pharmacy[1]):
                benches_near_pharmacies += 1
                break

    return total_benches, benches_by_type, benches_near_pharmacies


# Пример использования
files = ["2.osm", "2 - 2.osm"]
for file in files:
    print(f"Обрабатываем файл: {file}")
    total_benches, benches_by_type, benches_near_pharmacies = analyze_benches(file)

    print(f"Общее количество скамеек: {total_benches}")
    print("Количество скамеек по типу:")
    for bench_type, count in benches_by_type.items():
        print(f"  {bench_type}: {count}")
    print(f"Количество скамеек рядом с аптеками: {benches_near_pharmacies}")
