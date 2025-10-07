from db.departments import add_department, list_departments, delete_department
from db.positions import add_position, list_positions, delete_position
from ui.curses_utils import cinput, cprint


def setup_departments(stdscr):
    """
    Подменю настройки отделов: добавление, просмотр, удаление.
    """
    while True:
        cprint(stdscr, "\n=== Настройка отделов ===")
        cprint(stdscr, "1. Просмотреть все отделы")
        cprint(stdscr, "2. Добавить отдел")
        cprint(stdscr, "3. Удалить отдел")
        cprint(stdscr, "0. Назад")

        choice = cinput(stdscr, 5, 4, "Выберите действие: ").strip()
        if choice == "1":
            list_departments()
        elif choice == "2":
            name = cinput(stdscr, 5, 4, "Введите название отдела: ").strip()
            if name:
                add_department(name)
        elif choice == "3":
            dep_id = cinput(stdscr, 5, 4, "Введите ID отдела для удаления: ").strip()
            if dep_id.isdigit():
                delete_department(int(dep_id))
        elif choice == "0":
            break
        else:
            cprint(stdscr, "⚠️ Некорректный выбор. Попробуйте снова.")


def setup_positions(stdscr):
    """
    Подменю настройки должностей: добавление, просмотр, удаление.
    """
    while True:
        cprint(stdscr, "\n=== Настройка должностей ===")
        cprint(stdscr, "1. Просмотреть все должности")
        cprint(stdscr, "2. Добавить должность")
        cprint(stdscr, "3. Удалить должность")
        cprint(stdscr, "0. Назад")

        choice = cinput(stdscr, 5, 4, "Выберите действие: ").strip()
        if choice == "1":
            list_positions()
        elif choice == "2":
            name = cinput(stdscr, 5, 4, "Введите название должности: ").strip()
            if name:
                add_position(name)
        elif choice == "3":
            pos_id = cinput(stdscr, 5, 4, "Введите ID должности для удаления: ").strip()
            if pos_id.isdigit():
                delete_position(int(pos_id))
        elif choice == "0":
            break
        else:
            cprint(stdscr, "⚠️ Некорректный выбор. Попробуйте снова.")


def setup_database_menu(stdscr):
    """
    Главное подменю «Настройка базы данных».
    Позволяет управлять отделами и должностями.
    """
    while True:
        cprint(stdscr, "\n=== Настройка базы данных ===")
        cprint(stdscr, "1. Настройка отделов")
        cprint(stdscr, "2. Настройка должностей")
        cprint(stdscr, "0. Назад")

        choice = cinput(stdscr, 5, 4, "Выберите действие: ").strip()
        if choice == "1":
            setup_departments(stdscr)
        elif choice == "2":
            setup_positions(stdscr)
        elif choice == "0":
            break
        else:
            cprint(stdscr, "⚠️ Некорректный выбор. Попробуйте снова.")
