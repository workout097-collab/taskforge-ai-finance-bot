import sqlite3

from datetime import datetime

def init_db():

    conn = sqlite3.connect("expenses.db")

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        category TEXT,
        amount INTEGER,
        created_at TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        user_id INTEGER PRIMARY KEY,
        currency TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS budgets (
        user_id INTEGER PRIMARY KEY,
        amount INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS goals (
        user_id INTEGER PRIMARY KEY,
        goal_name TEXT,
        goal_amount INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        amount INTEGER
    )
    """)


    conn.commit()
    conn.close()

def add_expense_db(user_id, category, amount):

    conn = sqlite3.connect("expenses.db")

    cursor = conn.cursor()

    created_at = datetime.now().strftime("%Y-%m-%d")

    cursor.execute(
        "INSERT INTO expenses (user_id, category, amount, created_at) VALUES (?, ?, ?, ?)",
        (user_id, category, amount, created_at)
    )

    conn.commit()
    conn.close()

def get_expenses_db(user_id):

    conn = sqlite3.connect("expenses.db")

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses WHERE user_id = ?",
                   (user_id,)
                   )

    expenses = cursor.fetchall()

    conn.close()

    return expenses

def delete_expense_db(user_id, expense_id):

    conn = sqlite3.connect("expenses.db")

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM expenses WHERE id = ? AND user_id = ?",
        (expense_id, user_id)
    )

    conn.commit()
    conn.close()

def set_budget_db(user_id, amount):

    conn = sqlite3.connect("expenses.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO budgets (user_id, amount)
        VALUES (?, ?)
        """,
        (user_id, amount)
    )

    conn.commit()
    conn.close()


def get_budget_db(user_id):

    conn = sqlite3.connect("expenses.db")

    cursor = conn.cursor()

    cursor.execute(
        "SELECT amount FROM budgets WHERE user_id = ?",
        (user_id,)
    )

    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]

    return None

def get_month_expenses_db(user_id, month):

    conn = sqlite3.connect("expenses.db")

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM expenses WHERE user_id = ? AND created_at LIKE ?",
        (user_id, f"{month}%")
    )

    expenses = cursor.fetchall()

    conn.close()

    return expenses

def set_currency_db(user_id, currency):

    conn = sqlite3.connect("expenses.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO settings
        (user_id, currency)
        VALUES (?, ?)
        """,
        (user_id, currency)
    )

    conn.commit()
    conn.close()


def get_currency_db(user_id):

    conn = sqlite3.connect("expenses.db")

    cursor = conn.cursor()

    cursor.execute(
        "SELECT currency FROM settings WHERE user_id = ?",
        (user_id,)
    )

    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]

    return "$"

def set_goal_db(user_id, goal_name, goal_amount):

    conn = sqlite3.connect("expenses.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO goals
        (user_id, goal_name, goal_amount)
        VALUES (?, ?, ?)
        """,
        (user_id, goal_name, goal_amount)
    )

    conn.commit()
    conn.close()


def get_goal_db(user_id):

    conn = sqlite3.connect("expenses.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT goal_name, goal_amount
        FROM goals
        WHERE user_id = ?
        """,
        (user_id,)
    )

    result = cursor.fetchone()

    conn.close()

    return result

def add_subscription_db(user_id, name, amount):

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO subscriptions (user_id, name, amount) VALUES (?, ?, ?)",
        (user_id, name, amount)
    )

    conn.commit()
    conn.close()

def get_subscriptions_db(user_id):

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM subscriptions WHERE user_id = ?",
        (user_id,)
    )

    subscriptions = cursor.fetchall()

    conn.close()

    return subscriptions