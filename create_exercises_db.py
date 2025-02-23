import sqlite3

# Yhteys SQLite-tietokantaan (luo tiedoston, jos sitä ei ole)
conn = sqlite3.connect("workouts.db")
cursor = conn.cursor()

# Luodaan taulu
cursor.execute("""
CREATE TABLE IF NOT EXISTS workouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    exercise TEXT,
    reps INTEGER,
    weight REAL
)
""")

conn.commit()  # Tallennetaan muutokset