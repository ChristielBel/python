import tkinter as tk
from tkinter import messagebox
import random
from math import gcd

# Генерация сверхвозрастающей последовательности
def generate_superincreasing(n):
    seq = []
    total = 0
    for _ in range(n):
        next_val = random.randint(total + 1, total + 10)
        seq.append(next_val)
        total += next_val
    return seq

# Поиск обратного элемента
def mod_inverse(r, m):
    for i in range(1, m):
        if (r * i) % m == 1:
            return i
    return None

class KnapsackApp:
    def __init__(self, root):
        self.root = root
        self.root.title("АВКР — Аддитивный рюкзак")

        self.label = tk.Label(root, text="Введите двоичное сообщение:")
        self.label.pack()

        self.entry = tk.Entry(root, width=50)
        self.entry.pack()

        self.encrypt_btn = tk.Button(root, text="Сгенерировать ключи и зашифровать", command=self.encrypt)
        self.encrypt_btn.pack()

        self.decrypt_btn = tk.Button(root, text="Расшифровать", command=self.decrypt)
        self.decrypt_btn.pack()

        self.result = tk.Text(root, height=15, width=70)
        self.result.pack()

        self.private_key = None
        self.public_key = None
        self.cipher = None

    def encrypt(self):
        message = self.entry.get()

        if not all(bit in '01' for bit in message):
            messagebox.showerror("Ошибка", "Сообщение должно быть двоичным.")
            return

        n = len(message)
        W = generate_superincreasing(n)
        m = sum(W) + random.randint(1, 10)

        r = random.randint(2, m-1)
        while gcd(r, m) != 1:
            r = random.randint(2, m-1)

        B = [(r * w) % m for w in W]

        cipher = sum(int(message[i]) * B[i] for i in range(n))

        self.private_key = (W, m, r)
        self.public_key = B
        self.cipher = cipher

        self.result.delete(1.0, tk.END)
        self.result.insert(tk.END, f"Открытый ключ:\n{B}\n\n")
        self.result.insert(tk.END, f"Закрытый ключ:\n{self.private_key}\n\n")
        self.result.insert(tk.END, f"Шифртекст:\n{cipher}\n")

    def decrypt(self):
        if not self.private_key or self.cipher is None:
            messagebox.showerror("Ошибка", "Нет данных для расшифрования.")
            return

        W, m, r = self.private_key
        r_inv = mod_inverse(r, m)

        S = (self.cipher * r_inv) % m

        decrypted = []
        for w in reversed(W):
            if w <= S:
                decrypted.append(1)
                S -= w
            else:
                decrypted.append(0)

        decrypted.reverse()
        self.result.insert(tk.END, f"\nРасшифрованное сообщение:\n{''.join(map(str, decrypted))}\n")

root = tk.Tk()
app = KnapsackApp(root)
root.mainloop()
