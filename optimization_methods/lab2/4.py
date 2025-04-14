import numpy as np

# Целевая функция
def f(x):
    x1, x2 = x
    return x1 ** 2 + 8 * x2 ** 2 - x1 * x2 + x1

# Градиент функции
def grad_f(x):
    x1, x2 = x
    return np.array([2 * x1 - x2 + 1, 16 * x2 - x1])

# Метод золотого сечения
def golden_section_search(phi, a=0, b=1, tol=1e-5):
    gr = (np.sqrt(5) + 1) / 2
    c = b - (b - a) / gr
    d = a + (b - a) / gr
    while abs(b - a) > tol:
        if phi(c) < phi(d):
            b = d
        else:
            a = c
        c = b - (b - a) / gr
        d = a + (b - a) / gr
    return (a + b) / 2

# Метод Флетчера–Ривза с двойной проверкой условия остановки
def fletcher_reeves(x0, eps1, eps2, M):
    xk = np.array(x0, dtype=float)
    grad_k = grad_f(xk)
    dk = -grad_k
    k = 0
    f_prev = f(xk)
    stop_counter = 0  # Счётчик подряд выполненных условий

    while True:
        print(f"k = {k}")
        print(f"x{k} = {xk}")
        print(f"grad = {grad_k}")
        print(f"norm = {np.linalg.norm(grad_k)}")
        if np.linalg.norm(grad_k) < eps1:
            return xk, f(xk), "||grad(f(xk))|| < eps1", k + 1

        if k >= M:
            return xk, f(xk), "Достигнуто максимальное число итераций", k + 1

        phi = lambda t: f(xk + t * dk)
        tk = golden_section_search(phi)

        print(f"t = {tk}")
        xk_new = xk + tk * dk
        grad_k_new = grad_f(xk_new)
        f_new = f(xk_new)

        if np.linalg.norm(xk_new - xk) < eps2 and abs(f_new - f_prev) < eps2:
            stop_counter += 1
            if stop_counter >= 2:
                return xk_new, f_new, "Условия по ||xk+1 - xk|| и |f(xk+1) - f(xk)| выполнены дважды", k + 1
        else:
            stop_counter = 0  # сброс если условие не выполнено подряд

        beta_k = np.dot(grad_k_new, grad_k_new) / np.dot(grad_k, grad_k)
        dk = -grad_k_new + beta_k * dk

        print(np.dot(grad_k_new, grad_k_new) , np.dot(grad_k, grad_k))
        print(f"beta = {beta_k}")
        print(f"d = {dk}")
        xk = xk_new
        grad_k = grad_k_new
        f_prev = f_new
        k += 1

# Параметры
x0 = [1.5, 0.1]
eps1 = 0.1
eps2 = 0.15
M = 10

# Запуск
x_star, f_star, stop_cond, iterations = fletcher_reeves(x0, eps1, eps2, M)

print(f"x* = {x_star}")
print(f"f(x*) = {f_star}")
print(f"Условие остановки: {stop_cond}")
print(f"Количество итераций: {iterations}")
