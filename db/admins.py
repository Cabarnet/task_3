from db.database import get_connection

# Создание админа
def add_admin(fio: str, login: str, password: str):
    """Добавляет нового администратора"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO Admins (fio, login, password) VALUES (?, ?, ?)",
            (fio, login, password),
        )
        conn.commit()
        print(f"✅ Администратор '{fio}' успешно добавлен!")
    except Exception as e:
        print(f"❌ Ошибка добавления администратора: {e}")
    finally:
        conn.close()

# Получение администратора по логину
def get_admin_by_login(login: str):
    """Возвращает запись администратора по логину или None"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Admins WHERE login = ?", (login,))
    admin = cur.fetchone()
    conn.close()
    return admin

# Проверка входа
def check_login(login: str, password: str) -> bool:
    """Возвращает True, если логин и пароль верны"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM Admins WHERE login = ? AND password = ?",
        (login, password),
    )
    user = cur.fetchone()
    conn.close()
    return user is not None

# Список админов
def list_admins():
    """Выводит список всех администраторов"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, fio, login FROM Admins")
    admins = cur.fetchall()
    conn.close()

    if not admins:
        print("\nНет зарегистрированных администраторов.")
        return

    print("\n📋 Список администраторов:")
    for idx, admin in enumerate(admins, start=1):
        print(f"  {idx}. {admin['fio']} ({admin['login']})")

# Удаление админа
def delete_admin(login: str):
    """Удаляет администратора по логину"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Admins WHERE login = ?", (login,))
    conn.commit()
    conn.close()
    print(f"🗑️ Администратор с логином '{login}' удалён (если существовал).")

# Создание дефолтного админа
def create_default_admin():
    """Создаёт дефолтного администратора, если таблица пуста"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as cnt FROM Admins")
    count = cur.fetchone()["cnt"]
    if count == 0:
        try:
            cur.execute(
                "INSERT INTO Admins (fio, login, password) VALUES (?, ?, ?)",
                ("Просто Мега Хакер", "mega", "hacker"),
            )
            conn.commit()
        except Exception as e:
            print(f"❌ Ошибка при создании дефолтного администратора: {e}")
    conn.close()
