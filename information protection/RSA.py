import tkinter as tk
from tkinter import messagebox
import random
from math import gcd

# Проверка простоты (учебная)
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5)+1):
        if n % i == 0:
            return False
    return True

# Генерация простого числа
def generate_prime(start=100, end=300):
    while True:
        num = random.randint(start, end)
        if is_prime(num):
            return num

# Расширенный алгоритм Евклида
def mod_inverse(e, phi):
    def egcd(a, b):
        if b == 0:
            return (a, 1, 0)
        g, x1, y1 = egcd(b, a % b)
        return (g, y1, x1 - (a // b) * y1)

    g, x, y = egcd(e, phi)
    if g != 1:
        return None
    return x % phi


class RSAApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RSA — Криптосистема")

        tk.Label(root, text="Введите сообщение (число):").pack()
        self.entry = tk.Entry(root, width=40)
        self.entry.pack()

        tk.Button(root, text="Сгенерировать ключи",
                  command=self.generate_keys).pack()

        tk.Button(root, text="Зашифровать",
                  command=self.encrypt).pack()

        tk.Button(root, text="Расшифровать",
                  command=self.decrypt).pack()

        self.output = tk.Text(root, height=15, width=60)
        self.output.pack()

        self.public_key = None
        self.private_key = None
        self.N = None
        self.cipher = None

    def generate_keys(self):
        p = generate_prime()
        q = generate_prime()
        while p == q:
            q = generate_prime()

        N = p * q
        phi = (p-1)*(q-1)

        e = 65537
        if gcd(e, phi) != 1:
            e = 3
            while gcd(e, phi) != 1:
                e += 2

        d = mod_inverse(e, phi)

        self.public_key = e
        self.private_key = d
        self.N = N

        self.output.delete(1.0, tk.END)
        self.output.insert(tk.END, f"p = {p}\nq = {q}\n")
        self.output.insert(tk.END, f"N = {N}\n")
        self.output.insert(tk.END, f"Открытый ключ (e, N) = ({e}, {N})\n")
        self.output.insert(tk.END, f"Закрытый ключ (d, N) = ({d}, {N})\n")

    def encrypt(self):
        if not self.public_key:
            messagebox.showerror("Ошибка", "Сначала сгенерируйте ключи.")
            return

        M = int(self.entry.get())

        if M >= self.N:
            messagebox.showerror("Ошибка", "Сообщение должно быть меньше N.")
            return

        C = pow(M, self.public_key, self.N)
        self.cipher = C

        self.output.insert(tk.END, f"\nШифртекст: {C}\n")

    def decrypt(self):
        if not self.private_key or self.cipher is None:
            messagebox.showerror("Ошибка", "Нет данных для расшифрования.")
            return

        M = pow(self.cipher, self.private_key, self.N)

        self.output.insert(tk.END, f"\nРасшифрованное сообщение: {M}\n")


root = tk.Tk()
app = RSAApp(root)
root.mainloop()
