import kagglehub
import sqlite3
from pathlib import Path

# Descargar y conectar
path = kagglehub.dataset_download("wyattowalsh/basketball")
db_path = Path(path) / "nba.sqlite"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Mostrar tablas
print("Tablas disponibles:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(tables)

# Mostrar columnas de cada tabla
for table in tables:
    print(f"\nColumnas en {table[0]}:")
    cursor.execute(f"PRAGMA table_info({table[0]});")
    for col in cursor.fetchall():
        print(f" - {col[1]}")
