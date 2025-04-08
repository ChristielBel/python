global xm1, xm2


def f(x1, x2):
    return x1 ** 2 + 8 * x2 ** 2 - x1 * x2 + x1


def grad(x1, x2):
    return 2 * x1 - x2 + 1, 16 * x2 - x1


def t(x1, x2):
    return (((2 * x1 - x2 + 1) ** 2 + (16 * x2 - x1) ** 2)
            / (2 * (2 * x1 - x2 + 1) ** 2 + 16 * (16 * x2 - x1) ** 2 - 2 * (2 * x1 - x2 + 1) * (16 * x2 - x1)))


x1, x2 = 1.5, 0.1
fk = f(x1, x2)
eps1 = 0.1
eps2 = 0.15
m = 10
k = 0
count = 0

while True:
    print(k)
    gx1, gx2 = grad(x1, x2)
    print(gx1, gx2)
    grad_mod = (gx1 ** 2 + gx2 ** 2) ** 0.5
    print(grad_mod)
    if grad_mod < eps1:
        xm1, xm2 = x1, x2
        break

    if k >= m:
        xm1, xm2 = x1, x2
        break

    tk = t(x1, x2)

    print(tk)

    x1_new = x1 - tk * gx1
    x2_new = x2 - tk * gx2
    print(x1_new, x2_new)
    f_new = f(x1_new, x2_new)

    x_mod = ((x1_new - x1) ** 2 + (x2_new - x2) ** 2) ** 0.5
    f_mod = (f_new ** 2 + fk ** 2) ** 0.5

    print(x_mod)
    print(f_new, fk, f_mod)

    if x_mod < eps2 and f_mod < eps2:
        count += 1

    if count == 2:
        xm1, xm2 = x1, x2
        break

    x1 = x1_new
    x2 = x2_new
    fk = f_new
    k += 1

print(k, xm1, xm2)
