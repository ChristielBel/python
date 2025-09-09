import numpy as np

#1
a = np.zeros(10)
print("Вектор из нулей:", a)
print("\t")

#2
b = a.copy()
b[4] = 1
print("Вектор с пятым элементом = 1:", b)
print("\t")

#3
c = np.random.randint(0, 15, 20)
nonzero_ind = np.nonzero(c)
print("Исходный вектор:", c)
print("Индексы ненулевых элементов:", nonzero_ind[0])
print("Ненулевые элементы:", c[nonzero_ind])
print("\t")

#4
d = np.random.rand(3, 3, 3)
print("Массив 3x3x3:")
for i, layer in enumerate(d):
    print(f"Слой {i+1}:")
    print(layer)
print("\t")

#5
aa = np.random.randint(1, 10, 10)
avr = np.mean(aa)
print("Вектор:", aa)
print("Среднее значение:", round(avr, 2))
print("\t")

#6
a11 = np.random.randint(1, 10, (5, 3))
a22 = np.random.randint(1, 10, (3, 2))
multi_a11_a22 = a11 @ a22
print("Матрица A (5x3):")
print(a11)
print("\nМатрица B (3x2):")
print(a22)
print("\nПроизведение A @ B:")
print(multi_a11_a22)
print("\t")

#7
b11 = np.random.randint(1, 10, (4, 4))
b22 = np.random.randint(1, 10, (4, 4))
multi_b11_b22 = b11 @ b22
diagonal = np.diag(multi_b11_b22)
print("Матрица A (4x4):")
print(b11)
print("\nМатрица B (4x4):")
print(b22)
print("\nПроизведение A @ B:")
print(multi_b11_b22)
print("\nДиагональные элементы произведения:", diagonal)
print("\t")

#8
e = np.random.randint(1, 100, 20)
max_ind = np.argmax(e)
max_val = e[max_ind]
e_modified = e.copy()
e_modified[max_ind] = 0
print("Исходный вектор:", e)
print(f"Максимальный элемент: {max_val} (индекс {max_ind})")
print("Вектор после замены:", e_modified)
print("\t")

#9
f = np.random.randint(1, 10, 20)
unique_f = np.unique(f)
print("Исходный вектор:", f)
print("Уникальные значения:", unique_f)
print("\t")

#10
g = np.random.randint(1, 10, (4, 3))
row_means = np.mean(g, axis=1, keepdims=True)
g_normalized = g - row_means
print("Исходная матрица:")
print(g)
print("\nСредние значения по строкам:", row_means.flatten())
print("\nМатрица после вычитания среднего:")
print(g_normalized)
print("\t")

#11
h = np.random.randint(1, 10, (3, 3))
h_swapped = h.copy()
h_swapped[[0, 1]] = h_swapped[[1, 0]]
print("Исходная матрица:")
print(h)
print("\nМатрица после замены строк 0 и 1:")
print(h_swapped)
print("\t")

#12
i = np.random.randint(1, 100, 20)
n = 3
max_numbers = i[np.argpartition(i, -n)[-n:]]
print("Исходный вектор:", i)
print(f"Топ-{n} наибольших значений:", sorted(max_numbers, reverse=True))
print("\t")

#13
j = np.random.randint(1, 10, (5, 5))
sum_of_rows = np.sum(j, axis=1)
print("Матрица 5x5:")
print(j)
print("\nСуммы по строкам:", sum_of_rows)
print("\t")

#14
k = np.random.uniform(-1, 1, 10)
k_modified = k.copy()
k_modified[k < 0] = -1
k_modified[k > 0] = 1
print("Исходный вектор:", np.round(k, 2))
print("Модифицированный вектор:", k_modified)
print("\t")

#15
l = np.random.randint(1, 101, 12)
parts = np.split(l, 3)
sums = [np.sum(part) for part in parts]
print("Исходный вектор:", l)
for i, (part, s) in enumerate(zip(parts, sums), 1):
    print(f"Часть {i}: {part} -> Сумма: {s}")
print("Все суммы:", sums)
print("\t")
