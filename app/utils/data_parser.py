import sqlite3
import pandas as pd

conn = sqlite3.connect("nba.sqlite")
cursor = conn.cursor()

# Ver todas las tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tablas disponibles:", tables)

# Por ejemplo, exportar la tabla de juegos
df = pd.read_sql_query("SELECT * FROM Game", conn)
df.to_csv("games.csv", index=False)

conn.close()
