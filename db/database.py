import sqlite3
from pathlib import Path

DB_PATH = Path("data/hr.db")
DB_PATH.parent.mkdir(exist_ok=True)  # создаём папку data, если нет

def get_connection():
    """Возвращает объект подключения к SQLite"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # возвращает строки как dict-подобные объекты
    return conn

def init_db():
    """Создаёт таблицы, если их ещё нет"""
    conn = get_connection()
    cur = conn.cursor()

    # Таблица администраторов
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fio TEXT NOT NULL,
        login TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    # Таблица отделов
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    """)

    # Таблица должностей
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Positions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    """)

    # Таблица сотрудников
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Workers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fio TEXT NOT NULL,
        position_id INTEGER NOT NULL,
        department_id INTEGER NOT NULL,
        phone TEXT,
        email TEXT,
        birthdate TEXT,
        address TEXT,
        passport TEXT,
        login TEXT,
        password TEXT,
        FOREIGN KEY(position_id) REFERENCES Positions(id),
        FOREIGN KEY(department_id) REFERENCES Departments(id)
    )
    """)

    conn.commit()
    conn.close()
