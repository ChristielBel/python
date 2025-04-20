import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import math

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

def golden_section_search(phi, a=0, b=1, l=1e-4):
    k = 0
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
        k += 1

    t_min = (a + b) / 2
    return t_min

def newton_raphson_method(x0, eps1, eps2, M):
    xk = np.array(x0, dtype=float)
    k = 0
    fx_prev = f(xk)
    path = [xk.copy()]

    while True:
        print(f"\nk = {k}")
        print(f"x{k} = {xk}")

        grad = grad_f(xk)
        norm_grad = np.linalg.norm(grad)

        print(f"grad(f(x{k})) = {grad}")
        print(f"||grad(f(x{k}))|| = {norm_grad}")

        if norm_grad < eps1:
            stop_reason = "||grad(f(xk))|| < ε1"
            break

        if k >= M:
            stop_reason = "k ≥ M"
            break

        H = hessian_f(xk)
        try:
            H_inv = np.linalg.inv(H)
            eigvals = np.linalg.eigvals(H_inv)
        except np.linalg.LinAlgError:
            H_inv = None
            eigvals = []

        if H_inv is not None and np.all(eigvals > 0):
            dk = - H_inv @ grad
        else:
            dk = - grad

        phi = lambda t: f(xk + t * dk)
        tk = golden_section_search(phi)

        print(f"H(x{k}) = \n{H}")
        print(f"H⁻¹(x{k}) = \n{H_inv if H_inv is not None else 'Not invertible'}")
        print(f"d{k} = {dk}")
        print(f"t{k} = {tk}")

        x_next = xk + tk * dk
        fx = f(x_next)

        print(f"||x{k + 1} - x{k}|| = {np.linalg.norm(x_next - xk)}")
        print(f"|f(x{k + 1}) – f(x{k})| = {abs(fx - fx_prev)}")

        if np.linalg.norm(x_next - xk) < eps2 and abs(fx - fx_prev) < eps2:
            xk = x_next
            stop_reason = "||xk+1 - xk|| < ε2 и |f(xk+1) – f(xk)| < ε2"
            path.append(xk.copy())
            break

        xk = x_next
        fx_prev = fx
        path.append(xk.copy())
        k += 1

    return xk, f(xk), stop_reason, k, np.array(path)

x0 = [1.5, 0.1]
eps1 = 0.1
eps2 = 0.15
M = 10

x_star, f_star, stop_cond, iterations, path = newton_raphson_method(x0, eps1, eps2, M)

print(f"x* = {x_star}")
print(f"f(x*) = {f_star}")
print(f"Условие остановки: {stop_cond}")
print(f"Количество итераций: {iterations + 1}")

x_vals = np.linspace(-2, 2.5, 400)
y_vals = np.linspace(-2, 2.5, 400)
X, Y = np.meshgrid(x_vals, y_vals)
Z = f([X, Y])

plt.style.use('dark_background')
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
ax.set_title("3D-график функции")
ax.set_xlabel("x1")
ax.set_ylabel("x2")
ax.set_zlabel("f(x1, x2)")
plt.show()
