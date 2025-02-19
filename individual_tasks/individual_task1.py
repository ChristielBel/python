def find_missing_digits(sequence):
    # Список всех цифр от 1 до 9
    digits = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    found_digits = [False] * 9  # Флаги для отслеживания найденных цифр

    # Проходим по последовательности и отмечаем найденные цифры
    for char in sequence:
        if char in digits:
            index = int(char) - 1
            found_digits[index] = True

    # Формируем строку с отсутствующими цифрами
    missing_digits = []
    for i in range(9):
        if not found_digits[i]:
            missing_digits.append(str(i + 1))

    if not missing_digits:
        return "0"
    else:
        return ''.join(missing_digits)


sequence = "1A734B39."
result = find_missing_digits(sequence)
print(result)
