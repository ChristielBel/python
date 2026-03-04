import tkinter as tk
from tkinter import ttk, messagebox
import random
from math import gcd


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


def create_alphabet_mapping(alphabet):
    """Создаёт словарь {символ: число} для заданного алфавита."""
    return {ch: i for i, ch in enumerate(alphabet)}


# ------------------ RSA ------------------
# Модель Σ_RSA = <M*, Q, C*, E(m), D(c) | V(...)>
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

        self.public = (e, n)   # открытый ключ K_E
        self.private = (d, n)  # закрытый ключ K_D

    def encrypt(self, text):
        """E(m): c = m^e mod n для каждого символа."""
        e, n = self.public
        return [pow(ord(c), e, n) for c in text]

    def decrypt(self, cipher):
        """D(c): m = c^d mod n для каждого числа."""
        d, n = self.private
        numbers = list(map(int, cipher.split()))
        return ''.join(chr(pow(c, d, n)) for c in numbers)


# ------------------ АДДИТИВНЫЙ РЮКЗАК (классический Merkle-Hellman) ------------------
# Модель Σ_AK = <M*, Q, C*, E(m), D(c) | V(...)>
class AdditiveKnapsack:
    def generate_keys(self, n=8):
        # Секретная сверхрастущая последовательность w (Q для битов)
        self.w = []
        total = 0
        for _ in range(n):
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
        """E(m): для каждого символа представить его как 8 бит, вычислить сумму bi * Ai."""
        result = []
        for char in text:
            bits = format(ord(char), '08b')
            s = sum(int(bits[i]) * self.public[i] for i in range(8))
            result.append(str(s))
        return result

    def decrypt(self, cipher):
        """D(c): для каждого числа восстановить биты через обратное преобразование."""
        w, q, r = self.private
        r_inv = modinv(r, q)
        text = ""

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
            text += chr(int(''.join(bits), 2))

        return text


# ------------------ МУЛЬТИПЛИКАТИВНЫЙ РЮКЗАК (на основе дискретного логарифма) ------------------
# Модель Σ_MK = <M*, Q, C*, E(m), D(c) | V(...)>
class MultiplicativeKnapsack:
    def __init__(self):
        # Параметры конечного поля (для демонстрации выбраны небольшие)
        self.p = 257
        self.g = 3   # порождающий элемент (должен быть примитивным корнем, для 257 3 подходит)

    def generate_keys(self, n=8):
        # Секретная сверхрастущая последовательность s (битовые веса)
        self.s = []
        total = 0
        for _ in range(n):
            val = total + random.randint(1, 10)
            self.s.append(val)
            total += val

        # Открытый ключ A = g^s mod p
        self.public = [pow(self.g, si, self.p) for si in self.s]
        self.private = (self.s, self.p, self.g)

    def encrypt(self, text):
        """E(m): для каждого символа c = ∏ A_i^{bit_i} mod p."""
        result = []
        for char in text:
            bits = format(ord(char), '08b')
            c = 1
            for i in range(8):
                if bits[i] == '1':
                    c = (c * self.public[i]) % self.p
            result.append(str(c))
        return result

    def decrypt(self, cipher):
        """D(c): для каждого числа находим дискретный логарифм и решаем сверхрастущий рюкзак."""
        s, p, g = self.private
        text = ""
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
            text += chr(int(''.join(bits), 2))
        return text


