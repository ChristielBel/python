import math
import random

# Задача 1

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

# Задача 2

print("=" * 100)
print("Задача 2")
print("=" * 100)

import random

learning_rate = 0.5
epoches = 10


def generate_data(n):
    dots = []
    for _ in range(n):
        x1, x2 = random.random(), random.random()
        label = 1 if x1 > x2 else -1
        dots.append((x1, x2, label))
    return dots


def step_function(value):
    return 1 if value >= 0 else -1


def train_perceptron(data):
    w1, w2, bias = random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)

    for _ in range(epoches):
        for x1, x2, y in data:
            output = step_function(w1 * x1 + w2 * x2 + bias)
            update = learning_rate * (y - output)
            w1 += update * x1
            w2 += update * x2
            bias += update

    return w1, w2, bias


def train_adaline(data):
    w1, w2, bias = random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)

    for _ in range(epoches):
        total_w1_update = 0
        total_w2_update = 0
        total_bias_update = 0

        for x1, x2, y in data:
            output = w1 * x1 + w2 * x2 + bias
            error = y - output
            total_w1_update += error * x1
            total_w2_update += error * x2
            total_bias_update += error

        w1 += learning_rate * total_w1_update / len(data)
        w2 += learning_rate * total_w2_update / len(data)
        bias += learning_rate * total_bias_update / len(data)

    return w1, w2, bias


def predict(w1, w2, bias, x1, x2):
    return step_function(w1 * x1 + w2 * x2 + bias)


# Calculate accuracy
def compute_accuracy(w1, w2, bias, test_data):
    correct = 0
    for x1, x2, y in test_data:
        predicted_out = predict(w1, w2, bias, x1, x2)
        if predicted_out == y:
            correct += 1
    return correct / len(test_data)


train_data = generate_data(20)
test_data = generate_data(1000)

# Train and test Perceptron
p_w1, p_w2, p_bias = train_perceptron(train_data)
p_accuracy = compute_accuracy(p_w1, p_w2, p_bias, test_data)

# Train and test Adaline
a_w1, a_w2, a_bias = train_adaline(train_data)
a_accuracy = compute_accuracy(a_w1, a_w2, a_bias, test_data)

# Print results
print(f"Точность Персептрона: {p_accuracy * 100}")
print(f"Точность Адалайн: {a_accuracy * 100}")

# Задача 3

print("=" * 100)
print("Задача 3")
print("=" * 100)


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def sigmoid_derivative(x):
    return x * (1 - x)


inputs = [
    [1, 0, 1, 0, 1, 0, 1, 0, 1],  # X
    [1, 0, 1, 0, 1, 0, 0, 1, 0],  # Y
    [0, 1, 0, 0, 1, 0, 0, 1, 0],  # I
    [1, 0, 0, 1, 0, 0, 1, 1, 1]  # L
]

outputs = [
    [0, 0, 0, 1],
    [0, 0, 1, 0],
    [0, 1, 0, 0],
    [1, 0, 0, 0]
]

input_size = 9
hidden_size = 10
output_size = 4

weights_input_hidden = [[random.uniform(-1, 1) for _ in range(hidden_size)] for _ in range(input_size)]
weights_hidden_output = [[random.uniform(-1, 1) for _ in range(output_size)] for _ in range(hidden_size)]

bias_hidden = [random.uniform(-1, 1) for _ in range(hidden_size)]
bias_output = [random.uniform(-1, 1) for _ in range(output_size)]

learning_rate = 0.5
epochs = 500

for epoch in range(epochs):
    total_error = 0
    for i in range(len(inputs)):
        hidden_layer = [
            sigmoid(sum(inputs[i][j] * weights_input_hidden[j][k] for j in range(input_size)) + bias_hidden[k]) for k in
            range(hidden_size)]
        output_layer = [
            sigmoid(sum(hidden_layer[k] * weights_hidden_output[k][m] for k in range(hidden_size)) + bias_output[m]) for
            m in range(output_size)]

        output_errors = [outputs[i][m] - output_layer[m] for m in range(output_size)]
        total_error += sum(error ** 2 for error in output_errors)

        output_deltas = [output_errors[m] * sigmoid_derivative(output_layer[m]) for m in range(output_size)]

        hidden_errors = [sum(output_deltas[m] * weights_hidden_output[k][m] for m in range(output_size)) for k in
                         range(hidden_size)]
        hidden_deltas = [hidden_errors[k] * sigmoid_derivative(hidden_layer[k]) for k in range(hidden_size)]

        for k in range(hidden_size):
            for m in range(output_size):
                weights_hidden_output[k][m] += learning_rate * output_deltas[m] * hidden_layer[k]

        for j in range(input_size):
            for k in range(hidden_size):
                weights_input_hidden[j][k] += learning_rate * hidden_deltas[k] * inputs[i][j]

        for m in range(output_size):
            bias_output[m] += learning_rate * output_deltas[m]

        for k in range(hidden_size):
            bias_hidden[k] += learning_rate * hidden_deltas[k]


def predict(input_data):
    hidden_layer = [sigmoid(sum(input_data[j] * weights_input_hidden[j][k] for j in range(input_size)) + bias_hidden[k])
                    for k in range(hidden_size)]
    output_layer = [
        sigmoid(sum(hidden_layer[k] * weights_hidden_output[k][m] for k in range(hidden_size)) + bias_output[m]) for m
        in range(output_size)]
    return output_layer


print("\nТестирование на данных с шумом:")
test_noisy = [
    [1, 0, 1, 0, 1, 1, 1, 0, 1],
    [1, 1, 1, 0, 1, 0, 0, 1, 0],
    [0, 1, 0, 1, 1, 0, 0, 1, 0],
    [1, 0, 0, 1, 0, 0, 1, 1, 0]
]

for i, letter in enumerate(["X", "Y", "I", "L"]):
    output = predict(test_noisy[i])
    print(f"{letter}: {output}")
