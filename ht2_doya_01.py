import random
import time
import threading
import queue
import sys
import os
from faker import Faker
from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

fake = Faker()
console = Console()

TOTAL_SEATS = 198

SERVICE_TIME = 0.5 # Час обслуговувати клієнта
CLIENTS_TIME = 0.4 # Час між приїздами клієнтів

exit_event = threading.Event()

queue_platinum = queue.Queue()
queue_gold = queue.Queue()
queue_standard = queue.Queue()

seat_rows = range(1, 34)
seat_cols = ['A', 'B', 'C', 'D', 'E', 'F']
all_seats = [f"{row}{col}" for row in seat_rows for col in seat_cols]
seat_counter = 0
business_seats = [seat for seat in all_seats if int(seat[:-1]) <= 6] # Місця бізнес-класу (1-6 ряди)
assigned_seats = {}
client_types = {}

CARD_TYPES = {
    "Platinum": 0.05,
    "Gold": 0.25,
    "Standard": 0.7,
}

log_messages = []

class Client:
    def __init__(self, id):
        self.name = fake.first_name()
        self.id = id
        self.card = get_random_card()

    def __repr__(self):
        return f"{self.name} (#{self.id}, {self.card})"

# Потік для очікування натискання клавіші користувачем (завершення симуляції)
def wait_for_keypress():
    if os.name == 'nt':
        import msvcrt
        msvcrt.getch()
    else:
        import termios, tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    exit_event.set()

# Генерує тип картки клієнта відповідно до заданих ймовірностей
def get_random_card():
    r = random.random()
    if r < CARD_TYPES["Platinum"]:
        return "Platinum"
    elif r < CARD_TYPES["Platinum"] + CARD_TYPES["Gold"]:
        return "Gold"
    return "Standard"

# Потік генерації нових клієнтів, які розподіляються по чергах згідно типу картки
def generate_clients():
    client_id = 1
    while not exit_event.is_set():
        client = Client(client_id)
        client_types[client.id] = client.card
        if client.card == "Platinum":
            queue_platinum.put(client)
        elif client.card == "Gold":
            queue_gold.put(client)
        else:
            queue_standard.put(client)
        client_id += 1
        time.sleep(random.uniform(0.1, CLIENTS_TIME))

# Отримує наступного клієнта з черг, починаючи з Platinum, потім Gold, потім Standard
def get_next_client():
    if not queue_platinum.empty():
        return queue_platinum.queue[0]
    elif not queue_gold.empty():
        return queue_gold.queue[0]
    elif not queue_standard.empty():
        return queue_standard.queue[0]
    return None

# Потік для обслуговування клієнтів, які отримують місця в салоні літака
def process_clients():
    global seat_counter
    while (seat_counter < len(all_seats) or business_seats) and not exit_event.is_set():
        if not queue_platinum.empty():
            client = queue_platinum.get()
        elif not queue_gold.empty():
            client = queue_gold.get()
        elif not queue_standard.empty():
            client = queue_standard.get()
        else:
            time.sleep(0.1) # Немає клієнтів для обробки, зачекайте трохи
            continue

        if client.card == "Platinum" and business_seats:
            seat = business_seats.pop(0)
        else:
            # Знаходимо перше доступне місце не в бізнес-класі
            while seat_counter < len(all_seats) and all_seats[seat_counter] in business_seats:
                seat_counter += 1

            if seat_counter < len(all_seats):
                seat = all_seats[seat_counter]
                seat_counter += 1
            elif business_seats:
                # Звичайні місця закінчились — садимо в бізнес
                seat = business_seats.pop(0)
            else:
                # Взагалі немає місць (не повинно статись, але захист)
                continue

        # Присвоюємо місце клієнту
        assigned_seats[client.id] = seat
        msg_color = {
            "Platinum": "magenta",
            "Gold": "yellow",
            "Standard": "white"
        }[client.card]
        message = Text(f"{client.name} обслуговано | {client.card.upper()} | Місце: {seat}", style=msg_color)
        log_messages.append(message)
        if len(log_messages) > 100:
            log_messages.pop(0)

        time.sleep(SERVICE_TIME)

    if seat_counter >= len(all_seats) and not business_seats:
        if not exit_event.is_set():
            log_messages.append(Text("Всі місця зайняті. Очікуємо натискання клавіші для завершення...", style="bold red"))

# Генерує макет інтерфейсу з панелями для журналу, черг, салону літака та статистики
def generate_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="top", ratio=6),
        Layout(name="middle", size=8),
        Layout(name="bottom", size=3)
    )
    layout["top"].split_row(
    Layout(name="left", size=57),  # фіксована ширина для журналу
    Layout(name="right")           # решта йде на черги
    )

    layout["left"].update(generate_log_panel())
    layout["right"].update(generate_queues_panel())
    layout["middle"].update(generate_seats_panel())
    layout["bottom"].update(generate_stats_panel())
    return layout

