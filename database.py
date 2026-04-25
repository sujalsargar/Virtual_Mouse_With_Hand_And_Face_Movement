import sqlite3

# Step 1 — Create Database and Table
def create_database():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        sensitivity REAL,
        dead_zone INTEGER,
        blink_threshold REAL,
        scroll_speed INTEGER
    )
    """)

    conn.commit()
    conn.close()


# Step 2 — Add Default Users
def add_default_users():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    users = [
        ("atharvad", 20, 8, 0.015, 25),
        ("kunalt", 30, 6, 0.014, 20),
        ("sandesh", 25, 10, 0.016, 30),
        ("sujal", 18, 7, 0.015, 15)
    ]

    cursor.executemany("""
    INSERT INTO users (name, sensitivity, dead_zone, blink_threshold, scroll_speed)
    VALUES (?, ?, ?, ?, ?)
    """, users)

    conn.commit()
    conn.close()


# Step 3 — Load User Settings
def get_user(name):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE name=?", (name,))
    user = cursor.fetchone()

    conn.close()

    return user


# Run setup when file is executed
if __name__ == "__main__":
    create_database()
    add_default_users()

    user = get_user("sujal")
    print("Loaded user settings:", user)