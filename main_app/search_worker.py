# main_app/search_worker.py
from db.database import get_connection
from ui.curses_utils import cinput, cprint


# Получаем список всех столбцов таблицы Workers
def get_worker_columns():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(Workers)")
        columns = [row["name"] for row in cur.fetchall()]
        return columns
    finally:
        conn.close()


# Поиск сотрудников по выбранному столбцу
def search_workers_by_column(column: str, value: str):
    """
    Поиск в Workers по колонке column, частичное совпадение через LIKE.
    Возвращает список dict-подобных результатов.
    """
    if not column:
        return []

    conn = get_connection()
    try:
        cur = conn.cursor()
        query = f"""
            SELECT W.id, W.fio, P.name AS position_name, D.name AS department_name, W.*
            FROM Workers AS W
            LEFT JOIN Positions AS P ON W.position_id = P.id
            LEFT JOIN Departments AS D ON W.department_id = D.id
            WHERE W.{column} LIKE ?
            ORDER BY W.fio ASC
        """
        cur.execute(query, (f"%{value}%",))
        return cur.fetchall()
    finally:
        conn.close()


# Основной поток поиска
def search_worker_flow(stdscr):
    cprint(stdscr, "\n=== Поиск сотрудника ===")

    columns = get_worker_columns()
    if not columns:
        cprint(stdscr, "⚠️  Таблица сотрудников пуста или не существует.")
        return

    cprint(stdscr, "\nДоступные поля для поиска:")
    for i, col in enumerate(columns, start=1):
        cprint(stdscr, f"  {i}. {col}")

    while True:
        col_choice = cinput(stdscr, 5, 4, "\nВыберите номер поля для поиска или 0 для отмены: ").strip()
        if col_choice == "0":
            return
        if col_choice.isdigit() and 1 <= int(col_choice) <= len(columns):
            selected_column = columns[int(col_choice) - 1]
            break
        cprint(stdscr, "Некорректный выбор, попробуйте снова.")

    search_value = cinput(stdscr, 5, 4, f"Введите значение для поиска в поле '{selected_column}': ").strip()
    if not search_value:
        cprint(stdscr, "⚠️  Значение для поиска не может быть пустым.")
        return

    results = search_workers_by_column(selected_column, search_value)
    if not results:
        cprint(stdscr, "\n❌ Сотрудники не найдены.")
        return

    cprint(stdscr, f"\n✅ Найдено {len(results)} совпадений:\n")
    for i, w in enumerate(results, start=1):
        cprint(stdscr, f"{i}. {w['fio']} — {w['position_name']} ({w['department_name']})")

    cinput(stdscr, 5, 4, "\nНажмите Enter для возврата в меню...")


# Тестовый запуск
if __name__ == "__main__":
    search_worker_flow()