# Виводить журнал обслуговування клієнтів з останніми записами
def generate_log_panel():
    total_height = console.size.height
    layout_top_ratio = 0.7  # Припустимо: top займає ~70% терміналу
    visible_lines = max(5, int(total_height * layout_top_ratio) - 0)

    visible = log_messages[-visible_lines:] if len(log_messages) > visible_lines else log_messages

    return Panel(Text('\n').join(visible), title="Обслуговування МАУ", border_style="green", box=box.ROUNDED)

# Генерує панель з чергами клієнтів, відображаючи їх у відповідних стовпцях
def generate_queues_panel():
    table = Table(box=box.MINIMAL, expand=True)
    table.add_column("Platinum", style="bold magenta", no_wrap=True, width=30)
    table.add_column("Gold", style="bold yellow", no_wrap=True, width=30)
    table.add_column("Standard", style="dim white", no_wrap=True, width=30)
    max_len = max(queue_platinum.qsize(), queue_gold.qsize(), queue_standard.qsize(), 1)
    next_client = get_next_client()
    start_idx = 0  # Виводимо всі, не обрізаємо
    for i in range(start_idx, max_len):
        def format_client(q, idx):
            if idx < q.qsize():
                client = q.queue[idx]
                prefix = "→ " if client == next_client else "  "
                return prefix + str(client)
            return ""
        row = [
            format_client(queue_platinum, i),
            format_client(queue_gold, i),
            format_client(queue_standard, i),
        ]
        table.add_row(*row)
    return Panel(table, title="Черги клієнтів", border_style="cyan", box=box.ROUNDED)

# Генерує панель з місцями в салоні літака, відображаючи їх у горизонтальному форматі
def generate_seats_panel():
    layout = []
    for col in seat_cols:
        line = []
        for row in seat_rows:
            seat = f"{row}{col}"
            if seat in assigned_seats.values():
                client_id = [k for k, v in assigned_seats.items() if v == seat]
                card = client_types.get(client_id[0], "Standard") if client_id else "Standard"
                if card == "Platinum":
                    style = "on magenta"
                elif card == "Gold":
                    style = "on yellow"
                else:
                    style = "on green"
            elif row <= 6:  # Бізнес-клас
                style = "on blue"
            else:
                style = "on black"
            line.append(Text(f" {seat} ", style=style))
        layout.append(Text.assemble(*line))
    return Panel(Text('\n').join(layout), title="← Ніс | Салон літака Boeng-737 (горизонтально) | Хвіст →", border_style="blue", box=box.ROUNDED)

# Генерує панель зі статистикою, відображаючи кількість клієнтів у чергах та на місцях
def generate_stats_panel():
    count_p = queue_platinum.qsize()
    count_g = queue_gold.qsize()
    count_s = queue_standard.qsize()

    platinum = sum(1 for s in assigned_seats if client_types[s] == "Platinum")
    gold = sum(1 for s in assigned_seats if client_types[s] == "Gold")
    standard = sum(1 for s in assigned_seats if client_types[s] == "Standard")

    queue_line = Text(f"У чергах → Platinum: {count_p}, Gold: {count_g}, Standard: {count_s}", style="cyan")
    onboard_line = Text(f"Платинових: {platinum}  |  Золотих: {gold}  |  Стандартних: {standard}  |  Всього місць: {len(assigned_seats)}/{TOTAL_SEATS}", style="white")

    return Panel(Text('\n').join([queue_line, onboard_line]), title="Статистика", border_style="white", box=box.ROUNDED)

# Головна функція для запуску симуляції
if __name__ == "__main__":
    console.clear()

    console.print("Реєстрація відкрита. Натисніть будь-яку клавішу для завершення симуляції.")
    log_messages.append(Text("Реєстрація відкрита. Вітаємо Вас на стійці МАУ! Натисніть будь-яку клавішу для термінової евакуації.", style="bold cyan"))

    threading.Thread(target=generate_clients, daemon=True).start()
    threading.Thread(target=wait_for_keypress, daemon=True).start()
    threading.Thread(target=process_clients, daemon=True).start()

    # Запускаємо Live-інтерфейс для відображення макету (10 оновлень на секунду)
    with Live(generate_layout(), refresh_per_second=20, screen=True) as live:
        while not exit_event.is_set():
            live.update(generate_layout())
            time.sleep(0.1)
    console.print("Симуляцію завершено. Дякуємо за участь.")
