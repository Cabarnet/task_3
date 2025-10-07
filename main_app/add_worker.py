# main_app/add_worker.py
import re
from datetime import datetime
from db.database import get_connection
from ui.curses_utils import cinput, cprint

# Регулярные выражения для валидации (все проверки через regex)
RE_FIO = re.compile(r"^[А-ЯЁа-яёA-Za-z\s\-]{3,100}$")            # ФИО: буквы, пробелы, дефис
RE_EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")             # простой валидатор email
RE_PHONE = re.compile(r"^\+\d{10,14}$")                          # телефон: + и 10-14 цифр
RE_BIRTH = re.compile(r"^(0[1-9]|[12]\d|3[01])\.(0[1-9]|1[0-2])\.(19|20)\d{2}$")  # ДД.MM.ГГГГ
RE_PASSPORT = re.compile(r"^\d{6,10}$")                          # паспорт: 6-10 цифр (вариант)
RE_LOGIN = re.compile(r"^[A-Za-z0-9_]{3,20}$")                   # логин: лат/цифры/_
RE_PASSWORD = re.compile(r"^\S{6,}$")                            # пароль: минимум 6 непробельных символов


# Получение списка должностей из БД
def fetch_positions():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM Positions ORDER BY id")
        return cur.fetchall()
    finally:
        conn.close()


# Получение списка отделов из БД
def fetch_departments():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM Departments ORDER BY id")
        return cur.fetchall()
    finally:
        conn.close()


# Проверка уникальности логина среди Workers и Admins
def is_login_unique(login: str) -> bool:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM Workers WHERE login = ? LIMIT 1", (login,))
        if cur.fetchone():
            return False
        cur.execute("SELECT 1 FROM Admins WHERE login = ? LIMIT 1", (login,))
        return cur.fetchone() is None
    finally:
        conn.close()


# Вспомогательная функция выбора пункта из списка (возвращает id)
def choose_from_list(stdscr, items, label: str):
    """
    items: list of rows with [id, name] (sqlite Row or tuple)
    Возвращает selected id (int) или None, если пользователь отменил.
    """
    if not items:
        cprint(stdscr, f"⚠️ Список для выбора ({label}) пуст.")
        return None

    cprint(stdscr, f"\nВыберите {label}:")
    for i, it in enumerate(items, start=1):
        # row may be sqlite3.Row with indices 0/1 or tuple
        _id = it[0]
        _name = it[1]
        cprint(stdscr, f"  {i}. {_name} (ID={_id})")

    while True:
        choice = cinput(stdscr, 5, 4, stdscr, 5, 4, f"Введите номер (1..{len(items)}) или '0' для отмены: ").strip()
        if choice == "0":
            return None
        if not choice.isdigit():
            cprint(stdscr, "Введите число.")
            continue
        idx = int(choice)
        if 1 <= idx <= len(items):
            return items[idx - 1][0]
        cprint(stdscr, "Неверный номер. Попробуйте снова.")


# Ввод и валидация ФИО
def prompt_fio(stdscr):
    while True:
        try:
            fio = cinput(stdscr, 5, 4, stdscr, 5, 4, "ФИО (Фамилия Имя Отчество): ").strip()
            if not fio:
                raise ValueError("ФИО не может быть пустым.")
            if not RE_FIO.match(fio):
                raise ValueError("ФИО должно содержать только буквы, пробелы или дефисы (3–100 символов).")
            return fio
        except ValueError as e:
            cprint(stdscr, f"Ошибка: {e}")


# Ввод и валидация телефона
def prompt_phone(stdscr):
    while True:
        try:
            phone = cinput(stdscr, 5, 4, stdscr, 5, 4, "Телефон (формат +71234567890): ").strip()
            if not phone:
                return None  # телефон может быть опционален
            if not RE_PHONE.match(phone):
                raise ValueError("Телефон должен быть в формате + и 10–14 цифр, например +71234567890.")
            return phone
        except ValueError as e:
            cprint(stdscr, f"Ошибка: {e}")


# Ввод и валидация email
def prompt_email(stdscr):
    while True:
        try:
            email = cinput(stdscr, 5, 4, stdscr, 5, 4, "Email: ").strip()
            if not email:
                return None
            if not RE_EMAIL.match(email):
                raise ValueError("Неверный формат email (пример: user@example.com).")
            return email
        except ValueError as e:
            cprint(stdscr, f"Ошибка: {e}")


# Ввод и проверка даты рождения
def prompt_birthdate(stdscr):
    while True:
        try:
            birth = cinput(stdscr, 5, 4, stdscr, 5, 4, "Дата рождения (ДД.MM.ГГГГ): ").strip()
            if not birth:
                return None
            if not RE_BIRTH.match(birth):
                raise ValueError("Формат даты: ДД.MM.ГГГГ (например 31.12.1990).")
            # Дополнительная проверка на реальные даты (напр., 30 февраля)
            day, month, year = map(int, birth.split("."))
            datetime(year, month, day)  # бросит ValueError, если дата некорректна
            return birth
        except ValueError as e:
            cprint(stdscr, f"Ошибка: {e}")


