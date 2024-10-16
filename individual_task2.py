bank = {}

def deposit(name, sum):
    # Зачисление средств на счет клиента
    if name not in bank:
        bank[name] = 0
    bank[name] += sum

def withdraw(name, sum):
    # Снятие средств со счета клиента
    if name not in bank:
        bank[name] = 0
    bank[name] -= sum

def balance(name):
    # Запрос остатка средств на счете клиента
    if name in bank:
        return bank[name]
    else:
        return "ERROR"

def transfer(name1, name2, sum):
    # Перевод средств с одного счета на другой
    if name1 not in bank:
        bank[name1] = 0
    if name2 not in bank:
        bank[name2] = 0
    bank[name1] -= sum
    bank[name2] += sum

def income(p):
    # Начисление процента по всем счетам
    for name in bank:
        if bank[name] > 0:
            income = bank[name] * p // 100
            bank[name] += income

deposit("Ivan", 1000)

withdraw("Ivan", 200)

print(balance("Ivan"))  # 800

transfer("Ivan", "Maria", 300)

print(balance("Ivan"))
print(balance("Maria"))

income(10)

print(balance("Ivan"))
print(balance("Maria"))
