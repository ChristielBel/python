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

cmap = plt.get_cmap("viridis")
colors = cmap(np.linspace(0, 1, len(counts)))

counts.plot(kind="bar", figsize=(8,5), color=colors, edgecolor="black")
plt.xlabel("Интервалы CO(GT) (мг/м³)")
plt.ylabel("Количество наблюдений")
plt.title("Распределение концентрации CO(GT)")
plt.show()

# 2

counts.plot(kind="bar", figsize=(8,5), color=colors, edgecolor="black", logy=True)
plt.xlabel("Интервалы CO(GT) (мг/м³)")
plt.ylabel("Количество наблюдений (лог)")
plt.title("Распределение CO(GT)")
plt.show()

# 3

mean_co = df["CO(GT)"].mean()

above = df[df["CO(GT)"] > mean_co]["T"]
below = df[df["CO(GT)"] <= mean_co]["T"]

plt.hist(above, bins=20, alpha=0.6, density=True, color="#e63946", label="CO выше среднего")
plt.hist(below, bins=20, alpha=0.6, density=True, color="#457b9d", label="CO ниже среднего")

plt.xlabel("Температура (°C)")
plt.ylabel("Частота")
plt.title("Распределение температуры при разных уровнях CO")
plt.show()

# 4

plt.hist(above, bins=20, alpha=0.6, density=True, color="#e63946", label="CO выше среднего")
plt.hist(below, bins=20, alpha=0.6, density=True, color="#457b9d", label="CO ниже среднего")

plt.xlabel("Температура (°C)")
plt.ylabel("Плотность распределения")
plt.title("Распределение температуры при разных уровнях CO")
plt.show()

# 5

plt.hist(above, bins=20, alpha=0.6, density=True, color="#e63946", label="CO выше среднего")
plt.hist(below, bins=20, alpha=0.6, density=True, color="#457b9d", label="CO ниже среднего")

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

colors = ["#ffb703", "#e63946", "#1d3557", "#2a9d8f"]

plt.figure(figsize=(8,5))
for period, color in zip(["Утро", "День", "Вечер", "Ночь"], colors):
    subset = df[df["Period"] == period]["C6H6(GT)"]
    plt.hist(subset, bins=20, alpha=0.6, label=period, color=color)

plt.xlabel("C6H6(GT) (мкг/м³)")
plt.ylabel("Частота")
plt.title("Распределение бензола по времени суток")
plt.legend()
plt.show()

# 7

data = [df[df["Period"] == p]["CO(GT)"].dropna() for p in ["Утро", "День", "Вечер", "Ночь"]]

box_colors = ["#ffb703", "#8ecae6", "#219ebc", "#023047"]

bp = plt.boxplot(data, patch_artist=True, labels=["Утро","День","Вечер","Ночь"])

for patch, color in zip(bp["boxes"], box_colors):
    patch.set_facecolor(color)

plt.xlabel("Время суток")
plt.ylabel("CO(GT) (мг/м³)")
plt.title("CO(GT) в зависимости от времени суток")
plt.show()

# 8

plt.figure(figsize=(8,5))
plt.scatter(df["T"], df["CO(GT)"], alpha=0.5, label="CO(GT)", color="#e63946")
plt.scatter(df["T"], df["C6H6(GT)"], alpha=0.5, label="C6H6(GT)", color="#457b9d")
plt.scatter(df["T"], df["NOx(GT)"], alpha=0.5, label="NOx(GT)", color="#2a9d8f")

plt.xlabel("Температура (°C)")
plt.ylabel("Концентрация (логарифм)")
plt.title("Зависимость загрязнений от температуры")
plt.yscale("log")
plt.legend()
plt.show()

# 9

df_area = df[["Datetime","CO(GT)","C6H6(GT)","NOx(GT)"]].dropna().set_index("Datetime")

df_norm = df_area / df_area.max()
df_norm.iloc[:200].plot.area(figsize=(12,6), alpha=0.6, cmap="tab10")

plt.ylabel("Нормализованная концентрация")
plt.title("Изменение загрязнений во времени (нормализованные значения)")
plt.show()