# Ввод места регистрации (адрес)
def prompt_address(stdscr):
    while True:
        try:
            addr = cinput(stdscr, 5, 4, stdscr, 5, 4, "Место регистрации (адрес): ").strip()
            if not addr:
                raise ValueError("Адрес не может быть пустым.")
            if len(addr) < 3:
                raise ValueError("Адрес слишком короткий.")
            return addr
        except ValueError as e:
            cprint(stdscr, f"Ошибка: {e}")


# Ввод и проверка номера паспорта
def prompt_passport(stdscr):
    while True:
        try:
            passport = cinput(stdscr, 5, 4, "Номер паспорта (6–10 цифр): ").strip()
            if not passport:
                raise ValueError("Номер паспорта не может быть пустым.")
            if not RE_PASSPORT.match(passport):
                raise ValueError("Номер паспорта должен содержать только цифры (6–10 цифр).")
            return passport
        except ValueError as e:
            cprint(stdscr, f"Ошибка: {e}")


# Ввод логина для сотрудника
def prompt_login(stdscr):
    while True:
        try:
            login = cinput(stdscr, 5, 4, "Логин для сотрудника (3–20 латинских/цифры/_): ").strip()
            if not login:
                raise ValueError("Логин не может быть пустым.")
            if not RE_LOGIN.match(login):
                raise ValueError("Логин: только латинские буквы, цифры или '_' (3–20 символов).")
            if not is_login_unique(login):
                raise ValueError("Логин уже занят. Выберите другой.")
            return login
        except ValueError as e:
            cprint(stdscr, f"Ошибка: {e}")


# Ввод пароля для сотрудника
def prompt_password(stdscr):
    while True:
        try:
            pwd = cinput(stdscr, 5, 4, "Пароль для сотрудника (минимум 6 символов, без пробелов): ").strip()
            if not pwd:
                raise ValueError("Пароль не может быть пустым.")
            if not RE_PASSWORD.match(pwd):
                raise ValueError("Пароль: минимум 6 символов, без пробельных символов.")
            return pwd
        except ValueError as e:
            cprint(stdscr, f"Ошибка: {e}")


# Добавление сотрудника (основная последовательность)
def add_worker_flow(stdscr):
    """
    Последовательный ввод всех полей сотрудника и запись в таблицу Workers.
    Поля: fio, position_id, department_id, phone, email, birthdate, address, passport, login, password
    """
    # Проверяем, есть ли должности и отделы
    positions = fetch_positions()
    departments = fetch_departments()
    if not positions:
        cprint(stdscr, "⚠️ Невозможно добавить сотрудника: в базе нет должностей. Сначала добавьте должности (Настройка БД).")
        return
    if not departments:
        cprint(stdscr, "⚠️ Невозможно добавить сотрудника: в базе нет отделов. Сначала добавьте отделы (Настройка БД).")
        return

    cprint(stdscr, "\n=== Добавление нового сотрудника ===")
    fio = prompt_fio()

    # Выбор должности
    position_id = choose_from_list(positions, "должность")
    if position_id is None:
        cprint(stdscr, "Добавление отменено.")
        return

    # Выбор отдела
    department_id = choose_from_list(departments, "отдел")
    if department_id is None:
        cprint(stdscr, "Добавление отменено.")
        return

    phone = prompt_phone()
    email = prompt_email()
    birthdate = prompt_birthdate()
    address = prompt_address()
    passport = prompt_passport()
    login = prompt_login()
    password = prompt_password()

    # Подтверждение перед записью
    cprint(stdscr, "\nПроверьте введённые данные:")
    cprint(stdscr, f"  ФИО: {fio}")
    cprint(stdscr, f"  Должность ID: {position_id}")
    cprint(stdscr, f"  Отдел ID: {department_id}")
    cprint(stdscr, f"  Телефон: {phone or '—'}")
    cprint(stdscr, f"  Email: {email or '—'}")
    cprint(stdscr, f"  ДР: {birthdate or '—'}")
    cprint(stdscr, f"  Адрес: {address}")
    cprint(stdscr, f"  Паспорт: {passport}")
    cprint(stdscr, f"  Логин: {login}")
    ok = cinput(stdscr, 5, 4, "Сохранить сотрудника? (Y/N): ").strip().lower()
    if ok != "y":
        cprint(stdscr, "Добавление отменено.")
        return

    # Вставка в базу
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO Workers
            (fio, position_id, department_id, phone, email, birthdate, address, passport, login, password)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (fio, position_id, department_id, phone, email, birthdate, address, passport, login, password),
        )
        conn.commit()
        cprint(stdscr, "✅ Сотрудник успешно добавлен в базу.")
    except Exception as e:
        # Пользовательские сообщения без traceback
        cprint(stdscr, "❌ Ошибка при записи в базу. Сотрудник не добавлен.")
        cprint(stdscr, "Причина:", str(e))
    finally:
        conn.close()


# Позволяет импортировать функцию add_worker_flow в меню
if __name__ == "__main__":
    add_worker_flow()
