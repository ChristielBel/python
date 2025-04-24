import random

raw_data = [
    ["Варданян", 1, 1, 60, 79, 60, 72, 63, 1.00],
    ["Горбунов", 1, 0, 60, 61, 30, 5, 17, 0.00],
    ["Гуменюк", 0, 0, 60, 61, 30, 66, 58, 0.00],
    ["Егоров", 1, 1, 85, 78, 72, 70, 85, 1.25],
    ["Захарова", 0, 1, 65, 78, 60, 67, 65, 1.00],
    ["Иванова", 0, 1, 60, 78, 77, 81, 60, 1.25],
    ["Ишонина", 0, 1, 55, 79, 56, 69, 72, 0.00],
    ["Климчук", 1, 0, 55, 56, 50, 56, 60, 0.00],
    ["Лисовский", 1, 0, 55, 60, 21, 64, 50, 0.00],
    ["Нетреба", 1, 0, 60, 56, 30, 16, 17, 0.00],
    ["Остапова", 0, 1, 85, 89, 85, 92, 85, 1.75],
    ["Пашкова", 0, 1, 60, 88, 76, 66, 60, 1.25],
    ["Попов", 1, 0, 55, 64, 0, 9, 50, 0.00],
    ["Сазон", 0, 1, 80, 83, 62, 72, 72, 1.25],
    ["Степоненко", 1, 0, 55, 10, 3, 8, 50, 0.00],
    ["Терентьева", 0, 1, 60, 67, 57, 64, 50, 0.00],
    ["Титов", 1, 1, 75, 98, 86, 82, 85, 1.50],
    ["Чернова", 0, 1, 85, 85, 81, 85, 72, 1.25],
    ["Четкин", 1, 1, 80, 56, 50, 69, 50, 0.00],
    ["Шевченко", 1, 0, 55, 60, 30, 8, 60, 0.00],
]

data = []
for row in raw_data:
    data.append({
        "Фамилия": row[0],
        "Пол": row[1],
        "Зачеты": row[2],
        "История": row[3],
        "ИнжГраф": row[4],
        "Матем": row[5],
        "Химия": row[6],
        "Физика": row[7],
        "Стипендия": row[8]
    })

def normalize(column):
    values = [row[column] for row in data]
    min_v = min(values)
    max_v = max(values)
    for row in data:
        if max_v - min_v != 0:
            row[column] = (row[column] - min_v) / (max_v - min_v)
        else:
            row[column] = 0.0

columns_to_normalize = ["История", "ИнжГраф", "Матем", "Химия", "Физика"]
for col in columns_to_normalize:
    normalize(col)

inputs = []
for row in data:
    inputs.append([
        row["Пол"],
        row["Зачеты"],
        row["История"],
        row["ИнжГраф"],
        row["Матем"],
        row["Химия"],
        row["Физика"]
    ])

num_inputs = 7
num_clusters = 4
weights = [[random.random() for _ in range(num_inputs)] for _ in range(num_clusters)]

def distance(v1, v2):
    return sum((a - b) ** 2 for a, b in zip(v1, v2)) ** 0.5

learning_rate = 0.30
for epoch in range(6):
    for idx in range(len(inputs)):
        x = inputs[idx]
        distances = [distance(x, w) for w in weights]
        winner = distances.index(min(distances))
        for i in range(num_inputs):
            weights[winner][i] += learning_rate * (x[i] - weights[winner][i])
    learning_rate -= 0.05

clusters = [[] for _ in range(num_clusters)]
for i, x in enumerate(inputs):
    distances = [distance(x, w) for w in weights]
    winner = distances.index(min(distances))
    clusters[winner].append(i)

print("Результаты кластеризации студентов:\n")
for i, s in enumerate(clusters):
    print(f"Кластер {i + 1}:")
    if len(s) == 0:
        print("  Пустой кластер\n")
        continue
    for j in s:
        print(f"  {data[j]['Фамилия']} (стипендия: {data[j]['Стипендия']})")
    avg = sum([data[j]['Стипендия'] for j in s]) / len(s)
    print(f"  Средняя стипендия по кластеру: {avg:.2f}\n")

print("\nСписок студентов с указанием их кластера:\n")
for i, cluster in enumerate(clusters):
    for j in cluster:
        print(f"{data[j]['Фамилия']} — кластер {i + 1}, стипендия: {data[j]['Стипендия']}")
