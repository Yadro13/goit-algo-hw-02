import random
import time
import threading
import queue
from faker import Faker

fake = Faker()

# --- Налаштування ---
TOTAL_SEATS = 198
SERVICE_TIME = 2  # seconds

# --- Черги ---
queue_platinum = queue.Queue()
queue_gold = queue.Queue()
queue_standard = queue.Queue()

# --- Місця в літаку ---
seat_rows = range(1, 34)  # 33 ряди
seat_cols = ['A', 'B', 'C', 'D', 'E', 'F']
all_seats = [f"{row}{col}" for row in seat_rows for col in seat_cols]
seat_counter = 0

# --- Типи карток і шанси ---
CARD_TYPES = {
    "Platinum": 0.1,
    "Gold": 0.2,
    "Standard": 0.7,
}

# --- Генерація карток ---
def get_random_card():
    r = random.random()
    if r < CARD_TYPES["Platinum"]:
        return "Platinum"
    elif r < CARD_TYPES["Platinum"] + CARD_TYPES["Gold"]:
        return "Gold"
    return "Standard"

# --- Клієнт ---
class Client:
    def __init__(self, id):
        self.name = fake.first_name()
        self.id = id
        self.card = get_random_card()

# --- Генератор клієнтів ---
def generate_clients():
    client_id = 1
    while True:
        client = Client(client_id)
        if client.card == "Platinum":
            queue_platinum.put(client)
        elif client.card == "Gold":
            queue_gold.put(client)
        else:
            queue_standard.put(client)
        client_id += 1
        time.sleep(random.uniform(0.5, 1.5))  # Потік клієнтів з інтервалом

# --- Обробка клієнтів ---
def process_clients():
    global seat_counter
    while seat_counter < TOTAL_SEATS:
        if not queue_platinum.empty():
            client = queue_platinum.get()
        elif not queue_gold.empty():
            client = queue_gold.get()
        elif not queue_standard.empty():
            client = queue_standard.get()
        else:
            print("🕐 Очікуємо нових пасажирів...")
            time.sleep(1)
            continue

        seat = all_seats[seat_counter]
        seat_counter += 1

        print(f"\n✈️ Добро пожаловать в Терминал Б, {client.name}!")
        print(f"🎫 Тип вашей карты: {client.card.upper()}")
        print(f"🪪 Ваше место: {seat}")
        print("✅ Регистрация завершена. Спасибо, хорошего полёта!")

        time.sleep(SERVICE_TIME)

    print("\n🚫 Все места заняты. Посадка завершена. В нашем Боинге 737 их всего 198.")

# --- Запуск ---
if __name__ == "__main__":
    print("\n🛫 Стартує симуляція Терміналу Б міжнародних авіаліній України...")

    thread_gen = threading.Thread(target=generate_clients, daemon=True)
    thread_gen.start()

    process_clients()