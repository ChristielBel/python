import numpy as np
import matplotlib.pyplot as plt
import math

def f(x):
    return x[0] ** 2 + 8 * x[1] ** 2 - x[0] * x[1] + x[0]

def g(x):
    return 2 * x[0] + 3 * x[1] - 1

def P(x, r):
    return (r / 2) * (g(x)) ** 2

def F(x, r):
    return f(x) + P(x, r)

def grad_F(x, r):
    df_dx1 = 2 * x[0] - x[1] + 1
    df_dx2 = 16 * x[1] - x[0]
    dg_dx1 = 2
    dg_dx2 = 3
    return np.array([
        df_dx1 + r * g(x) * dg_dx1,
        df_dx2 + r * g(x) * dg_dx2
    ])

def golden_ratio_search(phi, a=0, b=1, l=1e-6):
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


def fletcher_reeves_method(x0, F_func, grad_F_func, r, eps1=1e-8, eps2=1e-8, M=1000):  # Уменьшены критерии остановки
    xk = np.array(x0, dtype=float)
    grad_k = grad_F_func(xk, r)
    dk = -grad_k
    fx_prev = F_func(xk, r)
    k = 0
    stop_counter = 0
    path = [xk.copy()]

    while True:
        if np.linalg.norm(grad_k) < eps1 or k >= M:
            return xk, path

        phi = lambda t: F_func(xk + t * dk, r)
        tk = golden_ratio_search(phi, l=1e-6)

        x_next = xk + tk * dk
        grad_next = grad_F_func(x_next, r)
        fx = F_func(x_next, r)

        if np.linalg.norm(x_next - xk) < eps2 and abs(fx - fx_prev) < eps2:
            stop_counter += 1
            if stop_counter >= 2:
                return x_next, path
        else:
            stop_counter = 0

        beta = np.dot(grad_next, grad_next) / np.dot(grad_k, grad_k)
        dk = -grad_next + beta * dk

        xk = x_next
        grad_k = grad_next
        fx_prev = fx
        path.append(xk.copy())
        k += 1


# Метод штрафов
def penalty_method(x0, r0, C, eps, max_iter):
    results = []
    x = x0.copy()
    r = r0
    k = 0
    all_paths = []

    for k in range(max_iter):
        x_opt, path = fletcher_reeves_method(x, F, grad_F, r)
        all_paths.extend(path)

        f_opt = f(x_opt)
        P_val = P(x_opt, r)
        F_val = F(x_opt, r)

        lambda_val = -r * g(x_opt)

        results.append({
            'k': k,
            'r': r,
            'x1': x_opt[0],
            'x2': x_opt[1],
            'F(x*,r)': F_val,
            'lambda': lambda_val,
            'P(x*,r)': P_val
        })

        if P_val <= eps:
            break

        r *= C
        x = x_opt

    return results, x_opt, all_paths


x0 = np.array([0.0, 0.0]) 
r0 = 1
C = 10
eps = 0.0001
max_iter = 50

results, x_opt, all_paths = penalty_method(x0, r0, C, eps, max_iter)

print("k\t r\t\t x1\t\t x2\t\t F(x*,r)\t lambda\t\t P(x*,r)")
print("-" * 80)
for res in results:
    print(
        f"{res['k']}\t {res['r']:.1f}\t {res['x1']:.6f}\t {res['x2']:.6f}\t {res['F(x*,r)']:.6f}\t {res['lambda']:.6f}\t {res['P(x*,r)']:.6f}")

x1_values = [res['x1'] for res in results]
x2_values = [res['x2'] for res in results]

plt.figure(figsize=(10, 6))
plt.plot(x1_values, x2_values, 'bo-', label='Основные итерации')
plt.scatter(x1_values[0], x2_values[0], color='red', label='Начальная точка')
plt.scatter(x1_values[-1], x2_values[-1], color='green', label='Конечная точка')

plt.xlabel('x1')
plt.ylabel('x2')
plt.title('Метод штрафов')
plt.grid(True)
plt.legend()
plt.show()

analytical_solution = np.array([1 / 3, 1 / 9])
print("\nАналитическое решение:", analytical_solution)
print("Полученное решение:", x_opt)
print("Разница:", np.linalg.norm(x_opt - analytical_solution))
