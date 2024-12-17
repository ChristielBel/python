import csv
from datetime import datetime
import locale

locale.setlocale(locale.LC_TIME, 'Russian_Russia.1251')  # 'Russian_Russia.1251' или 'ru_RU.UTF-8'

def is_successful(row):
    """Проверка успешности прохождения теста."""
    if "Оценка/100,00" in row:
        score = row["Оценка/100,00"].replace(",", ".").strip()
        if len(score) > 3 and float(score) >= 60:
            return True
    if "Оценка/10,00" in row:
        score = row["Оценка/10,00"].replace(",", ".").strip()
        if len(score) > 2 and float(score) >= 6:
            return True
    return False

def find_unsuccessful_attempts(csv_file, given_date):
    given_date = datetime.strptime(given_date, "%d %B %Y")

    unsuccessful_attempts = []

    with open(csv_file, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            test_started_str = row["Тест начат"].strip()
            try:
                test_started = datetime.strptime(test_started_str, "%d %B %Y %H:%M")
            except ValueError:
                continue

            result = row["Состояние"]

            if result and result == "Завершено" \
                    and test_started and test_started > given_date \
                    and not is_successful(row):
                unsuccessful_attempts.append({
                    "name": f"{row['Фамилия']} {row['Имя']}",
                    "test_started": test_started
                })

    return unsuccessful_attempts

files = ["2 - 1.csv", "2 - 2.csv"]
given_date = "01 Январь 2017"

for file in files:
    print(file)
    unsuccessful_attempts = find_unsuccessful_attempts(file, given_date)

    print(f"Количество неудачных попыток после {given_date}: {len(unsuccessful_attempts)}")
    print("Список людей, не прошедших тест:")
    for attempt in unsuccessful_attempts:
        print(f"Имя: {attempt['name']}, Тест начат: {attempt['test_started']}")
