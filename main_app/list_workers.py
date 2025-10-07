import sqlite3
from db.database import get_connection
from ui.curses_utils import cinput, cprint


# Получить список сотрудников с JOIN на должности и отделы
def fetch_workers(department_id=None, position_id=None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        query = """
        SELECT
            W.id,
            W.fio,
            P.name AS position_name,
            D.name AS department_name,
            W.phone,
            W.email
        FROM Workers AS W
        LEFT JOIN Positions AS P ON W.position_id = P.id
        LEFT JOIN Departments AS D ON W.department_id = D.id
        WHERE 1=1
        """
        params = []
        if department_id:
            query += " AND D.id = ?"
            params.append(department_id)
        if position_id:
            query += " AND P.id = ?"
            params.append(position_id)

        query += " ORDER BY W.fio ASC"
        cur.execute(query, params)
        return cur.fetchall()
    finally:
        conn.close()


# Получить все отделы
def fetch_departments():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM Departments ORDER BY name")
        return cur.fetchall()
    finally:
        conn.close()


# Получить все должности
def fetch_positions():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM Positions ORDER BY name")
        return cur.fetchall()
    finally:
        conn.close()


# Форматированный вывод таблицы сотрудников
def print_workers_table(stdscr, workers):
    if not workers:
        cprint(stdscr, "⚠️  Сотрудники не найдены.")
        return

    cprint(stdscr, "\n📋 Список сотрудников:\n")
    cprint(stdscr, f"{'ID':<4} {'ФИО':<30} {'Должность':<20} {'Отдел':<20} {'Телефон':<15} {'Email'}")
    cprint(stdscr, "-" * 100)

    for row in workers:
        cprint(stdscr, f"{row['id']:<4} {row['fio']:<30.30} {row['position_name']:<20.20} "
              f"{row['department_name']:<20.20} {row['phone'] or '-':<15} {row['email'] or '-'}")
    cprint(stdscr, "-" * 100)
    cprint(stdscr, f"Всего сотрудников: {len(workers)}")


# Выбор отдела/должности для фильтрации
def choose_filter(stdscr):
    cprint(stdscr, "\nФильтрация списка:")
    cprint(stdscr, "  1. Все сотрудники")
    cprint(stdscr, "  2. По отделу")
    cprint(stdscr, "  3. По должности")
    cprint(stdscr, "  0. Отмена")

    while True:
        choice = cinput(stdscr, 5, 4, "Выберите пункт: ").strip()
        if choice == "0":
            return None, None
        if choice == "1":
            return None, None
        if choice == "2":
            return choose_department_filter(), None
        if choice == "3":
            return None, choose_position_filter()
        cprint(stdscr, "Некорректный выбор, попробуйте снова.")


def choose_department_filter(stdscr):
    deps = fetch_departments()
    if not deps:
        cprint(stdscr, "⚠️  В базе нет отделов.")
        return None

    cprint(stdscr, "\nВыберите отдел:")
    for i, d in enumerate(deps, start=1):
        cprint(stdscr, f"  {i}. {d['name']}")
    while True:
        c = cinput(stdscr, 5, 4, "Введите номер или 0 для отмены: ").strip()
        if c == "0":
            return None
        if c.isdigit() and 1 <= int(c) <= len(deps):
            return deps[int(c) - 1]['id']
        cprint(stdscr, "Некорректный номер.")


def choose_position_filter(stdscr):
    pos = fetch_positions()
    if not pos:
        cprint(stdscr, "⚠️  В базе нет должностей.")
        return None

    cprint(stdscr, "\nВыберите должность:")
    for i, p in enumerate(pos, start=1):
        cprint(stdscr, f"  {i}. {p['name']}")
    while True:
        c = cinput(stdscr, 5, 4, "Введите номер или 0 для отмены: ").strip()
        if c == "0":
            return None
        if c.isdigit() and 1 <= int(c) <= len(pos):
            return pos[int(c) - 1]['id']
        cprint(stdscr, "Некорректный номер.")


# Основной поток — вывод списка сотрудников
def list_workers_flow(stdscr):
    """
    Отображает список сотрудников с возможностью фильтрации по отделу или должности.
    """
    cprint(stdscr, "\n=== Просмотр списка сотрудников ===")
    dep_id, pos_id = choose_filter()
    workers = fetch_workers(department_id=dep_id, position_id=pos_id)
    print_workers_table(workers)
    cinput(stdscr, 5, 4, "\nНажмите Enter для возврата в меню...")


# Тестовый запуск
if __name__ == "__main__":
    list_workers_flow()
