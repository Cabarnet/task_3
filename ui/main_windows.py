import curses
from db.database import init_db
from db.admins import get_admin_by_login, create_default_admin
from main_app.setup_db import setup_departments, setup_positions
from main_app.add_worker import add_worker_flow
from main_app.list_workers import list_workers_flow
from main_app.fire_worker import fire_worker_flow
from main_app.search_worker import search_worker_flow
from main_app.clear_db import clear_database_flow
from main_app.export_excel import export_database_to_excel

APP_TITLE = "HR Manager — Главное меню"

# Главное меню
MENU_ITEMS = [
    "Настроить базу данных",
    "Добавить сотрудника",
    "Список сотрудников",
    "Уволить сотрудника",
    "Поиск сотрудника",
    "Очистить базу данных",
    "Кэшировать базу в Excel",
    "Выход"
]

def draw_menu(stdscr, idx: int, subtitle: str) -> None:
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    # Заголовок
    stdscr.addstr(1, max(0, (w - len(APP_TITLE)) // 2), APP_TITLE, curses.A_BOLD)
    stdscr.addstr(2, max(0, (w - len(subtitle)) // 2), subtitle)

    # Пункты меню
    start_y = 5
    for i, text in enumerate(MENU_ITEMS):
        y = start_y + i
        x = 4
        if i == idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, f"> {text}")
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, f"  {text}")

    # Нижняя шапка подсказок
    helpbar = " ↑/↓ — перемещение   Enter — выбрать   Esc — выход "
    stdscr.attron(curses.color_pair(2))
    stdscr.addstr(h - 1, 0, " " * (w - 1))
    stdscr.addstr(h - 1, max(0, (w - len(helpbar)) // 2), helpbar)
    stdscr.attroff(curses.color_pair(2))
    stdscr.refresh()

def handle_choice(stdscr, choice: str):
    """
    Обработка выбора пункта меню.
    Вызывает соответствующий функционал из main_app
    """
    stdscr.clear()
    if choice == "Настроить базу данных":
        setup_departments(stdscr)
        setup_positions(stdscr)
    elif choice == "Добавить сотрудника":
        add_worker_flow()
    elif choice == "Список сотрудников":
        list_workers_flow()
    elif choice == "Уволить сотрудника":
        fire_worker_flow()
    elif choice == "Поиск сотрудника":
        search_worker_flow()
    elif choice == "Очистить базу данных":
        clear_database_flow()
    elif choice == "Кэшировать базу в Excel":
        export_database_to_excel()
    elif choice == "Выход":
        return True

def main(stdscr):
    # Авторизация
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)   # Активный пункт
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Helpbar
    stdscr.keypad(True)

    init_db()
    create_default_admin()
    
    # Запрос логина/пароля
    stdscr.addstr(2, 2, "Введите логин: ")
    curses.echo()
    login = stdscr.getstr().decode().strip()
    stdscr.addstr(3, 2, "Введите пароль: ")
    password = stdscr.getstr().decode().strip()
    curses.noecho()

    admin = get_admin_by_login(login)
    if not admin or admin["password"] != password:
        stdscr.addstr(5, 2, "❌ Неверный логин или пароль. Нажмите любую клавишу.")
        stdscr.getch()
        return

    FIO_ADMIN = admin["fio"]
    subtitle = f"Авторизован: {FIO_ADMIN}"

    current_idx = 0

    while True:
        draw_menu(stdscr, current_idx, subtitle)
        key = stdscr.getch()
        if key in (curses.KEY_UP, ord('k')):
            current_idx = (current_idx - 1) % len(MENU_ITEMS)
        elif key in (curses.KEY_DOWN, ord('j')):
            current_idx = (current_idx + 1) % len(MENU_ITEMS)
        elif key in (curses.KEY_ENTER, 10, 13):
            choice = MENU_ITEMS[current_idx]
            exit_flag = handle_choice(stdscr, choice)
            if exit_flag:
                break
        elif key == 27:  # Esc
            break

# Запуск через curses.wrapper
if __name__ == "__main__":
    curses.wrapper(main)
