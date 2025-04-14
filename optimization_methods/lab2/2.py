import numpy as np
import matplotlib.pyplot as plt

def f(x):
    x1, x2 = x
    return x1 ** 2 + 8 * x2 ** 2 - x1 * x2 + x1

def grad_f(x):
    x1, x2 = x
    return np.array([2 * x1 - x2 + 1, 16 * x2 - x1])

def hessian_f(x):
    return np.array([
        [2, -1],
        [-1, 16]
    ])

def newton_method(x0, eps1, eps2, M):
    k = 0
    xk = np.array(x0)
    fx_prev = f(xk)

    path = [xk.copy()]

    while True:
        grad = grad_f(xk)
        norm_grad = np.linalg.norm(grad)

        if norm_grad < eps1:
            condition = "||grad(f(xk))|| < ε1"
            break

        if k >= M:
            condition = "k >= M"
            break

        H = hessian_f(xk)
        try:
            H_inv = np.linalg.inv(H)
        except np.linalg.LinAlgError:
            H_inv = None

        if H_inv is not None and np.all(np.linalg.eigvals(H_inv) > 0):
            d = - H_inv @ grad
        else:
            d = - grad

        t = 1
        x_next = xk + t * d
        fx_next = f(x_next)

        if (np.linalg.norm(x_next - xk) < eps2 and
                abs(fx_next - fx_prev) < eps2):
            xk = x_next
            condition = "||xk+1 - xk|| < ε2 и |f(xk+1) – f(xk)| < ε2"
            path.append(xk.copy())
            break

        xk = x_next
        fx_prev = fx_next
        path.append(xk.copy())
        k += 1

    return xk, f(xk), condition, k, np.array(path)

x0 = [1.5, 0.1]
eps1 = 0.1
eps2 = 0.15
M = 10

x_star, f_star, stop_condition, iterations, path = newton_method(x0, eps1, eps2, M)

print(f"x* = {x_star}")
print(f"f(x*) = {f_star}")
print(f"Условие остановки: {stop_condition}")
print(f"Количество итераций: {iterations + 1}")

x1_vals = np.linspace(-1, 2.5, 400)
x2_vals = np.linspace(-0.5, 1.5, 400)
X1, X2 = np.meshgrid(x1_vals, x2_vals)
Z = f((X1, X2))

plt.figure(figsize=(8, 6))
cp = plt.contour(X1, X2, Z, levels=50, cmap='viridis')
plt.colorbar(cp)
plt.plot(path[:, 0], path[:, 1], 'r.-', label='Траектория спуска')
plt.scatter(x0[0], x0[1], color='blue', label='Начальная точка')
plt.scatter(x_star[0], x_star[1], color='red', marker='*', s=100, label='Минимум')
plt.title("Линии уровня и траектория метода Ньютона")
plt.xlabel("x1")
plt.ylabel("x2")
plt.legend()
plt.grid(True)
plt.show()

fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(X1, X2, Z, cmap='viridis', alpha=0.9, edgecolor='none')
ax.set_title("3D-график функции")
ax.set_xlabel("x1")
ax.set_ylabel("x2")
ax.set_zlabel("f(x1, x2)")
plt.show()
