from db.database import get_connection

# Добвление сотрудника
def add_worker(fio: str, position: str, salary: float, department_id: int, phone: str = None, email: str = None):
    """
    Добавляет нового сотрудника в таблицу Workers.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO Workers (fio, position, salary, department_id, phone, email)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (fio, position, salary, department_id, phone, email),
        )
        conn.commit()
        print(f"✅ Сотрудник '{fio}' успешно добавлен!")
    except Exception as e:
        print(f"❌ Ошибка при добавлении сотрудника: {e}")
    finally:
        conn.close()

# Просмотр всех сотрудников
def list_workers():
    """
    Выводит всех сотрудников с указанием отдела и оклада.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT w.id, w.fio, w.position, w.salary, d.name AS department
        FROM Workers w
        LEFT JOIN Departments d ON w.department_id = d.id
        ORDER BY w.fio
        """
    )
    workers = cur.fetchall()
    conn.close()

    if not workers:
        print("\nНет зарегистрированных сотрудников.")
        return

    print("\n👥 Список сотрудников:")
    for idx, w in enumerate(workers, start=1):
        print(f"  {idx}. {w['fio']} | {w['position']} | {w['salary']} руб | Отдел: {w['department'] or '—'}")


# Поиск сотрудника
def find_worker_by_name(fio: str):
    """
    Находит сотрудника по ФИО (поиск частичный, регистронезависимый).
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT w.id, w.fio, w.position, w.salary, d.name AS department
        FROM Workers w
        LEFT JOIN Departments d ON w.department_id = d.id
        WHERE LOWER(w.fio) LIKE ?
        """,
        (f"%{fio.lower()}%",),
    )
    results = cur.fetchall()
    conn.close()

    if not results:
        print(f"\n❌ Сотрудники с именем '{fio}' не найдены.")
        return

    print(f"\n🔍 Найдено совпадений: {len(results)}")
    for idx, w in enumerate(results, start=1):
        print(f"  {idx}. {w['fio']} | {w['position']} | {w['salary']} руб | Отдел: {w['department'] or '—'}")


# Обновление данных сотрудника
def update_worker(worker_id: int, **kwargs):
    """
    Обновляет поля сотрудника (fio, position, salary, phone, email, department_id).
    Пример вызова:
        update_worker(3, salary=95000, position="Team Lead")
    """
    if not kwargs:
        print("⚠️ Нет данных для обновления.")
        return

    conn = get_connection()
    cur = conn.cursor()

    fields = ", ".join([f"{k} = ?" for k in kwargs.keys()])
    values = list(kwargs.values()) + [worker_id]

    try:
        cur.execute(f"UPDATE Workers SET {fields} WHERE id = ?", values)
        conn.commit()
        print(f"✅ Сотрудник с ID={worker_id} обновлён.")
    except Exception as e:
        print(f"❌ Ошибка при обновлении сотрудника: {e}")
    finally:
        conn.close()


# Удаление
def delete_worker(worker_id: int):
    """
    Удаляет сотрудника по ID.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Workers WHERE id = ?", (worker_id,))
    conn.commit()
    conn.close()
    print(f"🗑️ Сотрудник с ID={worker_id} удалён (если существовал).")