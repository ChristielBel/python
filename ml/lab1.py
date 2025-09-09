import numpy as np

#1
a = np.zeros(10)

#2
b = a.copy()
b[4] = 1

#3
c = np.random.randint(0, 15, 20)
nonzero_ind = np.nonzero(c)

#4
d = np.random.rand(3, 3, 3)

#5
aa = np.random.randint(1, 10, 10)
avr = np.mean(aa)

#6
a11 = np.random.randint(1, 10, (5, 3))
a22 = np.random.randint(1, 10, (3, 2))
multi_a11_a22 = a11 @ a22

#7
b11 = np.random.randint(1, 10, (4, 4))
b22 = np.random.randint(1, 10, (4, 4))
multi_b11_b22 = b11 @ b22
diagonal = np.diag(multi_b11_b22)

#8
e = np.random.randint(1, 100, 20)
max_ind = np.argmax(e)
e[max_ind] = 0

#9
f = np.random.randint(1, 10, 20)
unique_f = np.unique(f)

#10
g = np.random.randint(1, 10, (2, 2))
av = np.mean(g)
g = g - av

#11
h = np.random.randint(1, 10, (3, 3))
h[[0,1]] = h[[1,0]]

#12
i = np.random.randint(1, 100, 20)
n = 3
max_numbers = i[np.argpartition(i, -n)[-n:]]

#13
j = np.random.randint(1, 10, (5, 5))
sum_of_rows = np.sum(j, axis=1)

#14
k = np.random.uniform(-1, 1, 10)
k[k < 0] = -1
k[k > 0] = 1

#15
l = np.random.randint(1, 101, 12)
parts = np.split(l, 3)
sums = [np.sum(part) for part in np.array_split(i, 3)]
