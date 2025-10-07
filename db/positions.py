from db.database import get_connection


# Добавление должности
def add_position(name: str):
    """
    Добавляет новую должность в таблицу Positions.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO Positions (name) VALUES (?)", (name,))
        conn.commit()
        print(f"✅ Должность '{name}' успешно добавлена!")
    except Exception as e:
        print(f"❌ Ошибка при добавлении должности: {e}")
    finally:
        conn.close()


# Просмотр всех должностей
def list_positions():
    """
    Выводит список всех должностей с количеством сотрудников на каждой.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT p.id, p.name, COUNT(w.id) AS workers_count
        FROM Positions p
        LEFT JOIN Workers w ON w.position_id = p.id
        GROUP BY p.id, p.name
        ORDER BY p.name
        """
    )
    positions = cur.fetchall()
    conn.close()

    if not positions:
        print("\n📋 Список должностей пуст.")
        return

    print("\n📋 Список должностей:")
    for pos in positions:
        print(f"  {pos['id']}. {pos['name']} ({pos['workers_count']} сотрудников)")


# Поиск должности
def find_position(name: str):
    """
    Ищет должности по названию (частичное совпадение, без регистра).
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT p.id, p.name, COUNT(w.id) AS workers_count
        FROM Positions p
        LEFT JOIN Workers w ON w.position_id = p.id
        WHERE LOWER(p.name) LIKE ?
        GROUP BY p.id, p.name
        """,
        (f"%{name.lower()}%",),
    )
    results = cur.fetchall()
    conn.close()

    if not results:
        print(f"\n❌ Должности, содержащие '{name}', не найдены.")
        return

    print(f"\n🔍 Найдено совпадений: {len(results)}")
    for pos in results:
        print(f"  {pos['id']}. {pos['name']} ({pos['workers_count']} сотрудников)")


# Обновление данных
def update_position(pos_id: int, **kwargs):
    """
    Обновляет данные должности.
    Пример вызова:
        update_position(3, name="Инженер-программист")
    """
    if not kwargs:
        print("⚠️ Нет данных для обновления.")
        return

    conn = get_connection()
    cur = conn.cursor()
    fields = ", ".join([f"{k} = ?" for k in kwargs.keys()])
    values = list(kwargs.values()) + [pos_id]

    try:
        cur.execute(f"UPDATE Positions SET {fields} WHERE id = ?", values)
        conn.commit()
        print(f"✅ Должность с ID={pos_id} обновлена.")
    except Exception as e:
        print(f"❌ Ошибка при обновлении должности: {e}")
    finally:
        conn.close()


# Удаление должности
def delete_position(pos_id: int):
    """
    Удаляет должность по ID (при этом у сотрудников нужно обнулить position_id).
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE Workers SET position_id = NULL WHERE position_id = ?", (pos_id,))
        cur.execute("DELETE FROM Positions WHERE id = ?", (pos_id,))
        conn.commit()
        print(f"🗑️ Должность с ID={pos_id} удалена.")
    except Exception as e:
        print(f"❌ Ошибка при удалении должности: {e}")
    finally:
        conn.close()
