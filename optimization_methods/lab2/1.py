import numpy as np
import matplotlib.pyplot as plt

def f(x):
    x1, x2 = x
    return x1**2 + 8 * x2**2 - x1 * x2 + x1

def grad_f(x):
    x1, x2 = x
    return np.array([2 * x1 - x2 + 1, 16 * x2 - x1])

def t(x):
    x1, x2 = x
    numerator = (2 * x1 - x2 + 1) ** 2 + (16 * x2 - x1) ** 2
    denominator = (
        2 * (2 * x1 - x2 + 1) ** 2 +
        16 * (16 * x2 - x1) ** 2 -
        2 * (2 * x1 - x2 + 1) * (16 * x2 - x1)
    )
    return numerator / denominator

def steepest_gradient_descent(x0, eps1, eps2, M):
    xk = np.array(x0, dtype=float)
    k = 0
    f_prev = f(xk)
    stop_counter = 0

    path = [xk.copy()]

    while True:
        grad_k = grad_f(xk)

        if np.linalg.norm(grad_k) < eps1:
            return xk, f(xk), "||grad(f(xk))|| < eps1", k, path

        if k >= M:
            return xk, f(xk), "Достигнуто максимальное число итераций", k, path

        tk = t(xk)
        xk_new = xk - tk * grad_k
        f_new = f(xk_new)

        path.append(xk_new.copy())

        if np.linalg.norm(xk_new - xk) < eps2 and abs(f_new - f_prev) < eps2:
            stop_counter += 1
            if stop_counter >= 2:
                return xk_new, f_new, "Условия по ||xk+1 - xk|| и |f(xk+1) - f(xk)| выполнены дважды", k + 1, path
        else:
            stop_counter = 0

        xk = xk_new
        f_prev = f_new
        k += 1

x0 = [1.5, 0.1]
eps1 = 0.1
eps2 = 0.15
M = 10

x_star, f_star, stop_cond, iterations, path = steepest_gradient_descent(x0, eps1, eps2, M)
path = np.array(path)

print(f"x* = {x_star}")
print(f"f(x*) = {f_star}")
print(f"Условие остановки: {stop_cond}")
print(f"Количество итераций: {iterations}")

x_vals = np.linspace(-2, 2.5, 400)
y_vals = np.linspace(-2, 2.5, 400)
X, Y = np.meshgrid(x_vals, y_vals)
Z = f([X, Y])

plt.figure(figsize=(8, 6))
cp = plt.contour(X, Y, Z, levels=50, cmap='viridis')
plt.plot(path[:, 0], path[:, 1], marker='o', color='red', label='Траектория спуска')
plt.scatter(x_star[0], x_star[1], color='blue', label='x*')
plt.colorbar(cp)
plt.title('Контурный график функции и траектория спуска')
plt.xlabel('x1')
plt.ylabel('x2')
plt.legend()
plt.grid(True)
plt.show()

fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none')
ax.set_title('Поверхность функции f(x1, x2)')
ax.set_xlabel('x1')
ax.set_ylabel('x2')
ax.set_zlabel('f(x1, x2)')
plt.show()
