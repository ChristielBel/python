import math
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

l = 0.5
a = -6
b = 4
k = -1
N = 1


def f(x: float) -> float:
    return x ** 2 + 6 * x + 13


yk = a + ((3 - math.sqrt(5)) / 2) * (b - a)
zk = a + b - yk

while abs(b - a) > l:
    k += 1
    N += 1
    print(f"k = {k:d}")
    fy = f(yk)
    fz = f(zk)
    print(f"y = {yk}, z = {zk}")
    print(f"f(y) = {fy}, f(z) = {fz}")
    if fy <= fz:
        b = zk
        zk = yk
        yk = a + b - yk
    else:
        a = yk
        yk = zk
        zk = a + b - zk
    print(f"L{N}[{a},{b}]")

x_min = (a + b) / 2
fx_min = f(x_min)
R = 0.618 ** (N - 1)

print("\nРезультаты:")
print("=" * 50)
print(f"Количество итераций: {k-1}")
print(f"Индекс интервала неопределенности: {N}")
print(f"Интервал неопределенности L{N}: [{a:.4f}, {b:.4f}]")
print(f"Точка минимума: x* = {x_min:.4f}")
print(f"Значение функции в точке минимума: f(x*) = {fx_min:.4f}")
print(f"Сходимость R = {R:.6f}")
print("=" * 50)

x_vals = [i for i in range(-6, 5)]
y_vals = [f(i) for i in range(-6, 5)]

plt.style.use("seaborn-v0_8-darkgrid")
plt.figure(figsize=(8, 5))
plt.plot(x_vals, y_vals, label="f(x) = x² + 6x + 13", color="blue")
plt.scatter(x_min, fx_min, color="red", zorder=3, label=f"Минимум (x* = {x_min:.4f})")

plt.annotate(f"Минимум\n(x* = {x_min:.2f}, f(x*) = {fx_min:.2f})",
             xy=(x_min, fx_min),
             xytext=(x_min + 1, fx_min + 5),
             arrowprops=dict(facecolor='black', arrowstyle="->"))

plt.xlabel("x")
plt.ylabel("f(x)")
plt.title("График функции и точка минимума (метод  золотого сечения)")
plt.legend()
plt.grid(True)
plt.show()
