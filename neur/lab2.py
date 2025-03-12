import random

#Задача 1

print("=" * 100)
print("Задача 1")
print("=" * 100)
def relu(x):
    return max(0, x)

def xor_relu(x1, x2):
    h1 = relu(x1 - x2)
    h2 = relu(x2 - x1)
    output = h1 + h2
    return round(output) % 2

inputs = [(0, 0), (0, 1), (1, 0), (1, 1)]
outputs = [xor_relu(x1, x2) for x1, x2 in inputs]

for (x1, x2), y in zip(inputs, outputs):
    print(f"XOR({x1}, {x2}) = {y}")

#Задача 2

print("=" * 100)
print("Задача 2")
print("=" * 100)

# Генерация случайных точек (x1, x2) в [0,1] × [0,1] и их классов
def generate_data(num_points):
    data = []
    for _ in range(num_points):
        x1, x2 = random.random(), random.random()
        label = 1 if x1 > x2 else -1  # Разделяем по x1 - x2 = 0
        data.append((x1, x2, label))
    return data

# Перцептрон
class Perceptron:
    def __init__(self, learning_rate=0.1, epochs=100):
        self.lr = learning_rate
        self.epochs = epochs
        self.w1, self.w2, self.b = random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)

    def predict(self, x1, x2):
        return 1 if (self.w1 * x1 + self.w2 * x2 + self.b) >= 0 else -1

    def train(self, training_data):
        for _ in range(self.epochs):
            for x1, x2, label in training_data:
                y_pred = self.predict(x1, x2)
                error = label - y_pred
                if error != 0:  # Обновление весов только при ошибке
                    self.w1 += self.lr * error * x1
                    self.w2 += self.lr * error * x2
                    self.b += self.lr * error

    def evaluate(self, test_data):
        correct = sum(1 for x1, x2, label in test_data if self.predict(x1, x2) == label)
        return correct / len(test_data)

# Adaline (Адаптивный нейрон)
class Adaline:
    def __init__(self, learning_rate=0.01, epochs=100):
        self.lr = learning_rate
        self.epochs = epochs
        self.w1, self.w2, self.b = random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)

    def activation(self, x1, x2):
        return self.w1 * x1 + self.w2 * x2 + self.b

    def predict(self, x1, x2):
        return 1 if self.activation(x1, x2) >= 0 else -1

    def train(self, training_data):
        for _ in range(self.epochs):
            for x1, x2, label in training_data:
                output = self.activation(x1, x2)
                error = label - output  # Линейная ошибка
                self.w1 += self.lr * error * x1
                self.w2 += self.lr * error * x2
                self.b += self.lr * error

    def evaluate(self, test_data):
        correct = sum(1 for x1, x2, label in test_data if self.predict(x1, x2) == label)
        return correct / len(test_data)

# Генерация данных
train_data = generate_data(20)
test_data = generate_data(1000)

# Обучение и тестирование перцептрона
perceptron = Perceptron()
perceptron.train(train_data)
accuracy_perceptron = perceptron.evaluate(test_data)
print(f"Точность перцептрона: {accuracy_perceptron:.2%}")

# Обучение и тестирование Adaline
adaline = Adaline()
adaline.train(train_data)
accuracy_adaline = adaline.evaluate(test_data)
print(f"Точность Adaline: {accuracy_adaline:.2%}")

#Задача 3

print("=" * 100)
print("Задача 3")
print("=" * 100)

import random
import math


# Функция активации (сигмоида) и её производная
def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def sigmoid_derivative(x):
    return x * (1 - x)


# Класс нейронной сети
class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size, learning_rate=0.5):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.learning_rate = learning_rate

        # Инициализация весов
        self.weights_input_hidden = [[random.uniform(-1, 1) for _ in range(hidden_size)] for _ in range(input_size)]
        self.weights_hidden_output = [[random.uniform(-1, 1) for _ in range(output_size)] for _ in range(hidden_size)]

        # Инициализация смещений (биасов)
        self.bias_hidden = [random.uniform(-1, 1) for _ in range(hidden_size)]
        self.bias_output = [random.uniform(-1, 1) for _ in range(output_size)]

    def forward(self, inputs):
        # Расчет значений скрытого слоя
        self.hidden_layer = [sigmoid(sum(i * w for i, w in zip(inputs, wh)) + b)
                             for wh, b in zip(self.weights_input_hidden, self.bias_hidden)]

        # Расчет значений выходного слоя
        self.output_layer = [sigmoid(sum(h * w for h, w in zip(self.hidden_layer, wo)) + b)
                             for wo, b in zip(self.weights_hidden_output, self.bias_output)]
        return self.output_layer

    def backward(self, inputs, expected):
        # Вычисление ошибки выходного слоя
        output_errors = [e - o for e, o in zip(expected, self.output_layer)]
        output_deltas = [error * sigmoid_derivative(o) for error, o in zip(output_errors, self.output_layer)]

        # Вычисление ошибки скрытого слоя
        hidden_errors = [sum(output_deltas[j] * self.weights_hidden_output[i][j] for j in range(self.output_size))
                         for i in range(self.hidden_size)]
        hidden_deltas = [error * sigmoid_derivative(h) for error, h in zip(hidden_errors, self.hidden_layer)]

        # Обновление весов скрытого -> выходного слоя
        for i in range(self.hidden_size):
            for j in range(self.output_size):
                self.weights_hidden_output[i][j] += self.learning_rate * output_deltas[j] * self.hidden_layer[i]

        # Обновление весов входного -> скрытого слоя
        for i in range(self.input_size):
            for j in range(self.hidden_size):
                self.weights_input_hidden[i][j] += self.learning_rate * hidden_deltas[j] * inputs[i]

        # Обновление биасов
        self.bias_output = [b + self.learning_rate * d for b, d in zip(self.bias_output, output_deltas)]
        self.bias_hidden = [b + self.learning_rate * d for b, d in zip(self.bias_hidden, hidden_deltas)]

    def train(self, data, epochs=10000):
        for _ in range(epochs):
            for inputs, expected in data:
                self.forward(inputs)
                self.backward(inputs, expected)

    def predict(self, inputs):
        output = self.forward(inputs)
        return [round(o) for o in output]


# Обучающие данные (буквы X, Y, I, L)
data = [
    ([1, 0, 1, 0, 1, 0, 1, 0, 1], [0, 0, 0, 1]),  # X
    ([1, 0, 1, 0, 1, 0, 0, 1, 0], [0, 0, 1, 0]),  # Y
    ([0, 1, 0, 0, 1, 0, 0, 1, 0], [0, 1, 0, 0]),  # I
    ([1, 0, 0, 1, 0, 0, 1, 1, 1], [1, 0, 0, 0])  # L
]

# Создание и обучение нейронной сети
nn = NeuralNetwork(input_size=9, hidden_size=6, output_size=4, learning_rate=0.5)
nn.train(data, epochs=10000)

# Тестирование нейросети
print("Распознавание символов:")
for inputs, expected in data:
    print(f"Вход: {inputs} -> Выход: {nn.predict(inputs)}")

# Проверка с шумом
noisy_input = [0, 1, 0, 1, 1, 0, 0, 1, 0]  # Шум в букве I
print(f"Шумный вход: {noisy_input} -> Выход: {nn.predict(noisy_input)}")
