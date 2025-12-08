import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import time
import threading
from queue import Queue, Empty
from enum import Enum

class Stage(Enum):
    """Этапы работы системы"""
    INIT = 0
    PUMP_START = 1
    PUMP_RUN = 2
    PUMP_STOP = 3
    HEAT_TANK1 = 4
    FILL_TANK1_TO_TANK2 = 5
    COOL_TANK2 = 6
    MAINTAIN_TANK2 = 7
    WAIT_OPERATOR_TANK2 = 8
    FILL_TANK2_TO_TANK3 = 9
    HEAT_TANK3 = 10
    MAINTAIN_TANK3 = 11
    DRAIN_TANK3 = 12


class LiquidComponentSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Имитационная модель участка подготовки жидкого компонента")
        self.root.geometry("1400x900")

        # Состояния системы
        self.running = False
        self.paused = False
        self.current_stage = Stage.INIT
        self.stage_progress = 0
        self.simulation_time = 0
        self.waiting_for_operator = False
        self.operator_signal = False
        self.hold_time_counter = 0

        # Параметры из задания
        self.adc_bits = 10
        self.dac_bits = 8
        self.adc_range = (0, 30)
        self.dac_range = (0, 90)
        self.max_dac_time = 20  # мс

        # Регулируемые параметры
        self.pump_start_time = 3.5  # Время набора напряжения насоса (сек)
        self.pump_run_time = 90.0  # Время работы насоса (наполнение емкости 1)
        self.pump_stop_time = 2.8  # Время снижения напряжения насоса (сек)
        self.fill_time = 90.0  # Время перелива между емкостями (сек)
        self.hold_time = 1800.0  # Время выдержки (30 минут = 1800 сек)
        self.drain_time = 90.0  # Время слива из емкости 3 (сек)

        # Параметры емкостей
        self.tank_volumes = [0, 0, 0]  # %
        self.tank_temperatures = [25, 25, 25]  # °C
        self.target_temperatures = [490, 360, 564]  # °C
        self.heating_states = [0, 0, 0]  # 0 - выкл, 1 - нормальный, 2 - интенсивный
        self.valve_states = [False, False, False]  # Клапаны
        self.pump_voltage = 0  # В
        self.pump_state = False

        # Коды из таблиц
        self.temp_codes = {
            490: 669, 470: 642, 360: 492, 340: 464, 564: 770, 544: 743
        }
        self.voltage_codes = {
            86: 245, 36: 102, 56: 159
        }

        # Данные для графиков
        self.time_data = []
        self.pump_data = []
        self.temp1_data = []
        self.temp2_data = []
        self.temp3_data = []
        self.heater1_data = []
        self.heater2_data = []
        self.heater3_data = []

        # Управляющие слова
        self.control_word = 0
        self.sensor_data = 0

        # Очередь для обновления GUI
        self.update_queue = Queue()

        self.setup_ui()

        # Инициализация начальных значений кодов
        self.generate_control_word()
        self.generate_sensor_data()
        self.update_gui()

        # Запуск потока обновления GUI
        self.root.after(100, self.process_queue)

    def setup_ui(self):
        # Основной контейнер
        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Левая часть - визуализация и управление
        left_frame = ttk.LabelFrame(main_container, text="Визуализация процесса", padding="10")
        left_frame.grid(row=0, column=0, sticky="wnse", padx=(0, 10))

        # Холст для емкостей
        self.tank_canvas = tk.Canvas(left_frame, width=550, height=500, bg='white')
        self.tank_canvas.grid(row=0, column=0, sticky="wnse")

        # Управление
        control_frame = ttk.LabelFrame(left_frame, text="Управление", padding="10")
        control_frame.grid(row=1, column=0, sticky="we", pady=(10, 0))

        ttk.Button(control_frame, text="Старт", command=self.start_simulation).grid(row=0, column=0, padx=5)
        ttk.Button(control_frame, text="Пауза", command=self.pause_simulation).grid(row=0, column=1, padx=5)
        ttk.Button(control_frame, text="Стоп", command=self.stop_simulation).grid(row=0, column=2, padx=5)
        ttk.Button(control_frame, text="Сброс", command=self.reset_simulation).grid(row=0, column=3, padx=5)

        # Кнопка сигнала оператора
        self.operator_btn = ttk.Button(control_frame, text="Сигнал оператора",
                                       command=self.send_operator_signal)
        self.operator_btn.grid(row=0, column=4, padx=5)
        self.operator_btn.config(state='disabled')

        ttk.Label(control_frame, text="Скорость:").grid(row=1, column=0, pady=(10, 0))
        self.speed_scale = ttk.Scale(control_frame, from_=0.1, to=5, orient="horizontal")
        self.speed_scale.set(1.0)
        self.speed_scale.grid(row=1, column=1, columnspan=4, sticky="we", pady=(10, 0), padx=5)

        # Правая часть - данные и графики
        right_frame = ttk.Frame(main_container)
        right_frame.grid(row=0, column=1, sticky="wnse")

        # Верхняя правая часть - данные системы
        data_frame = ttk.LabelFrame(right_frame, text="Данные системы", padding="10")
        data_frame.grid(row=0, column=0, sticky="wnse", pady=(0, 10))

        # Температуры
        temp_frame = ttk.LabelFrame(data_frame, text="Температуры (°C)", padding="5")
        temp_frame.grid(row=0, column=0, sticky="we", pady=(0, 10))

        self.temp_vars = []
        for i in range(3):
            ttk.Label(temp_frame, text=f"Емкость {i + 1}:").grid(row=i, column=0, sticky=tk.W, padx=(0, 5))
            var = tk.StringVar(value="25.0")
            self.temp_vars.append(var)
            ttk.Entry(temp_frame, textvariable=var, width=10, state='readonly').grid(row=i, column=1)

            # Кнопка установки температуры
            btn = ttk.Button(temp_frame, text="Уст.",
                             command=lambda idx=i: self.set_temperature_dialog(idx))
            btn.grid(row=i, column=2, padx=(5, 0))

        # Напряжения
        volt_frame = ttk.LabelFrame(data_frame, text="Напряжения (В)", padding="5")
        volt_frame.grid(row=1, column=0, sticky="we", pady=(0, 10))

        self.pump_volt_var = tk.StringVar(value="0.0")
        ttk.Label(volt_frame, text="Насос:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(volt_frame, textvariable=self.pump_volt_var, width=10, state='readonly').grid(row=0, column=1)

        self.heater_vars = []
        for i in range(3):
            ttk.Label(volt_frame, text=f"Нагрев {i + 1}:").grid(row=i + 1, column=0, sticky=tk.W)
            var = tk.StringVar(value="0.0")
            self.heater_vars.append(var)
            ttk.Entry(volt_frame, textvariable=var, width=10, state='readonly').grid(row=i + 1, column=1)

        # Регулировка времени
        time_frame = ttk.LabelFrame(data_frame, text="Регулировка времени", padding="5")
        time_frame.grid(row=2, column=0, sticky="we", pady=(0, 10))

        # Время наполнения емкости 1
        ttk.Label(time_frame, text="Умножить все времена на:").grid(row=0, column=0, sticky=tk.W)
        self.time_factor_var = tk.StringVar(value="1.0")
        time_entry = ttk.Entry(time_frame, textvariable=self.time_factor_var, width=10)
        time_entry.grid(row=0, column=1, padx=5)
        ttk.Button(time_frame, text="Применить", command=self.apply_time_factor).grid(row=0, column=2)

        # Время перелива
        ttk.Label(time_frame, text="Время перелива:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.fill_time_var = tk.StringVar(value="90.0")
        fill_time_entry = ttk.Entry(time_frame, textvariable=self.fill_time_var, width=10)
        fill_time_entry.grid(row=1, column=1, padx=5, pady=(5, 0))
        ttk.Button(time_frame, text="Применить",
                   command=lambda: self.apply_time_setting('fill')).grid(row=1, column=2, pady=(5, 0))

        # Время выдержки
        ttk.Label(time_frame, text="Время выдержки:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        self.hold_time_var = tk.StringVar(value="1800.0")
        hold_time_entry = ttk.Entry(time_frame, textvariable=self.hold_time_var, width=10)
        hold_time_entry.grid(row=2, column=1, padx=5, pady=(5, 0))
        ttk.Button(time_frame, text="Применить",
                   command=lambda: self.apply_time_setting('hold')).grid(row=2, column=2, pady=(5, 0))

        # Коды
        code_frame = ttk.LabelFrame(data_frame, text="Коды и управляющие слова", padding="5")
        code_frame.grid(row=3, column=0, sticky="we", pady=(0, 10))

        ttk.Label(code_frame, text="Порт 1h (управление):").grid(row=0, column=0, sticky=tk.W)
        self.control_word_var = tk.StringVar(value="0x00000000")
        ttk.Entry(code_frame, textvariable=self.control_word_var, width=15,
                  font=('Courier', 10), state='readonly').grid(row=0, column=1)

        ttk.Label(code_frame, text="Порт 2h (данные):").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.sensor_data_var = tk.StringVar(value="0x0000")
        ttk.Entry(code_frame, textvariable=self.sensor_data_var, width=15,
                  font=('Courier', 10), state='readonly').grid(row=1, column=1, pady=(5, 0))

        # Расшифровка кодов
        decode_frame = ttk.LabelFrame(data_frame, text="Расшифровка", padding="5")
        decode_frame.grid(row=4, column=0, sticky="we", pady=(0, 10))

        self.decode_text = tk.Text(decode_frame, height=15, width=50, font=('Courier', 9))
        self.decode_text.grid(row=0, column=0)
        scrollbar = ttk.Scrollbar(decode_frame, orient="vertical", command=self.decode_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.decode_text.config(yscrollcommand=scrollbar.set)

        # Статус
        status_frame = ttk.Frame(data_frame)
        status_frame.grid(row=5, column=0, sticky="we", pady=(10, 0))

        self.status_var = tk.StringVar(value="Готов к работе")
        ttk.Label(status_frame, textvariable=self.status_var, font=('Arial', 10, 'bold')).pack()

        self.stage_var = tk.StringVar(value="Этап: ИНИЦИАЛИЗАЦИЯ")
        ttk.Label(status_frame, textvariable=self.stage_var, font=('Arial', 9)).pack()

        self.time_var = tk.StringVar(value="Время: 0 с")
        ttk.Label(status_frame, textvariable=self.time_var).pack()

        self.hold_time_var_display = tk.StringVar(value="Выдержка: 0/1800 с")
        ttk.Label(status_frame, textvariable=self.hold_time_var_display).pack()

        # Графики справа от данных
        plots_frame = ttk.LabelFrame(right_frame, text="Графики", padding="10")
        plots_frame.grid(row=0, column=1, sticky="wnse", padx=(10, 0))

        # Создание графиков
        self.setup_plots(plots_frame)

        # Настройка весов для растяжения
        main_container.columnconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(0, weight=1)

        left_frame.rowconfigure(0, weight=1)
        left_frame.columnconfigure(0, weight=1)

        right_frame.columnconfigure(0, weight=1)
        right_frame.columnconfigure(1, weight=2)
        right_frame.rowconfigure(0, weight=1)

    def setup_plots(self, parent):
        self.fig = Figure(figsize=(12, 10), dpi=80)

        # График 1: Напряжения (насос и нагреватели)
        self.ax1 = self.fig.add_subplot(411)
        self.ax1.set_title('Аналоговые значения напряжений')
        self.ax1.set_ylabel('Напряжение, В')
        self.ax1.grid(True, alpha=0.3)
        self.ax1.set_ylim(0, 100)

        self.pump_line, = self.ax1.plot([], [], 'b-', label='Насос', linewidth=2)
        self.heater1_line, = self.ax1.plot([], [], 'r-', label='Нагрев 1', alpha=0.7)
        self.heater2_line, = self.ax1.plot([], [], 'g-', label='Нагрев 2', alpha=0.7)
        self.heater3_line, = self.ax1.plot([], [], 'm-', label='Нагрев 3', alpha=0.7)
        self.ax1.legend(loc='upper right', fontsize='small')

        # График 2: Температура емкости 1
        self.ax2 = self.fig.add_subplot(412)
        self.ax2.set_title('Температура емкости 1')
        self.ax2.set_ylabel('Температура, °C')
        self.ax2.grid(True, alpha=0.3)
        self.ax2.set_ylim(0, 600)
        self.temp1_line, = self.ax2.plot([], [], 'r-', linewidth=2)

        # График 3: Температура емкости 2
        self.ax3 = self.fig.add_subplot(413)
        self.ax3.set_title('Температура емкости 2')
        self.ax3.set_ylabel('Температура, °C')
        self.ax3.grid(True, alpha=0.3)
        self.ax3.set_ylim(0, 600)
        self.temp2_line, = self.ax3.plot([], [], 'g-', linewidth=2)

        # График 4: Температура емкости 3
        self.ax4 = self.fig.add_subplot(414)
        self.ax4.set_title('Температура емкости 3')
        self.ax4.set_xlabel('Время, с')
        self.ax4.set_ylabel('Температура, °C')
        self.ax4.grid(True, alpha=0.3)
        self.ax4.set_ylim(0, 600)
        self.temp3_line, = self.ax4.plot([], [], 'b-', linewidth=2)

        self.fig.tight_layout()

        self.canvas_plot = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas_plot.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def draw_tanks(self):
        self.tank_canvas.delete("all")

        tank_width = 80
        tank_height = 200
        spacing = 40
        start_x = 100
        start_y = 50

        temp_colors = {
            'cold': '#6495ED',
            'warm': '#FFA500',
            'hot': '#FF4500',
            'very_hot': '#DC143C'
        }

        heat_colors = {
            0: 'white',
            1: '#FFA500',
            2: '#FF4500'
        }

        for i in range(3):
            x = start_x + i * (tank_width + spacing)
            y = start_y

            temp = self.tank_temperatures[i]
            if temp < 100:
                liquid_color = temp_colors['cold']
            elif temp < 300:
                liquid_color = temp_colors['warm']
            elif temp < 500:
                liquid_color = temp_colors['hot']
            else:
                liquid_color = temp_colors['very_hot']

            # Емкость
            self.tank_canvas.create_rectangle(x, y, x + tank_width, y + tank_height,
                                              outline='black', width=2)

            # Жидкость
            liquid_height = tank_height * (self.tank_volumes[i] / 100)
            self.tank_canvas.create_rectangle(x, y + tank_height - liquid_height,
                                              x + tank_width, y + tank_height,
                                              fill=liquid_color, outline='')

            # Нагреватель
            heater_color = heat_colors[self.heating_states[i]]
            heater_y = y + tank_height + 10
            self.tank_canvas.create_rectangle(x + 10, heater_y,
                                              x + tank_width - 10, heater_y + 15,
                                              fill=heater_color, outline='black', width=1)

            # Клапан
            valve_color = 'green' if self.valve_states[i] else 'red'
            valve_x = x + tank_width
            valve_y = y + tank_height / 2
            self.tank_canvas.create_oval(valve_x - 10, valve_y - 10,
                                         valve_x + 10, valve_y + 10,
                                         fill=valve_color, outline='black', width=1)

            # Подписи
            self.tank_canvas.create_text(x + tank_width / 2, y - 20,
                                         text=f"Емкость {i + 1}", font=('Arial', 10, 'bold'))

            temp_text = f"T = {temp:.1f} °C"
            self.tank_canvas.create_text(x + tank_width / 2, y + tank_height + 45,
                                         text=temp_text, font=('Arial', 9), anchor='n')

            vol_text = f"V = {self.tank_volumes[i]:.0f} %"
            self.tank_canvas.create_text(x + tank_width / 2, y + tank_height + 70,
                                         text=vol_text, font=('Arial', 9), anchor='n')

        # Насос
        pump_x = start_x - 50
        pump_y = start_y + tank_height / 2
        pump_color = '#00CED1' if self.pump_state else '#A9A9A9'
        self.tank_canvas.create_oval(pump_x - 20, pump_y - 20,
                                     pump_x + 20, pump_y + 20,
                                     fill=pump_color, outline='black', width=2)
        self.tank_canvas.create_text(
            pump_x, pump_y - 30,
            text=f"U = {self.pump_voltage:.1f} В",
            font=('Arial', 8),
            anchor='s'
        )
        self.tank_canvas.create_text(pump_x, pump_y + 30,
                                     text="Насос", font=('Arial', 8, 'bold'))

        # Стрелки потока
        self.draw_flow_arrows(start_x, tank_width, spacing, start_y, tank_height)

        # Отображение текущего этапа
        self.tank_canvas.create_text(
            275, 5,
            text=f"РЕЖИМ: {self.get_stage_name()}",
            font=('Arial', 10, 'bold'),
            fill='blue',
            width=520,
            anchor='n',
            justify='center'
        )

    def draw_flow_arrows(self, start_x, tank_width, spacing, start_y, tank_height):
        arrow_y = start_y + tank_height / 2

        # Стрелка от насоса к емкости 1
        pump_x = start_x - 50
        if self.current_stage == Stage.PUMP_START or self.current_stage == Stage.PUMP_RUN:
            self.tank_canvas.create_line(pump_x + 20, arrow_y, start_x, arrow_y,
                                         arrow="last", fill='blue', width=3)

        # Стрелки между емкостями
        if self.current_stage == Stage.FILL_TANK1_TO_TANK2 and self.valve_states[0]:
            x1 = start_x + tank_width
            x2 = start_x + tank_width + spacing
            self.tank_canvas.create_line(x1, arrow_y, x2, arrow_y,
                                         arrow="last", fill='green', width=3)

        if self.current_stage == Stage.FILL_TANK2_TO_TANK3 and self.valve_states[1]:
            x1 = start_x + tank_width + spacing + tank_width
            x2 = start_x + 2 * (tank_width + spacing)
            self.tank_canvas.create_line(x1, arrow_y, x2, arrow_y,
                                         arrow="last", fill='green', width=3)

        # Стрелка слива из емкости 3
        if self.current_stage == Stage.DRAIN_TANK3 and self.valve_states[2]:
            x3 = start_x + 2 * (tank_width + spacing) + tank_width
            self.tank_canvas.create_line(x3, arrow_y, x3 + 30, arrow_y,
                                         arrow="last", fill='red', width=3)

    def get_stage_name(self):
        names = {
            Stage.INIT: "ИНИЦИАЛИЗАЦИЯ",
            Stage.PUMP_START: f"ВКЛЮЧЕНИЕ НАСОСА (0-56В за {self.pump_start_time:.1f}с)",
            Stage.PUMP_RUN: f"РАБОТА НАСОСА ({self.pump_run_time:.0f}с)",
            Stage.PUMP_STOP: f"ВЫКЛЮЧЕНИЕ НАСОСА (56-0В за {self.pump_stop_time:.1f}с)",
            Stage.HEAT_TANK1: "НАГРЕВ ЕМКОСТИ 1 до 490°C",
            Stage.FILL_TANK1_TO_TANK2: f"ПЕРЕЛИВ 1→2 ({self.fill_time:.0f}с)",
            Stage.COOL_TANK2: "ОХЛАЖДЕНИЕ ЕМКОСТИ 2 до 360°C",
            Stage.MAINTAIN_TANK2: "ПОДДЕРЖАНИЕ 360°C В ЕМКОСТИ 2",
            Stage.WAIT_OPERATOR_TANK2: "ОЖИДАНИЕ СИГНАЛА ОПЕРАТОРА",
            Stage.FILL_TANK2_TO_TANK3: f"ПЕРЕЛИВ 2→3 ({self.fill_time:.0f}с)",
            Stage.HEAT_TANK3: "НАГРЕВ ЕМКОСТИ 3 до 564°C",
            Stage.MAINTAIN_TANK3: f"ВЫДЕРЖКА ({self.hold_time:.0f}с) при 564°C",
            Stage.DRAIN_TANK3: f"СЛИВ ИЗ ЕМКОСТИ 3 ({self.drain_time:.0f}с)"
        }
        return names.get(self.current_stage, "НЕИЗВЕСТНЫЙ ЭТАП")

    def apply_time_factor(self):
        """Применить коэффициент ко всем временным параметрам"""
        try:
            factor = float(self.time_factor_var.get())
            if 0.1 <= factor <= 10.0:
                self.pump_run_time = 90.0 * factor
                self.fill_time = 90.0 * factor
                self.hold_time = 1800.0 * factor
                self.drain_time = 90.0 * factor
                messagebox.showinfo("Успех", f"Временные параметры умножены на {factor}")
            else:
                messagebox.showerror("Ошибка", "Коэффициент должен быть от 0.1 до 10")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите числовое значение")

    def apply_time_setting(self, setting_type):
        """Применить настройки времени"""
        try:
            if setting_type == 'fill':
                value = float(self.fill_time_var.get())
                if 1 <= value <= 600:
                    self.fill_time = value
                    messagebox.showinfo("Успех", f"Время перелива установлено: {value} сек")
                else:
                    messagebox.showerror("Ошибка", "Введите значение от 1 до 600 секунд")

            elif setting_type == 'hold':
                value = float(self.hold_time_var.get())
                if 1 <= value <= 7200:
                    self.hold_time = value
                    messagebox.showinfo("Успех", f"Время выдержки установлено: {value} сек")
                else:
                    messagebox.showerror("Ошибка", "Введите значение от 1 до 7200 секунд")

            self.update_gui()

        except ValueError:
            messagebox.showerror("Ошибка", "Введите числовое значение")

    def send_operator_signal(self):
        """Отправить сигнал оператора"""
        self.operator_signal = True
        self.operator_btn.config(state='disabled')
        self.status_var.set("Получен сигнал оператора")
        self.generate_sensor_data()
        self.update_gui()

    def start_simulation(self):
        if not self.running:
            self.running = True
            self.paused = False
            self.current_stage = Stage.PUMP_START
            self.stage_progress = 0
            self.simulation_time = 0
            self.status_var.set("Симуляция запущена")
            self.operator_btn.config(state='normal')
            threading.Thread(target=self.simulation_thread, daemon=True).start()
        elif self.paused:
            self.paused = False
            self.status_var.set("Симуляция продолжается")

    def pause_simulation(self):
        if self.running:
            self.paused = not self.paused
            if self.paused:
                self.status_var.set("Симуляция на паузе")
            else:
                self.status_var.set("Симуляция продолжается")

    def stop_simulation(self):
        self.running = False
        self.paused = False
        self.status_var.set("Симуляция остановлена")

    def reset_simulation(self):
        self.stop_simulation()

        # Сброс всех параметров
        self.tank_volumes = [0, 0, 0]
        self.tank_temperatures = [25, 25, 25]
        self.heating_states = [0, 0, 0]
        self.valve_states = [False, False, False]
        self.pump_voltage = 0
        self.pump_state = False
        self.current_stage = Stage.INIT
        self.stage_progress = 0
        self.simulation_time = 0
        self.waiting_for_operator = False
        self.operator_signal = False
        self.hold_time_counter = 0
        self.operator_btn.config(state='disabled')

        # Сброс данных графиков
        self.time_data = []
        self.pump_data = []
        self.temp1_data = []
        self.temp2_data = []
        self.temp3_data = []
        self.heater1_data = []
        self.heater2_data = []
        self.heater3_data = []

        # Восстановление значений времени по умолчанию
        self.time_factor_var.set("1.0")
        self.fill_time_var.set("90.0")
        self.hold_time_var.set("1800.0")
        self.pump_run_time = 90.0
        self.fill_time = 90.0
        self.hold_time = 1800.0
        self.drain_time = 90.0

        # Обновление управляющих слов
        self.generate_control_word()
        self.generate_sensor_data()
        self.update_gui()
        self.status_var.set("Система сброшена")

    def simulation_thread(self):
        """Основной поток симуляции"""
        last_time = time.time()
        while self.running:
            if not self.paused:
                current_time = time.time()
                elapsed = current_time - last_time
                last_time = current_time

                speed_factor = self.speed_scale.get()
                effective_time_step = elapsed * speed_factor

                # Обновление этапа
                self.update_stage(effective_time_step)

                # Обновление температуры
                self.update_temperatures(effective_time_step)

                # Обновление данных для графиков
                self.time_data.append(self.simulation_time)
                self.pump_data.append(self.pump_voltage)
                self.temp1_data.append(self.tank_temperatures[0])
                self.temp2_data.append(self.tank_temperatures[1])
                self.temp3_data.append(self.tank_temperatures[2])

                # Данные для нагревателей
                h1 = 0
                if self.heating_states[0] == 1:
                    h1 = 36
                elif self.heating_states[0] == 2:
                    h1 = 86

                h2 = 0
                if self.heating_states[1] == 1:
                    h2 = 36
                elif self.heating_states[1] == 2:
                    h2 = 86

                h3 = 0
                if self.heating_states[2] == 1:
                    h3 = 36
                elif self.heating_states[2] == 2:
                    h3 = 86

                self.heater1_data.append(h1)
                self.heater2_data.append(h2)
                self.heater3_data.append(h3)

                # Обновление времени симуляции
                self.simulation_time += elapsed

                # Обновление управляющих слов
                self.generate_control_word()
                self.generate_sensor_data()

                # Отправка обновления в GUI
                self.update_queue.put(True)

            time.sleep(0.01)

    def update_stage(self, time_step):
        """Обновление текущего этапа работы"""

        if self.current_stage == Stage.PUMP_START:
            # Линейное увеличение напряжения на насосе с 0 до 56 В
            if self.pump_voltage < 56:
                increment = 56 / self.pump_start_time * time_step
                self.pump_voltage = min(56, self.pump_voltage + increment)
                self.pump_state = True
            else:
                self.current_stage = Stage.PUMP_RUN
                self.stage_progress = 0

        elif self.current_stage == Stage.PUMP_RUN:
            # Ожидание работы насоса (наполнение емкости 1)
            self.stage_progress += time_step
            if self.stage_progress < self.pump_run_time:
                # Наполнение первой емкости
                if self.tank_volumes[0] < 100:
                    increment = 100 / self.pump_run_time * time_step
                    self.tank_volumes[0] = min(100, self.tank_volumes[0] + increment)
                if self.tank_temperatures[0] < 490:
                    if self.tank_temperatures[0] < 470:
                        self.heating_states[0] = 2  # Интенсивный
                    else:
                        self.heating_states[0] = 1  # Нормальный
                else:
                    self.heating_states[0] = 0
            else:
                self.current_stage = Stage.PUMP_STOP
                self.stage_progress = 0

        elif self.current_stage == Stage.PUMP_STOP:
            # Линейное уменьшение напряжения на насосе с 56 до 0 В
            if self.pump_voltage > 0:
                decrement = 56 / self.pump_stop_time * time_step
                self.pump_voltage = max(0, self.pump_voltage - decrement)
            else:
                self.pump_state = False
                self.current_stage = Stage.HEAT_TANK1
                self.stage_progress = 0

        elif self.current_stage == Stage.HEAT_TANK1:
            # Нагрев первой емкости до 490°C
            if self.tank_temperatures[0] < 490:
                # Определение режима нагрева
                if self.tank_temperatures[0] < 470:  # Разница более 20°
                    self.heating_states[0] = 2  # Интенсивный
                else:
                    self.heating_states[0] = 1  # Нормальный
            else:
                self.heating_states[0] = 0  # Выключить нагрев
                self.current_stage = Stage.FILL_TANK1_TO_TANK2
                self.stage_progress = 0
                self.valve_states[0] = True  # Открыть клапан 1

        elif self.current_stage == Stage.FILL_TANK1_TO_TANK2:
            # Перелив из 1 во 2 емкость
            self.stage_progress += time_step
            if self.stage_progress < self.fill_time:
                if self.tank_volumes[0] > 0:
                    transfer = 100 / self.fill_time * time_step
                    self.tank_volumes[0] = max(0, self.tank_volumes[0] - transfer)
                    self.tank_volumes[1] = min(100, self.tank_volumes[1] + transfer)
                    # Температура второй емкости становится равна температуре первой
                    self.tank_temperatures[1] = self.tank_temperatures[0]
            else:
                self.valve_states[0] = False  # Закрыть клапан
                self.current_stage = Stage.COOL_TANK2
                self.stage_progress = 0

        elif self.current_stage == Stage.COOL_TANK2:
            # Охлаждение второй емкости до 360°C
            if self.tank_temperatures[1] > 360:
                # Естественное охлаждение
                self.heating_states[1] = 0
            else:
                self.current_stage = Stage.MAINTAIN_TANK2
                self.stage_progress = 0

        elif self.current_stage == Stage.MAINTAIN_TANK2:
            # Поддержание температуры 360°C во второй емкости
            if self.tank_temperatures[1] < 360:
                self.heating_states[1] = 1  # Нормальный нагрев
            elif self.tank_temperatures[1] >= 360:
                self.heating_states[1] = 0  # Выключить нагрев

            # Проверка сигнала оператора
            if self.operator_signal:
                self.current_stage = Stage.FILL_TANK2_TO_TANK3
                self.stage_progress = 0
                self.valve_states[1] = True
                self.operator_signal = False
                return
            else:
                self.current_stage = Stage.WAIT_OPERATOR_TANK2

        elif self.current_stage == Stage.WAIT_OPERATOR_TANK2:
            # Ожидание сигнала оператора
            if self.operator_signal:
                self.current_stage = Stage.FILL_TANK2_TO_TANK3
                self.stage_progress = 0
                self.valve_states[1] = True

        elif self.current_stage == Stage.FILL_TANK2_TO_TANK3:
            # Перелив из 2 в 3 емкость
            self.stage_progress += time_step
            if self.stage_progress < self.fill_time:
                if self.tank_volumes[1] > 0:
                    transfer = 100 / self.fill_time * time_step
                    self.tank_volumes[1] = max(0, self.tank_volumes[1] - transfer)
                    self.tank_volumes[2] = min(100, self.tank_volumes[2] + transfer)
                    # Температура третьей емкости становится равна температуре второй
                    self.tank_temperatures[2] = self.tank_temperatures[1]
            else:
                self.valve_states[1] = False  # Закрыть клапан
                self.current_stage = Stage.HEAT_TANK3
                self.stage_progress = 0

        elif self.current_stage == Stage.HEAT_TANK3:
            # Нагрев третьей емкости до 564°C
            if self.tank_temperatures[2] < 564:
                if self.tank_temperatures[2] < 544:  # Разница более 20°
                    self.heating_states[2] = 2  # Интенсивный
                else:
                    self.heating_states[2] = 1  # Нормальный
            else:
                self.heating_states[2] = 0  # Выключить нагрев
                self.current_stage = Stage.MAINTAIN_TANK3
                self.stage_progress = 0
                self.hold_time_counter = 0

        elif self.current_stage == Stage.MAINTAIN_TANK3:
            # Выдержка при 564°C
            self.hold_time_counter += time_step

            # Поддержание температуры
            if self.tank_temperatures[2] < 544:
                self.heating_states[2] = 2  # Интенсивный
            elif self.tank_temperatures[2] < 564:
                self.heating_states[2] = 1  # Нормальный
            else:
                self.heating_states[2] = 0  # Выключить нагрев

            if self.hold_time_counter >= self.hold_time:
                self.current_stage = Stage.DRAIN_TANK3
                self.stage_progress = 0
                self.valve_states[2] = True  # Открыть клапан 3

        elif self.current_stage == Stage.DRAIN_TANK3:
            # Слив из третьей емкости
            self.stage_progress += time_step
            if self.stage_progress < self.drain_time:
                if self.tank_volumes[2] > 0:
                    drain = 100 / self.drain_time * time_step
                    self.tank_volumes[2] = max(0, self.tank_volumes[2] - drain)
            else:
                self.valve_states[2] = False  # Закрыть клапан
                # Цикл завершен
                self.current_stage = Stage.INIT
                self.running = False
                self.status_var.set(f"Цикл завершен за {self.simulation_time:.1f} сек")

    def update_temperatures(self, time_step):
        """Обновление температур в емкостях"""
        for i in range(3):
            if self.heating_states[i] == 1:  # Нормальный нагрев
                self.tank_temperatures[i] += 5 * time_step  # 5°C/сек
            elif self.heating_states[i] == 2:  # Интенсивный нагрев
                self.tank_temperatures[i] += 10 * time_step  # 10°C/сек
            elif self.heating_states[i] == 0:  # Охлаждение
                if self.tank_temperatures[i] > 25:
                    self.tank_temperatures[i] -= 2 * time_step  # 2°C/сек естественное охлаждение

    def generate_control_word(self):
        """Генерация управляющего слова для порта 1h"""
        control_word = 0

        # Бит 0-7: Код напряжения для ЦАП
        if self.pump_state:
            voltage_code = self.calculate_dac_code(self.pump_voltage)
            control_word |= voltage_code
        else:
            # Если не насос, то возможно нагреватель
            for i in range(3):
                if self.heating_states[i] > 0:
                    if self.heating_states[i] == 1:
                        voltage_code = self.calculate_dac_code(36)
                    else:  # intensive
                        voltage_code = self.calculate_dac_code(86)
                    control_word |= voltage_code
                    break

        # Бит 8: Питание ЦАП (всегда включено при работе)
        if self.pump_state or any(h > 0 for h in self.heating_states):
            control_word |= (1 << 8)

        # Бит 9-10: Код устройства для ЦАП
        # 00 - насос, 01 - нагрев1, 10 - нагрев2, 11 - нагрев3
        if self.pump_state:
            control_word |= (0 << 9)  # Насос
        else:
            for i in range(3):
                if self.heating_states[i] > 0:
                    control_word |= ((i + 1) << 9)  # Нагреватель i+1
                    break

        # Бит 11: Питание демультиплексора
        control_word |= (1 << 11)

        # Бит 24-26: Клапаны
        for i in range(3):
            if self.valve_states[i]:
                control_word |= (1 << (24 + i))

        # Бит 27: Питание АЦП
        control_word |= (1 << 27)

        # Бит 28: Питание мультиплексора
        control_word |= (1 << 28)

        # Бит 29-31: Код датчика (циклический опрос)
        sensor_idx = int(self.simulation_time * 2) % 6  # 6 датчиков
        control_word |= (sensor_idx << 29)

        self.control_word = control_word
        self.control_word_var.set(f"0x{control_word:08X}")

        # Расшифровка
        self.decode_control_word(control_word)

    def generate_sensor_data(self):
        """Генерация данных с датчиков для порта 2h"""
        sensor_data = 0

        # Циклический опрос датчиков
        sensor_idx = int(self.simulation_time * 2) % 6
        tank_idx = sensor_idx // 2
        temp = self.tank_temperatures[tank_idx]

        # Расчет кода АЦП
        adc_code = self.calculate_adc_code(temp)
        sensor_data |= adc_code

        # Бит 14: Сигнал от оператора
        if self.operator_signal:
            sensor_data |= (1 << 14)

        # Бит 15: Сигнал готовности АЦП
        sensor_data |= (1 << 15)

        self.sensor_data = sensor_data
        self.sensor_data_var.set(f"0x{sensor_data:04X}")

    @staticmethod
    def calculate_adc_code(temperature):
        """Расчет кода АЦП для температуры"""
        # U = 0.04 * T (из задания)
        voltage = 0.04 * temperature

        # D = round((U - Umin) / (Umax - Umin) * 1024)
        adc_code = int(round((voltage - 0) / (30 - 0) * 1024))
        return min(adc_code, 1023)

    @staticmethod
    def calculate_dac_code(voltage):
        """Расчет кода ЦАП для напряжения"""
        # D = round(U / 90 * 256)
        dac_code = int(round(voltage / 90 * 256))
        return min(dac_code, 255)

    def decode_control_word(self, word):
        """Расшифровка управляющего слова"""
        lines = []

        # ЦАП
        dac_code = word & 0xFF
        voltage = (dac_code / 255) * 90
        lines.append(f"[0–7]  Код ЦАП: {dac_code} → {voltage:.1f} В")

        dac_power = (word >> 8) & 1
        lines.append(f"[8]    Питание ЦАП: {'ВКЛ' if dac_power else 'ВЫКЛ'}")

        device_code = (word >> 9) & 3
        devices = ['Насос', 'Нагрев 1', 'Нагрев 2', 'Нагрев 3']
        lines.append(f"[9–10] Устройство: {devices[device_code]}")

        # Клапаны
        for i in range(3):
            valve_state = (word >> (24 + i)) & 1
            lines.append(f"[{24 + i}]  Клапан {i + 1}: {'ОТКРЫТ' if valve_state else 'ЗАКРЫТ'}")

        adc_power = (word >> 27) & 1
        mux_power = (word >> 28) & 1
        lines.append(f"[27]   Питание АЦП: {'ВКЛ' if adc_power else 'ВЫКЛ'}")
        lines.append(f"[28]   Питание МУХ: {'ВКЛ' if mux_power else 'ВЫКЛ'}")

        sensor_code = (word >> 29) & 7
        tank = sensor_code // 2 + 1
        sensor = sensor_code % 2 + 1
        lines.append(f"[29–31] Опрос: Емкость {tank}, Датчик {sensor}")

        self.decode_text.delete(1.0, tk.END)
        self.decode_text.insert(1.0, "\n".join(lines))

    def set_temperature_dialog(self, tank_idx):
        """Диалог установки температуры"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Установка температуры для емкости {tank_idx + 1}")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text=f"Температура емкости {tank_idx + 1}:").pack(pady=10)

        temp_var = tk.StringVar(value=str(self.tank_temperatures[tank_idx]))
        entry = ttk.Entry(dialog, textvariable=temp_var, width=20)
        entry.pack(pady=5)

        def apply_temp():
            try:
                temp = float(temp_var.get())
                if 0 <= temp <= 600:
                    self.tank_temperatures[tank_idx] = temp
                    self.generate_control_word()
                    self.generate_sensor_data()
                    self.update_gui()
                    dialog.destroy()
                else:
                    messagebox.showerror("Ошибка", "Температура должна быть от 0 до 600 °C")
            except ValueError:
                messagebox.showerror("Ошибка", "Введите числовое значение")

        ttk.Button(dialog, text="Применить", command=apply_temp).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack()

        entry.focus_set()

    def update_gui(self):
        """Обновление всех элементов GUI"""
        # Обновление переменных
        for i in range(3):
            self.temp_vars[i].set(f"{self.tank_temperatures[i]:.1f}")

        self.pump_volt_var.set(f"{self.pump_voltage:.1f}")

        for i in range(3):
            heater_volt = 0
            if self.heating_states[i] == 1:
                heater_volt = 36
            elif self.heating_states[i] == 2:
                heater_volt = 86
            self.heater_vars[i].set(f"{heater_volt:.1f}")

        # Обновление визуализации
        self.draw_tanks()

        # Обновление графиков
        self.update_plots()

        # Обновление статуса
        self.stage_var.set(f"Этап: {self.get_stage_name()}")
        self.time_var.set(f"Время: {self.simulation_time:.1f} с")
        self.hold_time_var_display.set(f"Выдержка: {self.hold_time_counter:.0f}/{self.hold_time:.0f} с")

        # Обновление кнопки оператора
        if self.current_stage == Stage.WAIT_OPERATOR_TANK2:
            self.operator_btn.config(state='normal')
        else:
            self.operator_btn.config(state='disabled')

    def update_plots(self):
        """Обновление графиков"""
        if len(self.time_data) > 0:
            # Обрезка данных для отображения последних 100 точек
            display_points = min(100, len(self.time_data))
            time_display = self.time_data[-display_points:]

            # График 1: Напряжения
            self.pump_line.set_data(time_display, self.pump_data[-display_points:])
            self.heater1_line.set_data(time_display, self.heater1_data[-display_points:])
            self.heater2_line.set_data(time_display, self.heater2_data[-display_points:])
            self.heater3_line.set_data(time_display, self.heater3_data[-display_points:])

            # График 2: Температуры
            self.temp1_line.set_data(time_display, self.temp1_data[-display_points:])
            self.temp2_line.set_data(time_display, self.temp2_data[-display_points:])
            self.temp3_line.set_data(time_display, self.temp3_data[-display_points:])

            # Обновление осей
            for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
                ax.relim()
                ax.autoscale_view(scalex=False)
                if len(time_display) > 1:
                    ax.set_xlim(min(time_display), max(time_display))

            # Перерисовка
            self.canvas_plot.draw_idle()

    def process_queue(self):
        """Обработка очереди обновлений"""
        try:
            while True:
                self.update_queue.get_nowait()
                self.update_gui()
        except Empty:
            # Очередь пуста, просто ждем следующего вызова
            pass
        finally:
            self.root.after(100, self.process_queue)


def main():
    root = tk.Tk()
    LiquidComponentSimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
