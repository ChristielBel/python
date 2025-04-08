import numpy as np
from scipy.optimize import minimize_scalar

# Целевая функция
def f(x):
    x1, x2 = x
    return x1**2 + 8 * x2**2 - x1 * x2 + x1

# Градиент функции
def grad_f(x):
    x1, x2 = x
    return np.array([2 * x1 - x2 + 1, 16 * x2 - x1])

# Гессиан (в данном случае постоянен)
def hessian_f(x):
    return np.array([
        [2, -1],
        [-1, 16]
    ])

# Метод Ньютона-Рафсона
def newton_raphson(x0, eps1, eps2, M):
    k = 0
    xk = np.array(x0)
    fx_prev = f(xk)

    while True:
        grad = grad_f(xk)
        norm_grad = np.linalg.norm(grad)

        # Шаг 4: Проверка по градиенту
        if norm_grad < eps1:
            condition = "||grad(f(xk))|| < ε1"
            break

        if k >= M:
            condition = "k ≥ M"
            break

        H = hessian_f(xk)
        try:
            H_inv = np.linalg.inv(H)
            eigs = np.linalg.eigvals(H_inv)
        except np.linalg.LinAlgError:
            H_inv = None
            eigs = []

        if H_inv is not None and np.all(eigs > 0):
            d = - H_inv @ grad
        elif H_inv is not None:
            d = - H_inv @ grad
        else:
            d = grad  # fallback (нечасто)

        # Шаг 9: Поиск оптимального t — минимизация f(xk + t * d)
        def phi(t):
            return f(xk + t * d)

        res = minimize_scalar(phi, bounds=(0, 1), method='bounded')
        t = res.x if res.success else 1

        x_next = xk + t * d
        fx_next = f(x_next)

        # Шаг 10: проверка сходимости
        if np.linalg.norm(x_next - xk) < eps2 and abs(fx_next - fx_prev) < eps2:
            xk = x_next
            condition = "||xk+1 - xk|| < ε2 и |f(xk+1) – f(xk)| < ε2"
            break

        xk = x_next
        fx_prev = fx_next
        k += 1

    return xk, f(xk), condition, k

# Параметры задачи
x0 = [1.5, 0.1]
eps1 = 0.1
eps2 = 0.15
M = 10

# Запуск
x_star, f_star, stop_condition, iterations = newton_raphson(x0, eps1, eps2, M)

# Вывод результатов
print(f"x* = {x_star}")
print(f"f(x*) = {f_star}")
print(f"Условие остановки: {stop_condition}")
print(f"Количество итераций: {iterations + 1}")
