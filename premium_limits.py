# premium_limits.py
import sqlite3
from datetime import date
from database import get_expenses_db, is_premium

FREE_LIMITS = {
    "expenses_per_month": 50,
    "subscriptions": 3,
    "goals": 1,
    "ai_insights_per_day": 2,
}

def can_add_expense(user_id, month: str) -> tuple[bool, str]:
    if is_premium(user_id):
        return True, "ok"

    expenses = get_expenses_db(user_id)
    month_expenses = [e for e in expenses if e[4].startswith(month)]

    if len(month_expenses) >= FREE_LIMITS["expenses_per_month"]:
        return False, f"❌ Ліміт {FREE_LIMITS['expenses_per_month']} витрат на місяць. Купи Premium за $5/міс для безліміту."

    return True, "ok"


def can_use_ai_insight(user_id) -> tuple[bool, str]:
    if is_premium(user_id):
        return True, "ok"

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    today = date.today().isoformat()

    cursor.execute(
        "SELECT COUNT(*) FROM ai_usage WHERE user_id = ? AND date = ?",
        (user_id, today)
    )
    count = cursor.fetchone()[0]

    if count >= FREE_LIMITS["ai_insights_per_day"]:
        conn.close()
        return False, f"❌ Ліміт {FREE_LIMITS['ai_insights_per_day']} AI-поради на день у безкоштовній версії. Купи Premium за $5/міс."

    # Записуємо використання
    cursor.execute(
        "INSERT INTO ai_usage (user_id, date) VALUES (?, ?)",
        (user_id, today)
    )
    conn.commit()
    conn.close()

    return True, "ok"