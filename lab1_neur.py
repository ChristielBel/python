import random
import math

inputs = [
    [0.97, 0.20],
    [1.00, 0.00],
    [-0.72, 0.70],
    [-0.67, 0.74],
    [-0.80, 0.60],
    [0.00, -1.00],
    [0.20, -0.97],
    [-0.30, -0.95]
]

eta = 0.5

# Задача 1

random.seed(42)
neurons = [[random.uniform(-1, 1) for _ in range(2)] for _ in range(4)]

def euclidean_distance(v1, v2):
    return sum((v1[i] - v2[i]) ** 2 for i in range(len(v1)))

for x in inputs:
    winner_idx = min(range(len(neurons)), key=lambda i: euclidean_distance(neurons[i], x))

    for j in range(len(neurons[winner_idx])):
        neurons[winner_idx][j] += eta * (x[j] - neurons[winner_idx][j])

print("Весовые коэффициенты после обучения:")
for i, neuron in enumerate(neurons):
    print(f"Нейрон {i + 1}: {neuron}")


# Задача 2

# def initialize_weights(num_neurons, input_dim):
#     weights = []
#     for _ in range(num_neurons):
#         neuron_weights = [random.uniform(-1, 1) for _ in range(input_dim)]
#         norm = math.sqrt(sum(w ** 2 for w in neuron_weights))
#         neuron_weights = [w / norm for w in neuron_weights]
#         weights.append(neuron_weights)
#     return weights
#
# def dot_product(v1, v2):
#     return sum(x * y for x, y in zip(v1, v2))
#
# def train_wta_neural_network(weights, input_vectors, eta, epochs, penalty_threshold):
#     num_neurons = len(weights)
#     wins = [0] * num_neurons
#
#     for _ in range(epochs):
#         for input_vector in input_vectors:
#             norm = math.sqrt(sum(x ** 2 for x in input_vector))
#             normalized_input = [x / norm for x in input_vector]
#
#             activations = [
#                 dot_product(neuron_weights, normalized_input) * (1 - 0.1 * wins[i])
#                 for i, neuron_weights in enumerate(weights)
#             ]
#
#             winner_index = activations.index(max(activations))
#
#             if wins[winner_index] >= penalty_threshold:
#                 activations[winner_index] = float('-inf')
#                 winner_index = activations.index(max(activations))
#
#             winner_weights = weights[winner_index]
#             weights[winner_index] = [
#                 w + eta * (x - w) for w, x in zip(winner_weights, normalized_input)
#             ]
#
#             norm = math.sqrt(sum(w ** 2 for w in weights[winner_index]))
#             weights[winner_index] = [w / norm for w in weights[winner_index]]
#
#             wins[winner_index] += 1
#
#     return weights
#
# num_neurons = 4
# input_dim = 2
# epochs = 100
# penalty_threshold = 10
#
# weights = initialize_weights(num_neurons, input_dim)
# trained_weights = train_wta_neural_network(weights, inputs, eta, epochs, penalty_threshold)
#
# for i, w in enumerate(trained_weights):
#     print(f"Нейрон {i + 1}: {w}")

# Задача 3

# def sign(x):
#     return 1 if x >= 0 else -1
#
# def initialize_weights(input_dim):
#     return [random.uniform(-1, 1) for _ in range(input_dim + 1)]
#
# def train_hebb(input_vectors, eta, epochs):
#     input_dim = len(input_vectors[0])
#     weights = initialize_weights(input_dim)
#
#     for _ in range(epochs):
#         for x in input_vectors:
#             x_with_bias = [1] + x
#
#             y = sign(sum(w * xi for w, xi in zip(weights, x_with_bias)))
#
#             weights = [w + eta * xi * y for w, xi in zip(weights, x_with_bias)]
#
#     return weights
#
# epochs = 20
#
# weights1 = train_hebb(inputs, eta, epochs)
# weights2 = train_hebb(inputs, eta, epochs)
#
# print("Весовые коэффициенты нейрона 1:", weights1)
# print("Весовые коэффициенты нейрона 2:", weights2)
