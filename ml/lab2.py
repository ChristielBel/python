import pandas as pd

# 1
df = pd.read_csv(
    "AirQualityUCI.csv",
    sep=";",
    decimal=",",
    usecols=lambda x: x not in ["Unnamed: 15", "Unnamed: 16"]
)

# 2
print("Первые 5 строки:\n", df.head())
print("Последние 5 строки:\n", df.tail())

# 3
print("Общее количество строк и столбцов в DataFrame:\n", df.shape)

# 4
print("Столбцы:\n", df.columns.tolist())

# 5
print("Пропущенные значения:\n", df.isna().sum())

# 6
print("Основные статистические характеристики для числовых столбцов DataFrame:\n", df.describe())

# 7
print("Сводная информация о DataFrame:")
print(df.info())

# 8
print("Уникальные значения T:\n", df["T"].unique())
print("Количество уникальных:\n", df["T"].nunique())
print("Частота:\n", df["T"].value_counts())

# 9
print("CO(GT) > 3 & T < 20:\n", df[(df["CO(GT)"] > 3) & (df["T"] < 20)])

# 10
df["NOx_CO_ratio"] = df["NOx(GT)"] / df["CO(GT)"]

# 11
print("Размер после добавления NOx_CO_ratio:\n", df.shape)

# 12
print("Значение T, которое встречается чаще всего:\n", df["T"].mode()[0])

# 13
missingBenzol = df[df["C6H6(GT)"] == -200]
print("Строки с отсутствующим бензолом:\n", len(missingBenzol))
print(missingBenzol)

# 14
print("min CO при T > 25:\n", df[df["T"] > 25]["CO(GT)"].min())

# 15
print("RH > 90%:\n", len(df[df["RH"] > 90]))
print(df[df["RH"] > 90])

# 16
meanH = df[df["T"] > 20]["CO(GT)"].mean()
meanL = df[df["T"] <= 20]["CO(GT)"].mean()
print("Разница между средним уровнем CO выше и ниже 20 градусов:\n", round(meanH - meanL, 2))

# 17
df["High_Ozone"] = (df["PT08.S5(O3)"] > df["PT08.S5(O3)"].mean()).astype(int)

# 18
print("Наиболее распространненный NOx(GT):\n", df["NOx(GT)"].mode()[0])

# 19
c6h6nox = (df["C6H6(GT)"] > df["C6H6(GT)"].mean()) & (df["NOx(GT)"] > df["NOx(GT)"].mean())
print("Измерения, в которых C6H6 и NOx выше средних:\n", df[c6h6nox].shape[0])

# 20
print("max T при NO2 < 50:\n", df[df["NO2(GT)"] < 50]["T"].max())

# 21
maxCO = df["CO(GT)"] > df["CO(GT)"].mean()
print("CO выше среднего:\n", maxCO.sum())
print(df[maxCO])

# 22
mean_T = df["T"].mean()
groupH = df[df["T"] > mean_T]["C6H6(GT)"].mean()
groupL = df[df["T"] <= mean_T]["C6H6(GT)"].mean()
print("Среднее C6H6 при T выше среднего:\n", groupH)
print("Среднее C6H6 при T ниже среднего:\n", groupL)
