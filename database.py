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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        task TEXT,
        completed INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_languages (
        user_id INTEGER PRIMARY KEY,
        language TEXT
    )
    """)



    conn.commit()
    conn.close()

def set_language_db(user_id, language):

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO user_languages
        (user_id, language)
        VALUES (?, ?)
        """,
        (user_id, language)
    )

    conn.commit()
    conn.close()

def get_language_db(user_id):

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT language
        FROM user_languages
        WHERE user_id = ?
        """,
        (user_id,)
    )

    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]

    return "ua"

def save_user(user_id, username, first_name):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO users (user_id, username, first_name)
    VALUES (?, ?, ?)
    """, (user_id, username, first_name))

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

def create_premium_table():

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS premium_users (
        user_id INTEGER PRIMARY KEY,
        premium INTEGER,
        trial_end TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()
create_premium_table()

def add_premium_user(user_id, premium, trial_end):

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO premium_users
    (user_id, premium, trial_end)
    VALUES (?, ?, ?)
    """, (user_id, premium, trial_end))

    conn.commit()
    conn.close()

def get_total_expenses_count():

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM expenses"
    )

    total = cursor.fetchone()[0]

    conn.close()

    return total

def get_total_tasks_count():

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM tasks"
    )

    total = cursor.fetchone()[0]

    conn.close()

    return total



def get_total_users():

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )

    total = cursor.fetchone()[0]

    conn.close()

    return total

def get_premium_user(user_id):

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT premium, trial_end FROM premium_users WHERE user_id = ?",
        (user_id,)
    )

    result = cursor.fetchone()

    conn.close()

    return result

def is_premium(user_id):

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT premium, trial_end
        FROM premium_users
        WHERE user_id = ?
        """,
        (user_id,)
    )

    result = cursor.fetchone()

    conn.close()

    if not result:
        return False

    premium, trial_end = result

    if premium == 1:

        if datetime.now() <= datetime.strptime(
                trial_end,
                "%Y-%m-%d"
        ):

            return True

    return False


def give_premium(user_id):

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO premium_users
        (user_id, premium, trial_end)
        VALUES (?, ?, ?)
        """,
        (
            user_id,
            1,
            "2099-12-31"
        )
    )

    conn.commit()
    conn.close()

def add_task_db(user_id, task):

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO tasks
        (user_id, task, completed)
        VALUES (?, ?, ?)
        """,
        (user_id, task, 0)
    )

    conn.commit()
    conn.close()


def get_tasks_db(user_id):

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM tasks
        WHERE user_id = ?
        """,
        (user_id,)
    )

    tasks = cursor.fetchall()

    conn.close()

    return tasks

def delete_task_db(user_id, task_id):

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, user_id)
    )

    conn.commit()
    conn.close()

def get_premium_users_count():

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM premium_users WHERE premium = 1"
    )

    total = cursor.fetchone()[0]

    conn.close()

    return total

def complete_task_db(user_id, task_id):

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE tasks
        SET completed = 1
        WHERE id = ? AND user_id = ?
        """,
        (task_id, user_id)
    )

    conn.commit()
    conn.close()

def delete_goal_db(user_id):

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM goals WHERE user_id = ?",
        (user_id,)
    )

    conn.commit()
    conn.close()

def clear_expenses_db(user_id):

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM expenses WHERE user_id = ?",
        (user_id,)
    )

    conn.commit()
    conn.close()