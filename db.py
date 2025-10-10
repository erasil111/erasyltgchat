import sqlite3
from typing import Optional

DB_NAME = "bot.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def add_user(user_id: int, username: Optional[str]):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    if not c.fetchone():
        c.execute("INSERT INTO users (user_id, username, balance) VALUES (?, ?, 0)", (user_id, username or ""))
    else:
        # обновим username при изменении
        c.execute("UPDATE users SET username = ? WHERE user_id = ?", (username or "", user_id))
    conn.commit()
    conn.close()

def get_balance(user_id: int) -> int:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def update_balance(user_id: int, new_balance: int):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
    conn.commit()
    conn.close()

def consume_token(user_id: int) -> bool:
    """
    Атомарно списать 1 токен. Возвращает True если списали, False если не хватило.
    Использует условное обновление — предотвращает гонки.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance - 1 WHERE user_id = ? AND balance > 0", (user_id,))
    success = c.rowcount > 0
    conn.commit()
    conn.close()
    return success

def add_tokens_by_id(user_id: int, amount: int):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    if not c.fetchone():
        c.execute("INSERT INTO users (user_id, username, balance) VALUES (?, ?, ?)", (user_id, "", amount))
    else:
        c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def find_user_by_username(username: str) -> Optional[int]:
    username = username.lstrip("@")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None
