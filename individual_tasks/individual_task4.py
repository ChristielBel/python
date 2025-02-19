class Wizard:
    def __init__(self, name: str, rating: int, age_appearance: int):
        self.name = name
        self.rating = rating  # Используем setter для применения ограничений
        self.age_appearance = age_appearance  # Используем setter для применения ограничений

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, value: int):
        """Ограничиваем рейтинг значениями от 1 до 100."""
        self._rating = max(1, min(100, value))

    @property
    def age_appearance(self):
        return self._age_appearance

    @age_appearance.setter
    def age_appearance(self, value: int):
        """Ограничиваем возраст значением не меньше 18."""
        self._age_appearance = max(18, value)

    def change_rating(self, value: int):
        """Изменяет рейтинг и корректирует возраст."""
        self.rating += value  # Используется setter для автоматического ограничения

        age_change = abs(value) // 10
        if value > 0:
            self.age_appearance -= age_change
        else:
            self.age_appearance += age_change

    def __iadd__(self, string: str):
        """Прибавление строки к экземпляру (изменяет рейтинг и возраст)."""
        length = len(string)
        self.change_rating(length)
        return self

    def __call__(self, number: int) -> int:
        """Вызов экземпляра с аргументом (числом)."""
        return (number - self.age_appearance) * self.rating

    def __str__(self):
        return f"Wizard({self.name}, Rating: {self.rating}, Age Appearance: {self.age_appearance})"

    def __eq__(self, other):
        return (self.rating, self.age_appearance, self.name) == (other.rating, other.age_appearance, other.name)

    def __lt__(self, other):
        return (self.rating, self.age_appearance, self.name) < (other.rating, other.age_appearance, other.name)

    @staticmethod
    def is_valid_age(age: int) -> bool:
        """Проверяет, является ли возраст допустимым."""
        return age >= 18


class IceWizard(Wizard):
    def __init__(self, name: str, rating: int, age_appearance: int, frost_power: int):
        super().__init__(name, rating, age_appearance)
        self.frost_power = frost_power

    def __str__(self):
        return f"IceWizard({self.name}, Rating: {self.rating}, Age Appearance: {self.age_appearance}, Frost Power: {self.frost_power})"


# Создаем волшебника с именем, рейтингом и возрастом на вид
wizard1 = Wizard(name="Gandalf", rating=85, age_appearance=70)
print(wizard1)  # Вывод: Wizard(Gandalf, Rating: 85, Age Appearance: 70)

# Изменяем рейтинг и проверяем, как это влияет на возраст
wizard1.change_rating(10)  # Увеличиваем рейтинг на 10
print(wizard1)  # Рейтинг: 95, Возраст на вид: 69 (уменьшился на 1)

wizard1.change_rating(-20)  # Уменьшаем рейтинг на 20
print(wizard1)  # Рейтинг: 75, Возраст на вид: 71 (увеличился на 2)

# Используем сложение строки с экземпляром
wizard1 += "magic"
print(wizard1)  # Рейтинг: 80 (увеличен на длину строки "magic" = 5), Возраст на вид: 70 (уменьшен на 5 // 10 = 0)

# Вызываем экземпляр с аргументом-числом
result = wizard1(100)  # Передаем число 100
print(f"Result of call: {result}")  # Вывод: (100 - 70) * 80 = 2400

# Создаем второго волшебника для сравнения
wizard2 = Wizard(name="Saruman", rating=75, age_appearance=65)
print(wizard2)  # Вывод: Wizard(Saruman, Rating: 75, Age Appearance: 65)

# Сравниваем волшебников по рейтингу, возрасту и имени
print(wizard1 > wizard2)  # True, так как у Gandalf рейтинг выше (80 > 75)
print(wizard1 < wizard2)  # False

# Проверка статического метода
print(Wizard.is_valid_age(25))  # True, так как возраст больше 18
print(Wizard.is_valid_age(15))  # False, так как возраст меньше 18

# Создаем Ледяного Волшебника
ice_wizard = IceWizard(name="Ice King", rating=90, age_appearance=50, frost_power=100)
print(ice_wizard)  # Вывод: IceWizard(Ice King, Rating: 90, Age Appearance: 50, Frost Power: 100)