# ------------------ ОБОБЩЕННЫЙ АДДИТИВНЫЙ РЮКЗАК (многозначный алфавит) ------------------
# Модель Σ_GAK = <M*, Q, C*, E(m), D(c) | V(...)>
class GeneralAdditive:
    def __init__(self):
        # Алфавит и его числовые эквиваленты
        self.alphabet = "0123456789"
        self.mapping = create_alphabet_mapping(self.alphabet)
        self.max_q = len(self.alphabet) - 1  # максимальное значение q (0..9)

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
        """E(m): сообщение длины n → одно число c = ∑ q_i * A_i."""
        if len(text) != len(self.public):
            raise Exception(f"Длина сообщения должна быть {len(self.public)}")
        c = 0
        for i, ch in enumerate(text):
            if ch not in self.mapping:
                raise Exception(f"Недопустимый символ: {ch}")
            q_val = self.mapping[ch]
            c += q_val * self.public[i]
        return [str(c)]  # возвращаем список с одним элементом для совместимости с GUI

    def decrypt(self, cipher):
        """D(c): по одному числу восстанавливаем сообщение."""
        w, q, r, mapping, max_q = self.private
        r_inv = modinv(r, q)

        numbers = cipher.split()
        if len(numbers) != 1:
            raise Exception("Ожидается одно число")
        c_int = int(numbers[0])
        c_prime = (c_int * r_inv) % q

        # Жадный алгоритм для обобщённого рюкзака
        q_values = []
        remaining = c_prime
        for wi in reversed(w):
            qv = min(remaining // wi, max_q)
            q_values.insert(0, qv)
            remaining -= qv * wi
        if remaining != 0:
            raise Exception("Ошибка дешифрования")

        # Обратное отображение чисел в символы
        reverse_mapping = {v: k for k, v in mapping.items()}
        text = ''.join(reverse_mapping[qv] for qv in q_values)
        return text


# ------------------ ОБОБЩЕННЫЙ МУЛЬТИПЛИКАТИВНЫЙ РЮКЗАК ------------------
# Модель Σ_GMK = <M*, Q, C*, E(m), D(c) | V(...)>
class GeneralMultiplicative:
    def __init__(self):
        self.alphabet = "0123456789"
        self.mapping = create_alphabet_mapping(self.alphabet)
        self.max_q = len(self.alphabet) - 1
        self.p = 257
        self.g = 3

    def generate_keys(self, n=16):
        # Секретная сверхрастущая последовательность с учётом max_q
        self.s = []
        total = 0
        for _ in range(n):
            val = total * self.max_q + random.randint(1, self.max_q * 10)
            self.s.append(val)
            total += val

        # Открытый ключ A = g^s mod p
        self.public = [pow(self.g, si, self.p) for si in self.s]
        self.private = (self.s, self.p, self.g, self.mapping, self.max_q)

    def encrypt(self, text):
        """E(m): c = ∏ A_i^{q_i} mod p (одно число)."""
        if len(text) != len(self.public):
            raise Exception(f"Длина сообщения должна быть {len(self.public)}")
        c = 1
        for i, ch in enumerate(text):
            q_val = self.mapping[ch]
            c = (c * pow(self.public[i], q_val, self.p)) % self.p
        return [str(c)]

    def decrypt(self, cipher):
        """D(c): дискретное логарифмирование + обобщённый сверхрастущий рюкзак."""
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


# ------------------ GUI (без изменений, только добавлены новые классы) ------------------
class CryptoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔐 Криптографическая лаборатория")
        self.root.geometry("1000x750")

        self.setup_theme()

        self.algorithms = {
            "RSA": RSA(),
            "Аддитивный рюкзак": AdditiveKnapsack(),
            "Мультипликативный рюкзак": MultiplicativeKnapsack(),
            "Обобщенный аддитивный": GeneralAdditive(),
            "Обобщенный мультипликативный": GeneralMultiplicative()
        }

        self.current_algo = None
        self.current_theme = "dark"

        self.create_menu()
        self.build_ui()
        self.apply_theme()

    def setup_theme(self):
        """Настройка базовых цветов темы"""
        self.themes = {
            "dark": {
                "bg": "#1a1b26",
                "fg": "#c0caf5",
                "accent": "#7aa2f7",
                "accent_hover": "#5d8ce8",
                "surface": "#24283b",
                "surface_light": "#2f334d",
                "text": "#c0caf5",
                "text_secondary": "#9aa5ce",
                "success": "#9ece6a",
                "error": "#f7768e",
                "border": "#414868"
            },
            "light": {
                "bg": "#f5f5f5",
                "fg": "#2c3e50",
                "accent": "#3498db",
                "accent_hover": "#2980b9",
                "surface": "#ffffff",
                "surface_light": "#ecf0f1",
                "text": "#2c3e50",
                "text_secondary": "#7f8c8d",
                "success": "#27ae60",
                "error": "#e74c3c",
                "border": "#bdc3c7"
            }
        }

    def create_menu(self):
        """Создание меню приложения"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📁 Файл", menu=file_menu)
        file_menu.add_command(label="Очистить всё", command=self.clear_all)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)

        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="👁 Вид", menu=view_menu)
        view_menu.add_command(label="🌙 Темная тема", command=lambda: self.change_theme("dark"))
        view_menu.add_command(label="☀️ Светлая тема", command=lambda: self.change_theme("light"))

    def create_styled_button(self, parent, text, command, style="primary"):
        """Создание стилизованной кнопки"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=8,
            borderwidth=0,
            cursor="hand2"
        )
        return btn

    def create_card(self, parent, title, **kwargs):
        """Создание карточки с заголовком"""
        frame = tk.Frame(parent, **kwargs)

        header = tk.Frame(frame, height=40)
        header.pack(fill="x", padx=15, pady=(10, 0))

        title_label = tk.Label(
            header,
            text=title,
            font=("Segoe UI", 12, "bold")
        )
        title_label.pack(side="left")

        separator = tk.Frame(frame, height=2)
        separator.pack(fill="x", padx=15, pady=(5, 10))

        content = tk.Frame(frame)
        content.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        return frame, content

    def build_ui(self):
        """Создание пользовательского интерфейса"""
        main_container = tk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        header_frame = tk.Frame(main_container)
        header_frame.pack(fill="x", pady=(0, 20))

        title = tk.Label(
            header_frame,
            text="🔐 Криптографическая лаборатория",
            font=("Segoe UI", 24, "bold")
        )
        title.pack(side="left")

        algo_frame = tk.Frame(main_container)
        algo_frame.pack(fill="x", pady=(0, 20))

        algo_card, algo_content = self.create_card(algo_frame, "Выбор алгоритма")
        algo_card.pack(fill="x")

        self.combo = ttk.Combobox(
            algo_content,
            values=list(self.algorithms.keys()),
            state="readonly",
            font=("Segoe UI", 11),
            width=40
        )
        self.combo.pack(side="left", padx=(0, 10))
        self.combo.bind("<<ComboboxSelected>>", self.select_algorithm)

        self.generate_btn = self.create_styled_button(
            algo_content,
            "🔑 Сгенерировать ключи",
            self.generate_keys,
            "primary"
        )
        self.generate_btn.pack(side="left")

        keys_card, keys_content = self.create_card(main_container, "Ключи")
        keys_card.pack(fill="x", pady=(0, 20))

        pub_frame = tk.Frame(keys_content)
        pub_frame.pack(fill="x", pady=(0, 10))

        tk.Label(
            pub_frame,
            text="🔓 Публичный ключ:",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        self.public_key_text = self.create_text_widget(pub_frame, 3)
        self.public_key_text.pack(fill="x", pady=(5, 0))

        priv_frame = tk.Frame(keys_content)
        priv_frame.pack(fill="x")

        tk.Label(
            priv_frame,
            text="🔐 Приватный ключ:",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        self.private_key_text = self.create_text_widget(priv_frame, 3)
        self.private_key_text.pack(fill="x", pady=(5, 0))

        input_card, input_content = self.create_card(main_container, "Сообщение / Шифртекст")
        input_card.pack(fill="x", pady=(0, 20))

        self.input_text = self.create_text_widget(input_content, 4)
        self.input_text.pack(fill="x")

        action_frame = tk.Frame(main_container)
        action_frame.pack(fill="x", pady=(0, 20))

        button_container = tk.Frame(action_frame)
        button_container.pack(expand=True)

        self.encrypt_btn = self.create_styled_button(
            button_container,
            "🔒 Зашифровать",
            self.encrypt,
            "success"
        )
        self.encrypt_btn.pack(side="left", padx=10)

        self.decrypt_btn = self.create_styled_button(
            button_container,
            "🔓 Расшифровать",
            self.decrypt,
            "success"
        )
        self.decrypt_btn.pack(side="left", padx=10)

        self.clear_btn = self.create_styled_button(
            button_container,
            "🗑 Очистить",
            self.clear_all,
            "secondary"
        )
        self.clear_btn.pack(side="left", padx=10)

        result_card, result_content = self.create_card(main_container, "Результат")
        result_card.pack(fill="both", expand=True)

        self.output_text = self.create_text_widget(result_content, 6)
        self.output_text.pack(fill="both", expand=True)

        self.status_bar = tk.Label(
            self.root,
            text="Готов к работе",
            font=("Segoe UI", 9),
            anchor="w",
            padx=20
        )
        self.status_bar.pack(side="bottom", fill="x")

    def create_text_widget(self, parent, height):
        """Создание стилизованного текстового поля"""
        text_frame = tk.Frame(parent)

        text = tk.Text(
            text_frame,
            height=height,
            font=("Consolas", 11),
            wrap="word",
            padx=10,
            pady=10,
            borderwidth=1,
            relief="solid"
        )
        text.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(text_frame, command=text.yview)
        scrollbar.pack(side="right", fill="y")
        text.config(yscrollcommand=scrollbar.set)

        text_frame.pack(fill="both", expand=True)
        return text

    def apply_theme(self):
        """Применение текущей темы"""
        theme = self.themes[self.current_theme]

        self.root.configure(bg=theme["bg"])

        self.update_widget_colors(self.root, theme)

        self.status_bar.configure(
            bg=theme["surface"],
            fg=theme["text_secondary"]
        )

        for text_widget in [self.public_key_text, self.private_key_text,
                            self.input_text, self.output_text]:
            text_widget.configure(
                bg=theme["surface"],
                fg=theme["text"],
                insertbackground=theme["accent"],
                selectbackground=theme["accent"],
                selectforeground=theme["bg"]
            )

        self.generate_btn.configure(
            bg=theme["accent"],
            fg=theme["bg"],
            activebackground=theme["accent_hover"],
            activeforeground=theme["bg"]
        )

        for btn in [self.encrypt_btn, self.decrypt_btn]:
            btn.configure(
                bg=theme["success"],
                fg=theme["bg"],
                activebackground=theme["success"],
                activeforeground=theme["bg"]
            )

        self.clear_btn.configure(
            bg=theme["surface_light"],
            fg=theme["text"],
            activebackground=theme["border"],
            activeforeground=theme["text"]
        )

        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "TCombobox",
            fieldbackground=theme["surface"],
            background=theme["surface"],
            foreground=theme["text"],
            arrowcolor=theme["text"],
            bordercolor=theme["border"],
            lightcolor=theme["border"],
            darkcolor=theme["border"]
        )

        self.update_theme_indicator()

    def update_widget_colors(self, widget, theme):
        """Рекурсивное обновление цветов виджетов"""
        try:
            if isinstance(widget, tk.Frame):
                widget.configure(bg=theme["bg"])
            elif isinstance(widget, tk.Label):
                if widget.cget("font") == ("Segoe UI", 24, "bold"):  # Заголовок
                    widget.configure(bg=theme["bg"], fg=theme["accent"])
                elif widget.cget("font") == ("Segoe UI", 12, "bold"):  # Заголовки карточек
                    widget.configure(bg=theme["bg"], fg=theme["accent"])
                else:
                    widget.configure(bg=theme["bg"], fg=theme["text"])
            elif isinstance(widget, tk.Button):
                pass
        except:
            pass

        for child in widget.winfo_children():
            self.update_widget_colors(child, theme)

    def update_theme_indicator(self):
        """Обновление индикатора текущей темы в меню"""
        pass

    def change_theme(self, theme_name):
        """Смена темы"""
        self.current_theme = theme_name
        self.apply_theme()
        self.update_status(f"Тема изменена на {theme_name}")

    def update_status(self, message):
        """Обновление статусной строки"""
        self.status_bar.config(text=f"  {message}")

    def clear_all(self):
        """Очистка всех полей"""
        self.public_key_text.delete("1.0", tk.END)
        self.private_key_text.delete("1.0", tk.END)
        self.input_text.delete("1.0", tk.END)
        self.output_text.delete("1.0", tk.END)
        self.update_status("Все поля очищены")

    def select_algorithm(self, event):
        name = self.combo.get()
        self.current_algo = self.algorithms[name]
        self.update_status(f"Выбран алгоритм: {name}")

    def generate_keys(self):
        if not self.current_algo:
            messagebox.showerror("Ошибка", "Выберите алгоритм")
            return

        try:
            self.public_key_text.delete("1.0", tk.END)
            self.private_key_text.delete("1.0", tk.END)

            self.current_algo.generate_keys()

            if hasattr(self.current_algo, "public"):
                self.public_key_text.insert(tk.END, str(self.current_algo.public))

            if hasattr(self.current_algo, "private"):
                self.private_key_text.insert(tk.END, str(self.current_algo.private))

            self.update_status("Ключи успешно сгенерированы")

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            self.update_status(f"Ошибка: {str(e)}")

    def encrypt(self):
        if not self.current_algo:
            messagebox.showerror("Ошибка", "Выберите алгоритм")
            return

        text = self.input_text.get("1.0", tk.END).strip()

        if not text:
            messagebox.showwarning("Предупреждение", "Введите текст для шифрования")
            return

        try:
            result = self.current_algo.encrypt(text)
            self.output_text.delete("1.0", tk.END)

            if isinstance(result, list):
                output = " ".join(map(str, result))
            else:
                output = str(result)

            self.output_text.insert(tk.END, output)
            self.update_status(f"✅ Текст успешно зашифрован")

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            self.update_status(f"❌ Ошибка шифрования: {str(e)}")

    def decrypt(self):
        if not self.current_algo:
            messagebox.showerror("Ошибка", "Выберите алгоритм")
            return

        text = self.input_text.get("1.0", tk.END).strip()

        if not text:
            messagebox.showwarning("Предупреждение", "Введите текст для расшифровки")
            return

        try:
            result = self.current_algo.decrypt(text)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, result)
            self.update_status(f"✅ Текст успешно расшифрован")

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            self.update_status(f"❌ Ошибка расшифровки: {str(e)}")


# ------------------ ЗАПУСК ------------------
if __name__ == "__main__":
    root = tk.Tk()
    try:
        root.iconbitmap(default='icon.ico')
    except:
        pass
    app = CryptoApp(root)
    root.mainloop()
