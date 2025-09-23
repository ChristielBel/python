import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
matplotlib.use('TkAgg')
import numpy as np

df = pd.read_csv("AirQualityUCI.csv", sep=";")
df = df.dropna(axis=1, how="all")
for col in df.columns[2:]:
    df[col] = df[col].astype(str).str.replace(",", ".").astype(float)
df = df.replace(-200, np.nan)
df["Time"] = df["Time"].str.replace(".", ":", regex=False)
df["Datetime"] = pd.to_datetime(df["Date"] + " " + df["Time"], format="%d/%m/%Y %H:%M:%S")

# 1

bins = pd.cut(df["CO(GT)"].dropna(), bins=10)

counts = bins.value_counts().sort_index()

counts.plot(kind="bar", figsize=(8,5), color="skyblue", edgecolor="black")
plt.xlabel("Интервалы CO(GT) (мг/м³)")
plt.ylabel("Количество наблюдений")
plt.title("Распределение концентрации CO(GT)")
plt.show()

# 2

counts.plot(kind="bar", figsize=(8,5), color="lightgreen", edgecolor="black", logy=True)
plt.xlabel("Интервалы CO(GT) (мг/м³)")
plt.ylabel("Количество наблюдений (лог)")
plt.title("Распределение CO(GT)")
plt.show()

# 3-5

mean_co = df["CO(GT)"].mean()

above = df[df["CO(GT)"] > mean_co]["T"]
below = df[df["CO(GT)"] <= mean_co]["T"]

plt.hist(above, bins=20, alpha=0.5, color="red")
plt.hist(below, bins=20, alpha=0.5, color="blue")

plt.xlabel("Температура (°C)")
plt.ylabel("Частота")
plt.title("Распределение температуры при разных уровнях CO")
plt.show()

# 4

plt.hist(above, bins=20, alpha=0.5, density=True, color="red")
plt.hist(below, bins=20, alpha=0.5, density=True, color="blue")

plt.xlabel("Температура (°C)")
plt.ylabel("Плотность распределения")
plt.title("Распределение температуры при разных уровнях CO")
plt.show()

# 5

plt.hist(above, bins=20, alpha=0.5, density=True, color="red", label="CO выше среднего")
plt.hist(below, bins=20, alpha=0.5, density=True, color="blue", label="CO ниже среднего")

plt.xlabel("Температура (°C)")
plt.ylabel("Плотность распределения")
plt.title("Распределение температуры при разных уровнях CO")
plt.legend()
plt.show()

# 6

def time_of_day(hour):
    if 6 <= hour < 12:
        return "Утро"
    elif 12 <= hour < 18:
        return "День"
    elif 18 <= hour < 24:
        return "Вечер"
    else:
        return "Ночь"

df["Period"] = df["Datetime"].dt.hour.apply(time_of_day)

plt.figure(figsize=(8,5))
for period, color in zip(["Утро", "День", "Вечер", "Ночь"], ["orange","green","purple","blue"]):
    subset = df[df["Period"] == period]["C6H6(GT)"]
    plt.hist(subset, bins=20, alpha=0.5, label=period, color=color)

plt.xlabel("C6H6(GT) (мкг/м³)")
plt.ylabel("Частота")
plt.title("Распределение бензола по времени суток")
plt.legend()
plt.show()

# 7

df.boxplot(column="CO(GT)", by="Period", figsize=(8,6))
plt.xlabel("Время суток")
plt.ylabel("CO(GT) (мг/м³)")
plt.title("CO(GT) в зависимости от времени суток")
plt.suptitle("")
plt.show()

# 8

plt.figure(figsize=(8,5))
plt.scatter(df["T"], df["CO(GT)"], alpha=0.5, label="CO(GT)")
plt.scatter(df["T"], df["C6H6(GT)"], alpha=0.5, label="C6H6(GT)")
plt.scatter(df["T"], df["NOx(GT)"], alpha=0.5, label="NOx(GT)")
plt.xlabel("Температура (°C)")
plt.ylabel("Концентрация")
plt.title("Зависимость загрязнений от температуры")
plt.legend()
plt.show()

# 9

df_area = df[["Datetime","CO(GT)","C6H6(GT)","NOx(GT)"]].dropna().set_index("Datetime")
df_area.iloc[:200].plot.area(figsize=(12,6), alpha=0.6)
plt.ylabel("Концентрация")
plt.title("Изменение загрязнений во времени")
plt.show()
