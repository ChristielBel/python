import numpy as np


# Заданная функция
def f(x):
    x1, x2 = x
    return x1 ** 2 + 8 * x2 ** 2 - x1 * x2 + x1


# Градиент функции
def grad_f(x):
    x1, x2 = x
    df_dx1 = 2 * x1 - x2 + 1
    df_dx2 = 16 * x2 - x1
    return np.array([df_dx1, df_dx2])


# Гессиан функции
def hessian_f(x):
    # Для данной функции Гессиан не зависит от x
    return np.array([
        [2, -1],
        [-1, 16]
    ])


# Метод Ньютона
def newton_method(x0, eps1, eps2, M):
    k = 0
    xk = np.array(x0)
    fx_prev = f(xk)

    while True:
        grad = grad_f(xk)
        norm_grad = np.linalg.norm(grad)

        # Шаг 4: условие по градиенту
        if norm_grad < eps1:
            condition = "||grad(f(xk))|| < ε1"
            break

        # Шаг 5: ограничение на число итераций
        if k >= M:
            condition = "k >= M"
            break

        # Шаг 6 и 7: Гессиан и его обратная матрица
        H = hessian_f(xk)
        try:
            H_inv = np.linalg.inv(H)
        except np.linalg.LinAlgError:
            H_inv = None

        # Шаг 8: проверка положительной определенности
        if H_inv is not None and np.all(np.linalg.eigvals(H_inv) > 0):
            d = - H_inv @ grad
        else:
            d = - grad

        # Шаг 10: шаг по направлению
        t = 1  # Можно добавить строковый поиск, но пока t = 1
        x_next = xk + t * d

        # Шаг 11: проверка сходимости по x и f
        fx_next = f(x_next)
        if (np.linalg.norm(x_next - xk) < eps2 and
                abs(fx_next - fx_prev) < eps2):
            xk = x_next
            condition = "||xk+1 - xk|| < ε2 и |f(xk+1) – f(xk)| < ε2"
            break

        xk = x_next
        fx_prev = fx_next
        k += 1

    return xk, f(xk), condition, k


# Параметры
x0 = [1.5, 0.1]
eps1 = 0.1
eps2 = 0.15
M = 10

# Запуск
x_star, f_star, stop_condition, iterations = newton_method(x0, eps1, eps2, M)

# Вывод результата
print(f"x* = {x_star}")
print(f"f(x*) = {f_star}")
print(f"Условие остановки: {stop_condition}")
print(f"Количество итераций: {iterations + 1}")
