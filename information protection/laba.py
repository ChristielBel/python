import tkinter as tk
from tkinter import ttk, messagebox
import random
from math import gcd


# ------------------ ГЛОБАЛЬНЫЙ АЛФАВИТ (латинские буквы + пробел) ------------------
LATIN_ALPHABET = " ABCDEFGHIJKLMNOPQRSTUVWXYZ"  # пробел на позиции 0
SYMBOL_TO_CODE = {ch: i for i, ch in enumerate(LATIN_ALPHABET)}
CODE_TO_SYMBOL = {i: ch for i, ch in enumerate(LATIN_ALPHABET)}


def code_to_5bits(code):
    """Возвращает 5-битное строковое представление числа code (0-31)."""
    return format(code, '05b')


def bits5_to_code(bits):
    """Из 5-битной строки получает число."""
    return int(bits, 2)


# ------------------ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ------------------
def egcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = egcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


def modinv(a, m):
    g, x, _ = egcd(a, m)
    if g != 1:
        raise Exception("Обратный элемент не существует")
    return x % m


def is_prime(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def generate_prime(start=1000, end=5000):
    while True:
        p = random.randint(start, end)
        if is_prime(p):
            return p


def discrete_log(c, g, p):
    """Находит дискретный логарифм перебором (для малых p)."""
    for x in range(p):
        if pow(g, x, p) == c:
            return x
    return None


# ------------------ RSA ------------------
class RSA:
    def generate_keys(self):
        p = generate_prime()
        q = generate_prime()
        while q == p:
            q = generate_prime()

        n = p * q
        phi = (p - 1) * (q - 1)

        e = 65537
        if gcd(e, phi) != 1:
            e = 3
            while gcd(e, phi) != 1:
                e += 2

        d = modinv(e, phi)

        self.public = (e, n)
        self.private = (d, n)

    def encrypt(self, text):
        text = text.upper()  # приводим к верхнему регистру
        e, n = self.public
        result = []
        for ch in text:
            if ch not in SYMBOL_TO_CODE:
                raise Exception(f"Недопустимый символ: {ch}")
            m = SYMBOL_TO_CODE[ch]
            c = pow(m, e, n)
            result.append(str(c))
        return result

    def decrypt(self, cipher):
        d, n = self.private
        numbers = list(map(int, cipher.split()))
        result = ''
        for c in numbers:
            m = pow(c, d, n)
            result += CODE_TO_SYMBOL[m]
        return result


# ------------------ АДДИТИВНЫЙ РЮКЗАК (Merkle-Hellman) ------------------
class AdditiveKnapsack:
    def __init__(self):
        self.n = 5  # используем 5 бит на символ

    def generate_keys(self):
        # Сверхрастущая последовательность длины n
        self.w = []
        total = 0
        for _ in range(self.n):
            val = total + random.randint(1, 20)
            self.w.append(val)
            total += val

        # Модуль q > sum(w)
        self.q = random.randint(total + 1, total + 100)

        # Множитель r, взаимно простой с q
        self.r = random.randint(2, self.q - 1)
        while gcd(self.r, self.q) != 1:
            self.r = random.randint(2, self.q - 1)

        # Открытый ключ A = r * w mod q
        self.public = [(self.r * wi) % self.q for wi in self.w]
        self.private = (self.w, self.q, self.r)

    def encrypt(self, text):
        text = text.upper()
        result = []
        for ch in text:
            if ch not in SYMBOL_TO_CODE:
                raise Exception(f"Недопустимый символ: {ch}")
            code = SYMBOL_TO_CODE[ch]
            bits = code_to_5bits(code)  # строка из 5 бит
            s = sum(int(bits[i]) * self.public[i] for i in range(self.n))
            result.append(str(s))
        return result

    def decrypt(self, cipher):
        w, q, r = self.private
        r_inv = modinv(r, q)
        text = ''
        for num in cipher.split():
            c = (int(num) * r_inv) % q
            bits = []
            for wi in reversed(w):
                if wi <= c:
                    bits.append('1')
                    c -= wi
                else:
                    bits.append('0')
            bits.reverse()
            bit_str = ''.join(bits)
            if len(bit_str) != self.n:
                raise Exception("Ошибка длины битовой строки")
            code = bits5_to_code(bit_str)
            text += CODE_TO_SYMBOL[code]
        return text


# ------------------ МУЛЬТИПЛИКАТИВНЫЙ РЮКЗАК ------------------
class MultiplicativeKnapsack:
    def __init__(self):
        self.n = 5
        self.p = 257
        self.g = 3

    def generate_keys(self):
        # Секретная сверхрастущая последовательность s
        self.s = []
        total = 0
        for _ in range(self.n):
            val = total + random.randint(1, 10)
            self.s.append(val)
            total += val

        # Открытый ключ A = g^s mod p
        self.public = [pow(self.g, si, self.p) for si in self.s]
        self.private = (self.s, self.p, self.g)

    def encrypt(self, text):
        text = text.upper()
        result = []
        for ch in text:
            if ch not in SYMBOL_TO_CODE:
                raise Exception(f"Недопустимый символ: {ch}")
            code = SYMBOL_TO_CODE[ch]
            bits = code_to_5bits(code)
            c = 1
            for i in range(self.n):
                if bits[i] == '1':
                    c = (c * self.public[i]) % self.p
            result.append(str(c))
        return result

    def decrypt(self, cipher):
        s, p, g = self.private
        text = ''
        for num in cipher.split():
            c_int = int(num)
            L = discrete_log(c_int, g, p)
            if L is None:
                raise Exception("Не удалось вычислить дискретный логарифм")
            bits = []
            remaining = L
            for si in reversed(s):
                if si <= remaining:
                    bits.append('1')
                    remaining -= si
                else:
                    bits.append('0')
            if remaining != 0:
                raise Exception("Ошибка дешифрования: остаток не ноль")
            bits.reverse()
            bit_str = ''.join(bits)
            code = bits5_to_code(bit_str)
            text += CODE_TO_SYMBOL[code]
        return text


# ------------------ ОБОБЩЁННЫЙ АДДИТИВНЫЙ РЮКЗАК ------------------
class GeneralAdditive:
    def __init__(self):
        self.alphabet = LATIN_ALPHABET
        self.mapping = SYMBOL_TO_CODE
        self.max_q = len(self.alphabet) - 1  # 26

    def generate_keys(self, n=16):
        # Сверхрастущая последовательность с учётом max_q
        self.w = []
        total = 0
        for _ in range(n):
            val = total * self.max_q + random.randint(1, self.max_q * 10)
            self.w.append(val)
            total += val

        # Модуль q > max_q * sum(w)
        self.q = random.randint(total * self.max_q + 1, total * self.max_q + 1000)

        # Множитель r, взаимно простой с q
        self.r = random.randint(2, self.q - 1)
        while gcd(self.r, self.q) != 1:
            self.r = random.randint(2, self.q - 1)

        # Открытый ключ A = r * w mod q
        self.public = [(self.r * wi) % self.q for wi in self.w]
        self.private = (self.w, self.q, self.r, self.mapping, self.max_q)

    def encrypt(self, text):
        text = text.upper()
        if len(text) != len(self.public):
            raise Exception(f"Длина сообщения должна быть {len(self.public)}")
        c = 0
        for i, ch in enumerate(text):
            if ch not in self.mapping:
                raise Exception(f"Недопустимый символ: {ch}")
            q_val = self.mapping[ch]
            c += q_val * self.public[i]
        return [str(c)]

    def decrypt(self, cipher):
        w, q, r, mapping, max_q = self.private
        r_inv = modinv(r, q)

        numbers = cipher.split()
        if len(numbers) != 1:
            raise Exception("Ожидается одно число")
        c_int = int(numbers[0])
        c_prime = (c_int * r_inv) % q

        q_values = []
        remaining = c_prime
        for wi in reversed(w):
            qv = min(remaining // wi, max_q)
            q_values.insert(0, qv)
            remaining -= qv * wi
        if remaining != 0:
            raise Exception("Ошибка дешифрования")

        reverse_mapping = {v: k for k, v in mapping.items()}
        text = ''.join(reverse_mapping[qv] for qv in q_values)
        return text


# ------------------ ОБОБЩЁННЫЙ МУЛЬТИПЛИКАТИВНЫЙ РЮКЗАК ------------------
class GeneralMultiplicative:
    def __init__(self):
        self.alphabet = LATIN_ALPHABET
        self.mapping = SYMBOL_TO_CODE
        self.max_q = len(self.alphabet) - 1
        self.p = 257
        self.g = 3

    def generate_keys(self, n=16):
        self.s = []
        total = 0
        for _ in range(n):
            val = total * self.max_q + random.randint(1, self.max_q * 10)
            self.s.append(val)
            total += val

        self.public = [pow(self.g, si, self.p) for si in self.s]
        self.private = (self.s, self.p, self.g, self.mapping, self.max_q)

    def encrypt(self, text):
        text = text.upper()
        if len(text) != len(self.public):
            raise Exception(f"Длина сообщения должна быть {len(self.public)}")
        c = 1
        for i, ch in enumerate(text):
            if ch not in self.mapping:
                raise Exception(f"Недопустимый символ: {ch}")
            q_val = self.mapping[ch]
            c = (c * pow(self.public[i], q_val, self.p)) % self.p
        return [str(c)]

    def decrypt(self, cipher):
        s, p, g, mapping, max_q = self.private
        numbers = cipher.split()
        if len(numbers) != 1:
            raise Exception("Ожидается одно число")
        c_int = int(numbers[0])
        L = discrete_log(c_int, g, p)
        if L is None:
            raise Exception("Не удалось вычислить дискретный логарифм")

        q_values = []
        remaining = L
        for si in reversed(s):
            qv = min(remaining // si, max_q)
            q_values.insert(0, qv)
            remaining -= qv * si
        if remaining != 0:
            raise Exception("Ошибка дешифрования")

        reverse_mapping = {v: k for k, v in mapping.items()}
        text = ''.join(reverse_mapping[qv] for qv in q_values)
        return text


# ------------------ КОД ХЭММИНГА (7,4) ------------------
class HammingCode:
    def __init__(self):
        self.alphabet = LATIN_ALPHABET
        self.symbol_to_code = SYMBOL_TO_CODE
        self.code_to_symbol = CODE_TO_SYMBOL

    def generate_keys(self):
        # Для кода Хэмминга ключи не нужны, но метод должен быть
        self.public = "Hamming code (7,4)"
        self.private = "Hamming code (7,4)"

    def _symbols_to_bits(self, text):
        bits = ''
        for ch in text:
            code = self.symbol_to_code[ch]
            bits += format(code, '05b')
        return bits

    def _bits_to_symbols(self, bits):
        if len(bits) % 5 != 0:
            raise Exception("Длина битовой строки не кратна 5")
        symbols = ''
        for i in range(0, len(bits), 5):
            code = int(bits[i:i+5], 2)
            symbols += self.code_to_symbol[code]
        return symbols

    def _encode_block(self, data_bits):
        # data_bits - строка из 4 бит
        m = [int(b) for b in data_bits]
        p1 = m[0] ^ m[1] ^ m[3]
        p2 = m[0] ^ m[2] ^ m[3]
        p3 = m[1] ^ m[2] ^ m[3]
        # порядок: p1, p2, m0, p3, m1, m2, m3
        return f"{p1}{p2}{m[0]}{p3}{m[1]}{m[2]}{m[3]}"

    def _decode_block(self, code_bits):
        # code_bits - строка из 7 бит
        c = [int(b) for b in code_bits]
        s1 = c[0] ^ c[2] ^ c[4] ^ c[6]
        s2 = c[1] ^ c[2] ^ c[5] ^ c[6]
        s3 = c[3] ^ c[4] ^ c[5] ^ c[6]
        syndrome = (s3 << 2) | (s2 << 1) | s1
        if syndrome != 0:
            pos = syndrome - 1
            if 0 <= pos < 7:
                c[pos] ^= 1
        # информационные биты: позиции 2,4,5,6 (0-based)
        return f"{c[2]}{c[4]}{c[5]}{c[6]}"

    def encrypt(self, text):
        text = text.upper()
        if (5 * len(text)) % 4 != 0:
            raise Exception("Длина сообщения должна быть такой, чтобы 5*len(text) делилось на 4 (например, 4, 8, 12 символов)")
        bits = self._symbols_to_bits(text)
        blocks = [bits[i:i+4] for i in range(0, len(bits), 4)]
        encoded = ''
        for block in blocks:
            encoded += self._encode_block(block)
        return [encoded]

    def decrypt(self, cipher):
        bits = cipher.strip().replace(' ', '')
        if len(bits) % 7 != 0:
            raise Exception("Длина шифртекста должна быть кратна 7")
        blocks = [bits[i:i+7] for i in range(0, len(bits), 7)]
        decoded_bits = ''
        for block in blocks:
            decoded_bits += self._decode_block(block)
        return self._bits_to_symbols(decoded_bits)


# ------------------ GUI ------------------
class CryptoApp:

    def __init__(self, root):
        self.root = root
        self.root.title("🔐 CryptoLab")
        self.root.geometry("1000x720")
        self.root.minsize(900, 650)

        self.algorithms = {
            "RSA": RSA(),
            "Аддитивный рюкзак": AdditiveKnapsack(),
            "Мультипликативный рюкзак": MultiplicativeKnapsack(),
            "Обобщенный аддитивный": GeneralAdditive(),
            "Обобщенный мультипликативный": GeneralMultiplicative(),
            "Код Хэмминга (7,4)": HammingCode()
        }

        self.current_algo = None

        self.setup_style()
        self.build_ui()

    # ---------------- STYLE ----------------
    def setup_style(self):

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Accent.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=8
        )

        style.configure(
            "Secondary.TButton",
            font=("Segoe UI", 10),
            padding=8
        )

        style.configure(
            "TLabel",
            font=("Segoe UI", 10)
        )

    # ---------------- CARD ----------------
    def create_card(self, parent, title):

        frame = tk.Frame(parent, bd=1, relief="solid", padx=15, pady=10)

        label = tk.Label(
            frame,
            text=title,
            font=("Segoe UI", 12, "bold")
        )
        label.pack(anchor="w", pady=(0, 10))

        sep = ttk.Separator(frame)
        sep.pack(fill="x", pady=(0, 10))

        content = tk.Frame(frame)
        content.pack(fill="both", expand=True)

        return frame, content

    # ---------------- TEXT FIELD ----------------
    def create_text(self, parent, height):

        frame = tk.Frame(parent)

        text = tk.Text(
            frame,
            height=height,
            font=("Consolas", 11),
            wrap="word",
            padx=10,
            pady=10
        )

        scroll = ttk.Scrollbar(frame, command=text.yview)
        text.configure(yscrollcommand=scroll.set)

        text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        frame.pack(fill="both", expand=True)

        return text

    # ---------------- UI ----------------
    def build_ui(self):

        container = tk.Frame(self.root)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # HEADER
        header = tk.Frame(container)
        header.pack(fill="x", pady=(0, 20))

        title = tk.Label(
            header,
            text="🔐 CryptoLab",
            font=("Segoe UI", 26, "bold")
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            header,
            text="Учебная лаборатория криптографических алгоритмов",
            font=("Segoe UI", 10)
        )
        subtitle.pack(anchor="w")

        # ALGORITHM
        card, content = self.create_card(container, "Алгоритм")
        card.pack(fill="x", pady=(0, 15))

        self.combo = ttk.Combobox(
            content,
            values=list(self.algorithms.keys()),
            state="readonly",
            width=40
        )
        self.combo.pack(side="left", padx=(0, 10))
        self.combo.bind("<<ComboboxSelected>>", self.select_algorithm)

        self.generate_btn = ttk.Button(
            content,
            text="🔑 Сгенерировать ключи",
            command=self.generate_keys,
            style="Accent.TButton"
        )
        self.generate_btn.pack(side="left")

        # KEYS
        card, content = self.create_card(container, "Ключи")
        card.pack(fill="x", pady=(0, 15))

        tk.Label(content, text="Публичный ключ").pack(anchor="w")
        self.public_key = self.create_text(content, 2)

        tk.Label(content, text="Приватный ключ").pack(anchor="w", pady=(10, 0))
        self.private_key = self.create_text(content, 2)

        # INPUT
        card, content = self.create_card(container, "Сообщение / Шифртекст")
        card.pack(fill="x", pady=(0, 15))

        self.input_text = self.create_text(content, 4)

        # BUTTONS
        buttons = tk.Frame(container)
        buttons.pack(pady=10)

        self.encrypt_btn = ttk.Button(
            buttons,
            text="🔒 Зашифровать",
            command=self.encrypt,
            style="Accent.TButton"
        )
        self.encrypt_btn.pack(side="left", padx=5)

        self.decrypt_btn = ttk.Button(
            buttons,
            text="🔓 Расшифровать",
            command=self.decrypt,
            style="Accent.TButton"
        )
        self.decrypt_btn.pack(side="left", padx=5)

        self.copy_btn = ttk.Button(
            buttons,
            text="📋 Копировать результат",
            command=self.copy_output,
            style="Secondary.TButton"
        )
        self.copy_btn.pack(side="left", padx=5)

        self.clear_btn = ttk.Button(
            buttons,
            text="🗑 Очистить",
            command=self.clear_all,
            style="Secondary.TButton"
        )
        self.clear_btn.pack(side="left", padx=5)

        # RESULT
        card, content = self.create_card(container, "Результат")
        card.pack(fill="both", expand=True, pady=(10, 0))

        self.output_text = self.create_text(content, 6)

        # STATUS
        self.status = tk.Label(
            self.root,
            text="Готово",
            anchor="w",
            padx=10
        )
        self.status.pack(fill="x", side="bottom")

        # PROGRESS
        self.progress = ttk.Progressbar(self.root, mode="indeterminate")
        self.progress.pack(fill="x", side="bottom")

    # ---------------- STATUS ----------------
    def set_status(self, text):
        self.status.config(text="  " + text)

    # ---------------- ALGO ----------------
    def select_algorithm(self, event):
        name = self.combo.get()
        self.current_algo = self.algorithms[name]
        self.set_status(f"Выбран алгоритм: {name}")

    # ---------------- KEYS ----------------
    def generate_keys(self):

        if not self.current_algo:
            messagebox.showerror("Ошибка", "Выберите алгоритм")
            return

        try:

            self.progress.start()
            self.root.update()

            self.current_algo.generate_keys()

            self.progress.stop()

            self.public_key.delete("1.0", tk.END)
            self.private_key.delete("1.0", tk.END)

            if hasattr(self.current_algo, "public"):
                self.public_key.insert(tk.END, str(self.current_algo.public))

            if hasattr(self.current_algo, "private"):
                self.private_key.insert(tk.END, str(self.current_algo.private))

            self.set_status("Ключи сгенерированы")

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    # ---------------- ENCRYPT ----------------
    def encrypt(self):

        if not self.current_algo:
            messagebox.showerror("Ошибка", "Выберите алгоритм")
            return

        text = self.input_text.get("1.0", tk.END).strip()

        try:

            result = self.current_algo.encrypt(text)

            self.output_text.delete("1.0", tk.END)

            if isinstance(result, list):
                result = " ".join(result)

            self.output_text.insert(tk.END, result)

            self.set_status("Текст зашифрован")

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    # ---------------- DECRYPT ----------------
    def decrypt(self):

        if not self.current_algo:
            messagebox.showerror("Ошибка", "Выберите алгоритм")
            return

        text = self.input_text.get("1.0", tk.END).strip()

        try:

            result = self.current_algo.decrypt(text)

            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, result)

            self.set_status("Текст расшифрован")

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    # ---------------- COPY ----------------
    def copy_output(self):

        text = self.output_text.get("1.0", tk.END).strip()

        self.root.clipboard_clear()
        self.root.clipboard_append(text)

        self.set_status("Результат скопирован")

    # ---------------- CLEAR ----------------
    def clear_all(self):

        for widget in [
            self.public_key,
            self.private_key,
            self.input_text,
            self.output_text
        ]:
            widget.delete("1.0", tk.END)

        self.set_status("Поля очищены")


# ------------------ ЗАПУСК ------------------
if __name__ == "__main__":
    root = tk.Tk()
    try:
        root.iconbitmap(default='icon.ico')
    except:
        pass
    app = CryptoApp(root)
    root.mainloop()
