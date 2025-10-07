# main_app/fire_worker.py
import getpass
from db.database import get_connection
from ui.curses_utils import cinput, cprint


# Получаем список сотрудников для выбора
def fetch_workers():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT W.id, W.fio, P.name AS position_name, D.name AS department_name
            FROM Workers AS W
            LEFT JOIN Positions AS P ON W.position_id = P.id
            LEFT JOIN Departments AS D ON W.department_id = D.id
            ORDER BY W.fio ASC
        """)
        return cur.fetchall()
    finally:
        conn.close()


# Получаем пароль администратора из БД
def fetch_admin_password(login: str):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT password FROM Admins WHERE login = ?", (login,))
        row = cur.fetchone()
        return row["password"] if row else None
    finally:
        conn.close()


# Удаление сотрудника по ID
def delete_worker(worker_id: int):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM Workers WHERE id = ?", (worker_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


# Выбор сотрудника из списка
def choose_worker(stdscr):
    workers = fetch_workers()
    if not workers:
        cprint(stdscr, "⚠️  В базе нет сотрудников для увольнения.")
        return None

    cprint(stdscr, "\n📋 Список сотрудников:")
    for i, w in enumerate(workers, start=1):
        cprint(stdscr, f"  {i}. {w['fio']} ({w['position_name']} — {w['department_name']})")

    while True:
        choice = cinput(stdscr, 5, 4, "\nВведите номер сотрудника или 0 для отмены: ").strip()
        if choice == "0":
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(workers):
            return workers[int(choice) - 1]
        cprint(stdscr, "Некорректный выбор, попробуйте снова.")


# Подтверждение удаления
def confirm_fire(stdscr, worker_fio: str):
    cprint(stdscr, f"\n⚠️  Вы собираетесь уволить сотрудника: {worker_fio}")
    confirm = cinput(stdscr, 5, 4, "Подтвердите (y/n): ").strip().lower()
    return confirm == "y"


# Проверка пароля администратора
def check_admin_password(stdscr):
    login = cinput(stdscr, 5, 4, "\nВведите логин администратора: ").strip()
    stored_password = fetch_admin_password(login)
    if not stored_password:
        cprint(stdscr, "❌ Администратор не найден.")
        return False

    password = getpass.getpass("Введите пароль: ")
    if password != stored_password:
        cprint(stdscr, "❌ Неверный пароль.")
        return False

    return True


# Основной поток логики увольнения
def fire_worker_flow(stdscr):
    """
    Позволяет выбрать сотрудника, подтвердить действие и удалить его из базы.
    Для безопасности требуется ввести пароль администратора.
    """
    cprint(stdscr, "\n=== Увольнение сотрудника ===")
    worker = choose_worker()
    if not worker:
        cprint(stdscr, "Отмена операции.")
        return

    if not confirm_fire(worker["fio"]):
        cprint(stdscr, "❎ Увольнение отменено пользователем.")
        return

    if not check_admin_password():
        cprint(stdscr, "🚫 Отказано в доступе.")
        return

    if delete_worker(worker["id"]):
        cprint(stdscr, f"✅ Сотрудник {worker['fio']} успешно удалён из базы.")
    else:
        cprint(stdscr, "⚠️  Не удалось удалить сотрудника.")

    cinput(stdscr, 5, 4, "\nНажмите Enter для возврата в меню...")


# Тестовый запуск
if __name__ == "__main__":
    fire_worker_flow()
