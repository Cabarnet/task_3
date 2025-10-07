# main_app/export_excel.py
from pathlib import Path
import pandas as pd
from db.database import get_connection
from ui.curses_utils import cinput, cprint

BACKUP_DIR = Path("backup")
BACKUP_DIR.mkdir(exist_ok=True)  # создаём папку backup, если нет

def export_database_to_excel(stdscr):
    """
    Экспорт всей базы данных в Excel.
    Каждая таблица в отдельном листе: Workers, Departments, Positions
    """
    cprint(stdscr, "\n=== Экспорт базы данных в Excel ===")
    backup_path = BACKUP_DIR / "hr_backup.xlsx"

    conn = get_connection()
    try:
        # Список таблиц для экспорта
        tables = ["Workers", "Departments", "Positions"]

        # Создаем ExcelWriter
        with pd.ExcelWriter(backup_path, engine="openpyxl") as writer:
            for table in tables:
                df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
                df.to_excel(writer, sheet_name=table, index=False)
        cprint(stdscr, f"✅ Экспорт выполнен успешно. Файл сохранен: {backup_path}")
    except Exception as e:
        cprint(stdscr, "❌ Ошибка при экспорте:", e)
    finally:
        conn.close()

    cinput(stdscr, 5, 4, "\nНажмите Enter для возврата в меню...")


# Тестовый запуск
if __name__ == "__main__":
    export_database_to_excel()
