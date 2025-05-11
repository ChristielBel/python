import numpy as np
import matplotlib
from matplotlib import pyplot as plt
matplotlib.use('TkAgg')


class HopfieldNetwork:
    def __init__(self, size):
        self.size = size
        self.weights = np.zeros((size, size))

    def train(self, patterns):
        """Обучение сети по правилу Хебба"""
        for pattern in patterns:
            pattern = np.array(pattern).flatten()
            self.weights += np.outer(pattern, pattern)

        # Диагональные элементы должны быть нулевыми
        np.fill_diagonal(self.weights, 0)
        self.weights = self.weights / self.size

    def predict(self, input_pattern, max_iter=100):
        """Предсказание с асинхронным обновлением"""
        state = np.array(input_pattern).flatten()
        prev_state = np.copy(state)

        for _ in range(max_iter):
            # Асинхронное обновление (случайный порядок)
            order = np.random.permutation(self.size)
            for i in order:
                activation = np.dot(self.weights[i], state)
                state[i] = 1 if activation >= 0 else -1

            # Проверка на сходимость
            if np.array_equal(state, prev_state):
                break
            prev_state = np.copy(state)

        return state.reshape(input_pattern.shape)

    def add_noise(self, pattern, noise_level):
        """Добавление шума к изображению"""
        noisy = np.copy(pattern)
        flips = np.random.choice([True, False], size=pattern.shape,
                                 p=[noise_level, 1 - noise_level])
        noisy[flips] *= -1
        return noisy

    def evaluate(self, patterns, test_patterns, noise_levels):
        """Оценка точности распознавания при разных уровнях шума"""
        results = {}

        for noise in noise_levels:
            correct = 0
            for i, pattern in enumerate(patterns):
                # Создаем зашумленную версию
                noisy = self.add_noise(pattern, noise)
                # Распознаем
                recognized = self.predict(noisy)
                # Проверяем соответствие
                if np.array_equal(recognized, pattern):
                    correct += 1

            accuracy = correct / len(patterns)
            results[noise] = accuracy

        return results


class HammingNetwork:
    def __init__(self, input_size, num_classes):
        self.input_size = input_size
        self.num_classes = num_classes
        self.weights1 = None  # Веса первого слоя
        self.weights2 = None  # Веса второго слоя
        self.epsilon = 0.2  # Параметр для второго слоя

    def train(self, patterns):
        """Обучение сети с правильной инициализацией весов"""
        # Нормализованные эталоны (делим на 2 и добавляем смещение)
        self.weights1 = np.array([p.flatten() for p in patterns]) / 2

        # Веса второго слоя
        self.weights2 = np.full((self.num_classes, self.num_classes),
                                -self.epsilon / (self.num_classes - 1))
        np.fill_diagonal(self.weights2, 1)

    def predict(self, input_pattern, max_iter=100, epsilon=0.1):
        """Корректный расчет расстояния Хэмминга"""
        input_vector = input_pattern.flatten()

        # Первый слой - считаем схожесть с эталонами
        similarities = []
        for t in range(self.num_classes):
            # Правильное расстояние Хэмминга
            distance = np.sum(input_vector != np.sign(self.weights1[t]))
            similarity = (self.input_size - distance) / self.input_size
            similarities.append(similarity)

        y1 = np.array(similarities)
        y1 = np.where(y1 >= 0, y1, 0)  # Пороговая функция

        # Второй слой - конкурентная сеть
        y2 = np.copy(y1)
        for _ in range(max_iter):
            prev_y2 = np.copy(y2)
            for i in range(self.num_classes):
                # Обновление с учетом обратных связей
                activation = y2[i] + np.sum(self.weights2[i] * y2)
                y2[i] = max(0, activation)  # Линейная пороговая функция

            # Проверка сходимости
            if np.max(np.abs(y2 - prev_y2)) < epsilon:
                break

        # Находим наиболее активный нейрон
        max_val = np.max(y2)
        if max_val <= 0:
            return None  # Не распознано

        # Возвращаем индекс максимального элемента
        return np.argmax(y2)

    def evaluate(self, patterns, test_patterns, noise_levels):
        """Оценка точности с подробным выводом"""
        results = {}
        for noise in noise_levels:
            correct = 0
            for i, pattern in enumerate(patterns):
                noisy = self.add_noise(pattern, noise)
                recognized = self.predict(noisy)

                if recognized == i:
                    correct += 1

            accuracy = correct / len(patterns)
            results[noise] = accuracy

        return results

    def add_noise(self, pattern, noise_level):
        """Добавление шума с сохранением структуры"""
        noisy = np.copy(pattern)
        flips = np.random.choice([True, False], size=pattern.shape,
                                 p=[noise_level, 1 - noise_level])
        noisy[flips] *= -1
        return noisy


