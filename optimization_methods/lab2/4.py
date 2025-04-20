import numpy as np
import math
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

def f(x):
    x1, x2 = x
    return x1**2 + 8 * x2**2 - x1 * x2 + x1

def grad_f(x):
    x1, x2 = x
    return np.array([2 * x1 - x2 + 1, 16 * x2 - x1])

def golden_ratio_search(phi, a=0, b=1, l=1e-4):
    yk = a + ((3 - math.sqrt(5)) / 2) * (b - a)
    zk = a + b - yk

    while abs(b - a) > l:
        fy = phi(yk)
        fz = phi(zk)
        if fy <= fz:
            b = zk
            zk = yk
            yk = a + b - yk
        else:
            a = yk
            yk = zk
            zk = a + b - zk

    return (a + b) / 2

def fletcher_reeves_method(x0, eps1, eps2, M):
    xk = np.array(x0, dtype=float)
    grad_k = grad_f(xk)
    direction = -grad_k
    fx_prev = f(xk)
    k = 0
    stop_counter = 0
    path = [xk.copy()]

    while True:
        if np.linalg.norm(grad_k) < eps1:
            return xk, f(xk), "||grad(f(xk))|| < ε1", k, np.array(path)

        if k >= M:
            return xk, f(xk), "k ≥ M", k, np.array(path)

        phi = lambda t: f(xk + t * direction)
        tk = golden_ratio_search(phi)

        x_next = xk + tk * direction
        grad_next = grad_f(x_next)
        fx = f(x_next)

        if np.linalg.norm(x_next - xk) < eps2 and abs(fx - fx_prev) < eps2:
            stop_counter += 1
            if stop_counter >= 2:
                path.append(x_next.copy())
                return x_next, fx, "||xk+1 - xk|| < ε2 и |f(xk+1) – f(xk)| < ε2", k, np.array(path)
        else:
            stop_counter = 0

        beta = np.dot(grad_next, grad_next) / np.dot(grad_k, grad_k)
        direction = -grad_next + beta * direction
        xk = x_next
        grad_k = grad_next
        fx_prev = fx
        path.append(xk.copy())
        k += 1

x0 = [1.5, 0.1]
eps1 = 0.1
eps2 = 0.15
M = 10

x_min, f_min, stop_cond, iterations, path = fletcher_reeves_method(x0, eps1, eps2, M)

print(f"x* = {x_min}")
print(f"f(x*) = {f_min}")
print(f"Условие остановки: {stop_cond}")
print(f"Количество итераций: {iterations + 1}")

x_vals = np.linspace(-2, 2.5, 400)
y_vals = np.linspace(-2, 2.5, 400)
X, Y = np.meshgrid(x_vals, y_vals)
Z = f([X, Y])

plt.style.use('dark_background')
fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none', alpha=0.8)
ax.set_title("3D-график функции")
ax.set_xlabel("x1")
ax.set_ylabel("x2")
ax.set_zlabel("f(x1, x2)")
plt.show()
