import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

def f(x):
    x1, x2 = x
    return x1**2 + 8 * x2**2 - x1 * x2 + x1

def grad_f(x):
    x1, x2 = x
    return np.array([2 * x1 - x2 + 1, 16 * x2 - x1])

def step_size(x):
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
    fx_prev = f(xk)
    counter = 0
    path = [xk.copy()]

    while True:
        grad = grad_f(xk)
        norm_grad = np.linalg.norm(grad)

        if norm_grad < eps1:
            return xk, f(xk), "||grad(f(xk))|| < ε1", k, np.array(path)

        if k >= M:
            return xk, f(xk), "k >= M", k, np.array(path)

        tk = step_size(xk)
        x_next = xk - tk * grad
        fx = f(x_next)
        path.append(x_next.copy())

        if np.linalg.norm(x_next - xk) < eps2 and abs(fx - fx_prev) < eps2:
            counter += 1
            if counter >= 2:
                return x_next, fx, "||xk+1 - xk|| < ε2 и |f(xk+1) – f(xk)| < ε2", k, np.array(path)
        else:
            counter = 0

        xk = x_next
        fx_prev = fx
        k += 1

x0 = [1.5, 0.1]
eps1 = 0.1
eps2 = 0.15
M = 10

x_min, f_min, stop_cond, iterations, path = steepest_gradient_descent(x0, eps1, eps2, M)

print(f"x* = {x_min}")
print(f"f(x*) = {f_min}")
print(f"Условие остановки: {stop_cond}")
print(f"Количество итераций: {iterations + 1}")

x_vals = np.linspace(-2, 2.5, 400)
y_vals = np.linspace(-2, 2.5, 400)
X, Y = np.meshgrid(x_vals, y_vals)
Z = f([X, Y])

fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
ax.set_title("3D-график функции")
ax.set_xlabel("x1")
ax.set_ylabel("x2")
ax.set_zlabel("f(x1, x2)")
plt.show()
