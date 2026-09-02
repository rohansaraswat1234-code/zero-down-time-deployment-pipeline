import sqlite3
from werkzeug.security import generate_password_hash

DB_PATH = "database/users.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'user')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

admin_password = generate_password_hash("admin123")
user_password = generate_password_hash("user123")

cursor.execute("""
INSERT OR IGNORE INTO users (name, email, password, role)
VALUES (?, ?, ?, ?)
""", ("System Admin", "admin@pipeline.com", admin_password, "admin"))

cursor.execute("""
INSERT OR IGNORE INTO users (name, email, password, role)
VALUES (?, ?, ?, ?)
""", ("Demo Developer", "user@pipeline.com", user_password, "user"))

conn.commit()
conn.close()

print("Users database created successfully!")
