from db.database import get_connection

# Работа с отделами

# Добавление
def add_department(name: str, description: str = None):
    """
    Добавляет новый отдел в таблицу Departments.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO Departments (name, description)
            VALUES (?, ?)
            """,
            (name, description),
        )
        conn.commit()
        print(f"✅ Отдел '{name}' успешно добавлен!")
    except Exception as e:
        print(f"❌ Ошибка при добавлении отдела: {e}")
    finally:
        conn.close()


# Просмотр всех
def list_departments():
    """
    Выводит список всех отделов с их описанием и количеством сотрудников.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT d.id, d.name, d.description,
               COUNT(w.id) AS workers_count
        FROM Departments d
        LEFT JOIN Workers w ON w.department_id = d.id
        GROUP BY d.id, d.name, d.description
        ORDER BY d.name
        """
    )
    departments = cur.fetchall()
    conn.close()

    if not departments:
        print("\n🏢 Нет зарегистрированных отделов.")
        return

    print("\n📋 Список отделов:")
    for dep in departments:
        print(f"  {dep['id']}. {dep['name']} — {dep['description'] or '—'} ({dep['workers_count']} сотрудников)")


# Поиск
def find_department(name: str):
    """
    Ищет отдел по названию (частичное совпадение, без регистра).
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT d.id, d.name, d.description,
               COUNT(w.id) AS workers_count
        FROM Departments d
        LEFT JOIN Workers w ON w.department_id = d.id
        WHERE LOWER(d.name) LIKE ?
        GROUP BY d.id, d.name, d.description
        """,
        (f"%{name.lower()}%",),
    )
    results = cur.fetchall()
    conn.close()

    if not results:
        print(f"\n❌ Отдел '{name}' не найден.")
        return

    print(f"\n🔍 Найдено совпадений: {len(results)}")
    for dep in results:
        print(f"  {dep['id']}. {dep['name']} — {dep['description'] or '—'} ({dep['workers_count']} сотрудников)")


# Обновление данных
def update_department(dep_id: int, **kwargs):
    """
    Обновляет данные отдела.
    Пример вызова:
        update_department(2, name="Отдел продаж", description="Работа с клиентами")
    """
    if not kwargs:
        print("⚠️ Нет данных для обновления.")
        return

    conn = get_connection()
    cur = conn.cursor()

    fields = ", ".join([f"{k} = ?" for k in kwargs.keys()])
    values = list(kwargs.values()) + [dep_id]

    try:
        cur.execute(f"UPDATE Departments SET {fields} WHERE id = ?", values)
        conn.commit()
        print(f"✅ Отдел с ID={dep_id} обновлён.")
    except Exception as e:
        print(f"❌ Ошибка при обновлении отдела: {e}")
    finally:
        conn.close()


# Удаление
def delete_department(dep_id: int):
    """
    Удаляет отдел по ID (при этом у сотрудников нужно обнулить department_id).
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Обнуляем department_id у сотрудников, чтобы не нарушить целостность
        cur.execute("UPDATE Workers SET department_id = NULL WHERE department_id = ?", (dep_id,))
        cur.execute("DELETE FROM Departments WHERE id = ?", (dep_id,))
        conn.commit()
        print(f"🗑️ Отдел с ID={dep_id} удалён.")
    except Exception as e:
        print(f"❌ Ошибка при удалении отдела: {e}")
    finally:
        conn.close()