def create_digit_patterns():
    """Создаем эталонные образы цифр 0-4 (7x7)"""
    digits = []

    # Цифра 0
    zero = np.ones((7, 7))
    zero[1:6, 1] = -1
    zero[1:6, 5] = -1
    zero[1, 1:6] = -1
    zero[5, 1:6] = -1
    digits.append(zero)

    # Цифра 1
    one = np.ones((7, 7))
    one[1:6, 3] = -1
    one[1, 2:5] = -1
    digits.append(one)

    # Цифра 2
    two = np.ones((7, 7))
    two[1, 1:6] = -1
    two[4, 1:6] = -1
    two[5, 1:6] = -1
    two[1:4, 5] = -1
    two[4:7, 1] = -1
    digits.append(two)

    # Цифра 3
    three = np.ones((7, 7))
    three[1, 1:6] = -1
    three[4, 1:6] = -1
    three[5, 1:6] = -1
    three[1:4, 5] = -1
    three[4:7, 5] = -1
    digits.append(three)

    # Цифра 4
    four = np.ones((7, 7))
    four[1:5, 3] = -1
    four[4, 1:6] = -1
    four[1:7, 5] = -1
    digits.append(four)

    return digits


def create_simple_patterns():
    """Создаем простые образы 10x10 для сети Хопфилда"""
    pattern1 = np.ones((10, 10))  # Белый квадрат
    pattern1[3:7, 3:7] = -1  # Черный квадрат внутри

    pattern2 = np.ones((10, 10))
    pattern2[2:8, 2] = -1
    pattern2[2:8, 7] = -1
    pattern2[2, 2:8] = -1
    pattern2[7, 2:8] = -1  # Контур квадрата

    return [pattern1, pattern2]


def run_comparison():
    """Запуск сравнения сетей Хопфилда и Хэмминга"""
    # Параметры тестирования
    noise_levels = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3]

    # Тестируем сеть Хопфилда на простых образах
    print("\nТестирование сети Хопфилда")
    hopfield_patterns = create_simple_patterns()
    hopfield = HopfieldNetwork(100)
    hopfield.train(hopfield_patterns)
    hop_results = hopfield.evaluate(hopfield_patterns, hopfield_patterns, noise_levels)

    # Тестируем сеть Хэмминга на цифрах
    print("\nТестирование сети Хэмминга")
    digit_patterns = create_digit_patterns()
    hamming = HammingNetwork(49, len(digit_patterns))
    hamming.train(digit_patterns)
    ham_results = hamming.evaluate(digit_patterns, digit_patterns, noise_levels)

    # Вывод результатов
    print("\nРезультаты сети Хопфилда:")
    for noise, accuracy in hop_results.items():
        print(f"Шум {noise * 100:.0f}%: точность {accuracy * 100:.1f}%")

    print("\nРезультаты сети Хэмминга:")
    for noise, accuracy in ham_results.items():
        print(f"Шум {noise * 100:.0f}%: точность {accuracy * 100:.1f}%")

    # Визуализация сравнения
    plt.figure(figsize=(10, 5))
    plt.plot([n * 100 for n in noise_levels], [acc * 100 for acc in hop_results.values()], 'o-',
             label='Хопфилд (2 образа)')
    plt.plot([n * 100 for n in noise_levels], [acc * 100 for acc in ham_results.values()], 's-',
             label='Хэмминг (5 цифр)')
    plt.xlabel('Уровень шума (%)')
    plt.ylabel('Точность распознавания (%)')
    plt.title('Сравнение сетей Хопфилда и Хэмминга')
    plt.legend()
    plt.grid()
    plt.show()


if __name__ == "__main__":
    run_comparison()
