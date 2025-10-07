# main_app/clear_db.py
from db.database import get_connection
from ui.curses_utils import cinput, cprint


# Функция очистки базы данных с проверкой пароля
def clear_database_flow(stdscr):
    cprint(stdscr, "\n=== Очистка базы данных ===")
    confirm = cinput(stdscr, 5, 4, "ВЫ действительно хотите удалить всю базу данных? (Y/N): ").strip().upper()
    if confirm != "Y":
        cprint(stdscr, "❌ Очистка отменена.")
        return

    admin_login = cinput(stdscr, 5, 4, "Введите логин администратора: ").strip()
    admin_password = cinput(stdscr, 5, 5, "Введите пароль администратора: ").strip()

    conn = get_connection()
    try:
        cur = conn.cursor()
        # Проверка логина и пароля администратора
        cur.execute("SELECT * FROM Admins WHERE login=? AND password=?", (admin_login, admin_password))
        admin = cur.fetchone()
        if not admin:
            cprint(stdscr, "❌ Ошибка: неверный логин или пароль администратора.")
            return

        # Очистка всех таблиц (не удаляем сами таблицы)
        tables_to_clear = ["Workers", "Departments", "Positions"]
        for table in tables_to_clear:
            cur.execute(f"DELETE FROM {table}")
        conn.commit()
        cprint(stdscr, "✅ Все данные успешно удалены.")
    finally:
        conn.close()

    cinput(stdscr, 5, 4, "\nНажмите Enter для возврата в меню...")


# Тестовый запуск
if __name__ == "__main__":
    clear_database_flow()
