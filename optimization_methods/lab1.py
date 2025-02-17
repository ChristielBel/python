import matplotlib.pyplot as plt

eps = 0.2
l = 0.5
a = -6
b = 4
k = 0
N = 2


def f(x: int) -> float:
    return x ** 2 + 6 * x + 13


def y():
    return (a + b - eps) / 2


def z():
    return (a + b + eps) / 2


def r(n):
    return 1 / (2 ** (n / 2))


while abs(b - a) > l:
    yk = y()
    zk = z()

    fy = f(yk)
    fz = f(zk)
    if fy <= fz:
        b = zk
    else:
        a = yk

    k += 1
    N += 2

x = (a + b) / 2
fx = f(x)
R = r(N)

print(f"Количество итераций k = {k}")
print(f"Индекс интервала неопределенности N = {N}")
print(f"Интервал неопределенности L{N} = [{a}, {b}]")
print(f"Точка минимума x* = {x}")
print(f"Значение в точке минимума f(x*) = {fx}")
print(f"Сходимость R = {R}")


x = [i for i in range(-6, 5)]
y = [f(i) for i in range(-6, 5)]

plt.grid()
plt.plot(x, y)
plt.show()
