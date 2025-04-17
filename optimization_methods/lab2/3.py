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

def hessian_f(x):
    return np.array([
        [2, -1],
        [-1, 16]
    ])

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

def newton_method(x0, eps1, eps2, M):
    xk = np.array(x0, dtype=float)
    k = 0
    fx_prev = f(xk)
    path = [xk.copy()]

    while True:
        print(f"k = {k}")
        print(f"x{k} = {xk}")
        grad = grad_f(xk)
        norm_grad = np.linalg.norm(grad)

        print(f"grad(f(x{k})) = {grad}")
        print(f"||grad(f(x{k}))|| = {norm_grad}")

        if norm_grad < eps1:
            return xk, f(xk), "||grad(f(xk))|| < ε1", k, np.array(path)

        if k >= M:
            return xk, f(xk), "k ≥ M", k, np.array(path)

        H = hessian_f(xk)
        try:
            H_inv = np.linalg.inv(H)
        except np.linalg.LinAlgError:
            H_inv = None

        if H_inv is not None and np.all(np.linalg.eigvals(H_inv) > 0):
            dk = - H_inv @ grad
        else:
            dk = - grad

        phi = lambda t: f(xk + t * dk)
        tk = golden_ratio_search(phi)

        print(f"H(x{k}) = {H}")
        print(f"H(x{k}^(-1)) = {H_inv}")

        print(f"d{k} = {dk}")
        print(f"t{k} = {tk}")

        x_next = xk + tk * dk
        fx = f(x_next)

        print(f"||x{k + 1} - x{k}|| = {np.linalg.norm(x_next - xk)}")

        if np.linalg.norm(x_next - xk) < eps2 and abs(fx - fx_prev) < eps2:
            path.append(x_next.copy())
            print(f"|f(x{k + 1}) – f(x{k})| = {abs(fx - fx_prev)}")
            return x_next, fx, "||xk+1 - xk|| < ε2 и |f(xk+1) – f(xk)| < ε2", k, np.array(path)

        xk = x_next
        fx_prev = fx
        path.append(xk.copy())
        k += 1

x0 = [1.5, 0.1]
eps1 = 0.1
eps2 = 0.15
M = 10

x_min, f_min, stop_cond, iterations, path = newton_method(x0, eps1, eps2, M)

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
