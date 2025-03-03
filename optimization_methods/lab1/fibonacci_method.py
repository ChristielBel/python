import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

eps = 0.2
l = 0.5
a = -6
b = 4
k = -1

def f(x: float) -> float:
    return x ** 2 + 6 * x + 13

def fibbonacci_sequence(L, l):
    ans = [1]
    cur = 0
    while ans[-1] + cur < L / l:
        ans.append(cur + ans[-1])
        cur = ans[-2]
    ans.append(cur + ans[-1])
    return ans

F = fibbonacci_sequence(abs(b - a), l)
N = len(F) - 1

yk = a + (F[N-2]/F[N])*(b-a)
zk = a + (F[N-1]/F[N])*(b-a)

while k != (N - 3):
    k += 1
    print(k)
    fy = f(yk)
    fz = f(zk)
    print(f"y = {yk}, z = {zk}")
    print(f"f(y) = {fy}, f(z) = {fz}")
    if fy <= fz:
       b = zk
       zk = yk
       yk = a + (F[N-k-3]/F[N-k-1])*(b-a)
    else:
        a = yk
        yk = zk
        zk = a + (F[N-k-2]/F[N-k-1])*(b-a)
    print(f"L{k+2}[{a},{b}]")

zk = zk + eps
fy = f(yk)
fz = f(zk)
if fy <= fz:
    b = zk
else:
    a = yk

print(f"y = {yk}, z = {zk}")
print(f"f(y) = {fy}, f(z) = {fz}")
print(f"L{N}[{a},{b}]")

x_min = (a+b)/2
fx_min = f(x_min)
R = 1/F[N]


print("\nРезультаты:")
print("=" * 50)
print(f"Количество итераций: {k}")
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
plt.title("График функции и точка минимума (метод Фибоначчи)")
plt.legend()
plt.grid(True)
plt.show()
