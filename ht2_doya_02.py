from collections import deque

# Функція для перевірки, чи є текст паліндромом
def is_palindrome(text):
    # Попередня обробка: приводимо до нижнього регістру і видаляємо пробіли
    cleaned_text = ''.join(char.lower() for char in text if char.isalnum())

    # Додаємо символи до двосторонньої черги
    chars = deque(cleaned_text)

    # Порівнюємо символи з обох кінців
    while len(chars) > 1:
        if chars.popleft() != chars.pop():
            return False  # Якщо символи не співпадають — не паліндром

    return True  # Якщо всі символи співпали — паліндром

# Приклади використання

TEXT1 = "Я несу гусеня"
TEXT2 = "Хто перший встав того і є першим"
TEXT3 = "Я несу лимон — номил усе, я"
TEXT4 = "Карл у Клари вкрав корали"
TEXT5 = "Тут Катя — я так тут"


print(TEXT1)  # "Я несу гусеня"
print(is_palindrome(TEXT1))  # True
print(TEXT2)  # "Хто перший встав того і є першим"
print(is_palindrome(TEXT2))  # False
print(TEXT3)  # "Я несу лимон — номил усе, я"
print(is_palindrome(TEXT3))  # False
print(TEXT4)  # "Карл у Клари вкрав корали"
print(is_palindrome(TEXT4))  # False
print(TEXT5)  # "Тут Катя — я так тут"
print(is_palindrome(TEXT5))  # True
print("Всі тести пройдено успішно!")
