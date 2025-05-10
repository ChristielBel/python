def x1(l, r):
    return - (35 * l - 26 * r + 16) / (94 * r + 31)


def x2(l, r):
    return - (8 * l - 14 * r + 1) / (94 * r + 31)


def calculate_l(l_val, r):
    return l_val + r * (2 * x1(l_val, r) + 3 * x2(l_val, r) - 1)


# Начальное значение l
l_current = 0

# Перебираем значения r
for r in [1, 2, 10, 100]:
    if r >= 2:
        # Вычисляем l только для r >= 2
        l_current = calculate_l(l_current, r)

    # Вычисляем x1 и x2
    x1_val = x1(l_current, r)
    x2_val = x2(l_current, r)

    # Вычисляем выражение l*(2x1 + 3x2 - 1)
    expr = l_current * (2 * x1_val + 3 * x2_val - 1) + r/2 * (2 * x1_val + 3 * x2_val - 1) ** 2

    # Вычисляем максимум между выражением и 0.001
    max_val = max(expr, 0.001)

    # Выводим результаты
    print(f"\nДля r = {r}:")
    print(f"l = {l_current}")
    print(f"x1 = {x1_val}, x2 = {x2_val}")
    print(f"l*(2x1 + 3x2 - 1) = {expr}")
    print(f"max(выражение, 0.001) = {max_val}")
