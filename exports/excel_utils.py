import pandas as pd
from db.database import get_connection
from pathlib import Path
import os
import shutil
from datetime import datetime

def export_database_to_excel():
    """
    Кэширует всю базу данных SQLite в Excel.
    Создаёт резервную копию и сохраняет в backup/ с timestamp.
    """
    conn = get_connection()
    tables = ["Admins", "Departments", "Positions", "Workers"]
    excel_path = Path("backup") / "hr_cache.xlsx"
    excel_path.parent.mkdir(exist_ok=True)

    with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
        for table_name in tables:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            df.to_excel(writer, sheet_name=table_name, index=False)

    # Создаём резервную копию с timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = Path("backup") / f"hr_backup_{timestamp}.xlsx"
    shutil.copy(excel_path, backup_path)

    print(f"База экспортирована в Excel: {excel_path}")
    print(f"Резервная копия создана: {backup_path}")
    conn.close()
