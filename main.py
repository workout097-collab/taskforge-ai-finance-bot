from datetime import datetime, timedelta
from main_keyboard import get_main_keyboard
import sqlite3
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
import matplotlib.pyplot as plt
from aiogram.types import FSInputFile
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from reportlab.pdfgen import canvas
from aiogram.types import FSInputFile
from database import *
from database import get_premium_users_count
from database import delete_task_db
from database import delete_goal_db
from database import clear_expenses_db
from database import get_total_users
from database import (
    get_total_users,
    get_total_expenses_count,
    get_total_tasks_count,
    get_premium_users_count
)


from database import  (get_month_expenses_db)


from dotenv import load_dotenv
import os
import asyncio
import json
from database import init_db, add_expense_db, get_expenses_db

from database import (
    init_db,
    add_expense_db,
    get_expenses_db,
    delete_expense_db,
    set_budget_db,
    get_budget_db,
    get_month_expenses_db,
    set_currency_db,
    get_currency_db,
    set_goal_db,
    get_goal_db,
    add_subscription_db,
    get_subscriptions_db
)
from database import add_task_db, get_tasks_db, complete_task_db

load_dotenv(dotenv_path=".env")
init_db()

BOT_TOKEN = os.getenv("BOT_TOKEN")


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

@dp.message(Command("admin"))
async def admin_stats(message: Message):

    if message.from_user.id != 1128720977:
        return

    users = get_total_users()
    expenses = get_total_expenses_count()
    tasks = get_total_tasks_count()
    premium = get_premium_users_count()

    text = (
        f"👥 Users: {users}\n"
        f"💰 Expenses added: {expenses}\n"
        f"✅ Tasks created: {tasks}\n"
        f"⭐ Premium users: {premium}"
    )

    await message.answer(text)

@dp.message(Command("users"))
async def users_count(message: Message):

    if message.from_user.id != 1128720977:
        return

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]

    conn.close()

    await message.answer(f"👥 Users: {count}")

@dp.message(Command("clear_expenses"))
async def clear_expenses(message: Message):

    user_id = message.from_user.id

    clear_expenses_db(user_id)

    await message.answer("🗑 Всі витрати очищені")

@dp.message(F.text == "+ Add Expense")
async def expense_menu(message: Message):
    await message.answer(
        "💸 Add expense:\n\n"
        "Example:\n"
        "/add Food 300\n"
        "/add Taxi 25\n"
        "/add Coffee 10"
    )

@dp.message(Command("premium_users"))
async def premium_users_command(message: Message):

    total = get_premium_users_count()

    await message.answer(
        f"💎 Premium users: {total}"
    )


@dp.message(F.text == "✅ Tasks")
async def tasks_menu(message: Message):
    await message.answer(
        "✅ VTask commands:\n\n"
        "/task Buy milk\n"
        "/tasks\n"
        "/done 1\n"
        "/delete_task 1"

    )
    return

@dp.message(Command("task"))
async def add_task(message: Message):

    user_id = message.from_user.id

    text = message.text.replace("/task ", "")

    add_task_db(user_id, text)

    await message.answer(
        f"✅ Задачу додано:\n\n{text}"
    )

@dp.message(F.text == "✅ Tasks")
async def tasks_button(message: Message):

    await message.answer(
        "📝 Tasks menu:\n\n"
        "/task Buy milk\n"
        "/tasks\n"
        "/done 1"
    )

@dp.message(F.text == "📊 Analytics")
async def analytics_help(message: Message):

    await message.answer(
        "📊 Analytics:\n\n"
        "/stats\n"
        "/chart\n"
        "/month"
    )

@dp.message(F.text == "➕ Add Expense")
async def add_expense_help(message: Message):

    await message.answer(
        "💸 Send expense like:\n\n"
        "/add food 300"
    )

@dp.message(Command("deletetask"))
async def delete_task_command(message: Message):

    text = message.text.split()

    task_id = int(text[1])

    user_id = message.from_user.id

    delete_task_db(user_id, task_id)

    await message.answer("🗑 Task deleted!")



@dp.message(Command("tasks"))
async def show_tasks(message: Message):

    user_id = message.from_user.id

    tasks = get_tasks_db(user_id)

    if not tasks:

        await message.answer("📭 Немає задач")
        return

    text = "📝 Твої задачі:\n\n"

    for index, task in enumerate(tasks, start=1):
        status = "✅" if task[3] == 1 else "⬜"

        text += f"{status} #{task[0]} {task[2]}\n"

    await message.answer(text)

@dp.message(Command("done"))
async def complete_task(message: Message):

    user_id = message.from_user.id

    text = message.text.split()

    task_id = int(text[1])

    complete_task_db(user_id, task_id)

    await message.answer("✅ Задачу виконано")


@dp.message(Command("help"))
async def help_command(message: Message):

    text = (
        "🤖 Команди бота:\n\n"

        "💸 Витрати:\n"
        "/add food 300\n"
        "/expenses\n"
        "/delete_task TASK_ID\n"
        "/clear_expenses\n"

        "📊 Аналітика:\n"
        "/stats\n"
        "/chart\n"
        "/insights\n"
        "/warnings\n"
        "/month\n\n"

        "💰 Бюджет:\n"
        "/budget 5000\n"
        "/budget_status\n\n"

        "🎯 Цілі:\n"
        "/goal 10000 MacBook\n"
        "/goal_status\n\n"

        "📺 Підписки:\n"
        "/subscribe Netflix 40\n"
        "/subscriptions\n\n"

        "🌍 Валюта:\n"
        "/currency USD\n"
        "/currency PLN\n"
        "/currency UAH\n\n"

        "✅ VTask:\n"
        "/task Go to the gym\n"
        "/tasks\n"
        "/done 1\n"

    )
    await message.answer(text)

@dp.message(Command("delete_task"))
async def delete_task(message: Message):
        user_id = message.from_user.id

        text = message.text.split()

        if len(text) < 2:
            await message.answer("❌ Use: /delete_task ID")
            return

        task_id = int(text[1])

        delete_task_db(user_id, task_id)

        await message.answer("🗑 Task deleted")




@dp.message(Command("subscribe"))
async def subscribe_command(message: Message):

    user_id = message.from_user.id

    text = message.text.split()

    name = text[1]
    amount = int(text[2])

    add_subscription_db(user_id, name, amount)

    currency = get_currency_db(user_id)

    await message.answer(
        f"📺 Підписка додана!\n\n"
        f"{name} — {amount} {currency}/month"
    )


@dp.message(Command("subscriptions"))
async def show_subscriptions(message: Message):

    user_id = message.from_user.id

    subscriptions = get_subscriptions_db(user_id)

    currency = get_currency_db(user_id)

    text = "📺 Твої підписки:\n\n"

    total = 0

    for sub in subscriptions:

        text += f"{sub[2]} — {sub[3]} {currency}/month\n"

        total += sub[3]

    text += f"\n💰 Разом: {total} {currency}/month"

    await message.answer(text)

@dp.message(Command("delete_goal"))
async def delete_goal(message: Message):

    user_id = message.from_user.id

    delete_goal_db(user_id)

    await message.answer("🎯 Goal deleted")

@dp.message(Command("goal"))
async def goal_handler(message: Message):

    try:

        user_id = message.from_user.id

        text = message.text.split()

        goal_amount = int(text[1])

        goal_name = " ".join(text[2:])

        set_goal_db(
            user_id,
            goal_name,
            goal_amount
        )

        currency = get_currency_db(user_id)

        await message.answer(
            f"🎯 Ціль створена!\n\n"
            f"{goal_name} — "
            f"{goal_amount} {currency}"
        )

    except:

        await message.answer(
            "❌ Формат:\n/goal 5000 MacBook"
        )

@dp.message(Command("goal_status"))
async def goal_status_handler(message: Message):

    user_id = message.from_user.id

    goal = get_goal_db(user_id)

    if not goal:

        await message.answer(
            "❌ Ціль не встановлена"
        )

        return

    goal_name = goal[0]
    goal_amount = goal[1]

    expenses = get_expenses_db(user_id)

    total_spent = sum(expense[3] for expense in expenses)

    saved = max(goal_amount - total_spent, 0)

    progress = (
        (saved / goal_amount) * 100
    )

    currency = get_currency_db(user_id)

    text = (
        f"🎯 {goal_name}\n\n"
        f"💰 Ціль: {goal_amount} {currency}\n"
        f"💵 Потенційно збережено: {saved} {currency}\n"
        f"📈 Прогрес: {progress:.1f}%"
    )

    await message.answer(text)

@dp.message(Command("currency"))
async def currency_handler(message: Message):

    user_id = message.from_user.id

    text = message.text.split()

    if len(text) != 2:

        await message.answer(
            "❌ Формат:\n/currency USD"
        )

        return

    currency = text[1].upper()

    allowed = ["USD", "EUR", "PLN", "UAH"]

    if currency not in allowed:

        await message.answer(
            "❌ Доступно:\nUSD EUR PLN UAH"
        )

        return

    set_currency_db(user_id, currency)

    await message.answer(
        f"💰 Валюта змінена на {currency}"
    )

@dp.message(Command("insights"))
async def insights_handler(message: Message):

    user_id = message.from_user.id

    if not is_premium(user_id):
        await message.answer(
            "👑 Premium feature\n\n"
            "Trial закінчився.\n"
            "Підписка: 5$/month"
        )

        return

    expenses = get_expenses_db(user_id)

    if not expenses:
        await message.answer("Немає витрат 😄")
        return

    stats = {}

    total = 0

    for expense in expenses:

        category = expense[2]
        amount = expense[3]

        total += amount

        if category in stats:
            stats[category] += amount
        else:
            stats[category] = amount

    top_category = max(stats, key=stats.get)

    top_amount = stats[top_category]

    percent = round((top_amount / total) * 100)

    text = (
        f"📊 AI Аналіз:\n\n"
        f"🔥 Найбільше витрат: {top_category} — {top_amount}$\n\n"
        f"⚠️ {top_category} займає {percent}% всіх витрат\n\n"
    )

    if percent > 50:
        text += (
            f"💡 Спробуй зменшити витрати на "
            f"{top_category}"
        )

    else:
        text += "✅ Баланс витрат виглядає добре"

    await message.answer(text)

@dp.message(F.text == "📄 Report")
async def report_button(message: Message):

    await report_handler(message)

def detect_category(text):

    text = text.lower()

    categories = {

        "food": [
            "mcdonalds",
            "burger",
            "pizza",
            "kfc",
            "restaurant",
            "cafe",
            "coffee",
            "food"
        ],

        "transport": [
            "uber",
            "taxi",
            "bolt",
            "bus",
            "train",
            "fuel"
        ],

        "entertainment": [
            "netflix",
            "spotify",
            "cinema",
            "movie",
            "game"
        ],

        "shopping": [
            "nike",
            "zara",
            "amazon",
            "clothes",
            "shopping"
        ],

        "health": [
            "doctor",
            "medicine",
            "gym",
            "health"
        ],

        "work": [
            "hosting",
            "server",
            "domain",
            "aws",
            "openai"
        ]
    }

    for category, keywords in categories.items():

        if any(word in text for word in keywords):
            return category

    return "other"

@dp.message(Command("chart"))
async def chart_handler(message: Message):

    user_id = message.from_user.id

    expenses = get_expenses_db(user_id)

    stats = {}

    for expense in expenses:

        category = expense[2]
        amount = expense[3]

        if category in stats:
            stats[category] += amount
        else:
            stats[category] = amount

    labels = list(stats.keys())
    sizes = list(stats.values())

    plt.figure(figsize=(6, 6))

    plt.pie(
        sizes,
        labels=labels,
        autopct='%1.1f%%'
    )

    plt.title("Expense Statistics")

    plt.savefig("chart.png")

    plt.close()

    photo = FSInputFile("chart.png")

    await message.answer_photo(photo)



@dp.message(Command("warnings"))
async def warnings_handler(message: Message):

    user_id = message.from_user.id

    expenses = get_expenses_db(user_id)

    if not expenses:
        await message.answer("❌ У тебе немає витрат")
        return

    stats = {}

    total = 0

    for expense in expenses:

        category = expense[2]
        amount = expense[3]

        total += amount

        if category in stats:
            stats[category] += amount
        else:
            stats[category] = amount

    text = "🤖 AI Аналіз витрат:\n\n"

    for category, amount in stats.items():

        percent = (amount / total) * 100

        if percent >= 50:

            text += (
                f"⚠️ У тебе дуже великі витрати "
                f"на {category} ({percent:.1f}%)\n"
            )

    if total > 1000:

        text += "\n🔥 Ти витрачаєш дуже багато грошей"

    elif total < 200:

        text += "\n✅ У тебе хороший контроль витрат"

    await message.answer(text)

@dp.message(Command("report"))
async def report_handler(message: Message):

    user_id = message.from_user.id

    expenses = get_expenses_db(user_id)

    current_date = datetime.now().strftime("%Y-%m-%d")

    pdf_name = f"reports/report_{user_id}_{current_date}.pdf"

    pdf = canvas.Canvas(pdf_name)

    # TITLE
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawString(180, 800, "TaskForge AI")

    pdf.setFont("Helvetica", 16)
    pdf.drawString(200, 770, "Finance Report")

    # USER INFO
    pdf.setFont("Helvetica", 12)

    pdf.drawString(
        50,
        730,
        f"User ID: {user_id}"
    )

    pdf.drawString(
        50,
        710,
        f"Date: {current_date}"
    )

    # LINE
    pdf.line(50, 690, 550, 690)

    # EXPENSES TITLE
    pdf.setFont("Helvetica-Bold", 16)

    pdf.drawString(
        50,
        660,
        "Expenses"
    )

    y = 630

    total = 0

    pdf.setFont("Helvetica", 12)

    if not expenses:

        pdf.drawString(
            50,
            y,
            "No expenses yet"
        )

    else:

        for expense in expenses:

            category = expense[2]
            amount = expense[3]

            total += amount

            pdf.drawString(
                70,
                y,
                f"• {category} — ${amount}"
            )

            y -= 25

        # TOTAL
        pdf.line(50, y, 550, y)

        y -= 30

        pdf.setFont("Helvetica-Bold", 16)

        pdf.drawString(
            50,
            y,
            f"Total: ${total}"
        )

    # FOOTER
    pdf.setFont("Helvetica-Oblique", 10)

    pdf.drawString(
        180,
        50,
        "Generated by TaskForge AI"
    )

    pdf.save()

    await message.answer_document(
        document=FSInputFile(pdf_name),
        caption="📄 Your finance report is ready"
    )


@dp.message(Command("stats"))
async def show_stats(message: Message):

    user_id = message.from_user.id

    expenses = get_expenses_db(user_id)

    if not expenses:
        await message.answer(
            "📭 У тебе ще немає витрат"
        )
        return

    stats = {}

    for expense in expenses:

        category = expense[2]
        amount = expense[3]

        if category in stats:
            stats[category] += amount
        else:
            stats[category] = amount

    currency = get_currency_db(user_id)

    text = "📊 Статистика:\n\n"

    total = 0

    for category, amount in stats.items():

        total += amount

        text += (
            f"{category} — "
            f"{amount} {currency}\n"
        )

    text += (
        f"\n💰 Загалом: "
        f"{total} {currency}"
    )

    await message.answer(text)


@dp.message(Command("recommend"))
async def recommend_handler(message: Message):

    user_id = message.from_user.id

    expenses = get_expenses_db(user_id)

    if not expenses:
        await message.answer("❌ Немає витрат")
        return

    stats = {}
    total = 0

    for expense in expenses:

        category = expense[2]
        amount = expense[3]

        total += amount

        if category in stats:
            stats[category] += amount
        else:
            stats[category] = amount

    biggest_category = max(stats, key=stats.get)
    biggest_amount = stats[biggest_category]

    percent = (biggest_amount / total) * 100

    save_money = biggest_amount * 0.2

    text = (
        f"🤖 AI Recommendations\n\n"
        f"🔥 Найбільше витрат йде на: {biggest_category}\n"
        f"💸 Це {percent:.1f}% всіх витрат\n\n"
        f"💡 Якщо зменшити витрати на "
        f"{biggest_category} на 20%,\n"
        f"ти зекономиш приблизно "
        f"{save_money:.0f}$"
    )

    await message.answer(text)

    await report_handler(message)

    user_id = message.from_user.id

    expenses = get_expenses_db(user_id)

    if not expenses:
        await message.answer("❌ Немає витрат")
        return

    pdf_name = f"report_{user_id}.pdf"

    pdf = canvas.Canvas(pdf_name)

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(200, 800, "Finance Report")

    pdf.setFont("Helvetica", 12)

    y = 760

    total = 0

    for expense in expenses:

        category = expense[2]
        amount = expense[3]

        total += amount

        pdf.drawString(
            100,
            y,
            f"{category} - {amount}$"
        )

        y -= 25

    pdf.setFont("Helvetica-Bold", 14)

    pdf.drawString(
        100,
        y - 20,
        f"Total: {total}$"
    )

    pdf.save()

    await message.answer_document(
        document=FSInputFile(pdf_name),
        caption="📄 Твій фінансовий звіт"
    )

@dp.message(Command("month"))
async def month_stats(message: Message):

    user_id = message.from_user.id

    current_month = datetime.now().strftime("%Y-%m")

    expenses = get_month_expenses_db(user_id, current_month)

    stats = {}

    total = 0

    for expense in expenses:

        category = expense[2]
        amount = expense[3]

        total += amount

        if category in stats:
            stats[category] += amount
        else:
            stats[category] = amount

    text = "📅 Витрати за місяць:\n\n"

    for category, amount in stats.items():
        text += f"{category} — {amount}$\n"

    text += f"\n💰 Загалом: {total}$"

    await message.answer(text)


@dp.message(Command("start"))
async def start_handler(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    save_user(user_id, username, first_name)

    premium_user = get_premium_user(user_id)

    if not premium_user:
        trial_end = (
                datetime.now() + timedelta(days=7)
        ).strftime("%Y-%m-%d")

        add_premium_user(
            user_id,
            1,
            trial_end
        )

        await message.answer(
            "🎁 Тобі активовано 7-денний Premium Trial!"
        )

    await message.answer(
        "🚀 Welcome to TaskForge AI\n\n"
        "Track:\n"
        "• expenses\n"
        "• tasks\n"
        "• goals\n"
        "• subscriptions\n"
        "• budgets\n\n"
        "👇 Use the menu below\n"
        "or type /help",
        reply_markup=get_main_keyboard("en")
    )


@dp.message(Command("add"))
async def add_expense(message: Message):

    try:

        user_id = message.from_user.id

        text = message.text.split()

        if len(text) == 2:

            category = "other"
            amount = int(text[1])

        else:

            category = detect_category(text[1])

            amount = int(text[2])

        add_expense_db(
            user_id,
            category,
            amount
        )

        currency = get_currency_db(user_id)

        await message.answer(
            f"✅ Додано!\n\n"
            f"Категорія: {category}\n"
            f"Сума: {amount} {currency}"
        )

    except ValueError:

        await message.answer(
            "❌ Сума має бути числом"
        )

    except:

        await message.answer(
            "❌ Формат:\n/add uber 25"
        )


@dp.message(F.text == "📊 Analytics")
async def analytics_button(message: Message):

    await message.answer(
        "/stats\n/chart\n/insights\n/warnings\n/month"
    )

@dp.message(F.text == "🎯 Goals")
async def goals_button(message: Message):

    await message.answer(
        "/goal 10000 MacBook\n/goal_status"
    )

@dp.message(F.text == "💳 Subscriptions")
async def subscriptions_button(message: Message):

    await message.answer(
        "/subscribe netflix 40\n/subscriptions"
    )

@dp.message(F.text == "💰 Budget")
async def budget_button(message: Message):

    await message.answer(
        "/budget 5000\n/budget_status"
    )

@dp.message(F.text == "⚙️ Settings")
async def settings_button(message: Message):

    await message.answer(
        "/currency USD"
    )

@dp.message(Command("expenses"))
async def show_expenses(message: Message):

    user_id = message.from_user.id

    expenses = get_expenses_db(user_id)

    if not expenses:
        await message.answer("📭 Немає витрат")
        return

    text = "💸 Твої витрати:\n\n"

    for index, expense in enumerate(expenses, start=1):

        text += (
            f"#{index} | "
            f"{expense[2]} - "
            f"{expense[3]}\n"
        )

    await message.answer(text)



@dp.message(Command("total"))
async def total_expenses(message: Message):

    expenses = get_expenses_db()

    total = sum(expense[2] for expense in expenses)

    await message.answer(
        f"💰 Загальні витрати: {total}$"
    )

@dp.message(Command("budget"))
async def set_budget(message: Message):

        try:

            user_id = message.from_user.id

            text = message.text.split()

            amount = int(text[1])

            set_budget_db(user_id, amount)

            await message.answer(
                f"💰 Бюджет встановлено: {amount}$"
            )

        except:

            await message.answer(
                "❌ Формат:\n/budget 2000"
            )
@dp.message(Command("budget_status"))
async def budget_status(message: Message):

            user_id = message.from_user.id

            budget = get_budget_db(user_id)

            if budget is None:
                await message.answer(
                    "❌ Бюджет не встановлено"
                )

                return

            expenses = get_expenses_db(user_id)

            total_spent = sum(expense[3] for expense in expenses)

            left = budget - total_spent

            text = (
                f"💰 Бюджет: {budget}$\n\n"
                f"📉 Витрачено: {total_spent}$\n\n"
                f"💵 Залишилось: {left}$"
            )

            await message.answer(text)

@dp.message(F.text == "🌍 Language")
async def language_button(message: Message):

    await message.answer(
        "Choose language:\n\n"
        "/english\n"
        "/ukrainian"
    )


@dp.message(Command("english"))
async def english_lang(message: Message):

    await message.answer(
        "🇬🇧 English enabled",
        reply_markup=get_main_keyboard("en")
    )


@dp.message(Command("ukrainian"))
async def ukrainian_lang(message: Message):

    await message.answer(
        "🇺🇦 Українська увімкнена",
        reply_markup=get_main_keyboard("ua")
    )


@dp.message(Command("delete"))
async def delete_expense(message: Message):

    try:
        text = message.text.split()

        delete_index = int(text[1])

        user_id = message.from_user.id

        expenses = get_expenses_db(user_id)

        if delete_index < 1 or delete_index > len(expenses):

            await message.answer("❌ Wrong expense number")
            return

        real_id = expenses[delete_index - 1][0]

        delete_expense_db(user_id, real_id)

        await message.answer(
            f"❌ Видалено витрату #{delete_index}"
        )

    except:
        await message.answer(
            "❌ Формат: /delete 1"
        )

@dp.message()
async def message_handler(message: Message):
    await message.answer(
        "Я не зрозумів команду 😄"
    )

async def send_daily_reminder():

    conn = sqlite3.connect("expenses.db")

    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT user_id FROM expenses")

    users = cursor.fetchall()

    conn.close()

    for user in users:

        user_id = user[0]

        try:
            await bot.send_message(
                user_id,
                "💸 Не забудь записати сьогоднішні витрати"
            )

        except:
            pass

async def main():
    scheduler.add_job(
        send_daily_reminder,
        "cron",
        hour="12,20",
        minute=0
    )

    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


@dp.message(Command("givepremium"))
async def give_premium_command(message: Message):

    admin_id = YOUR_ID

    if message.from_user.id != admin_id:
        return

    text = message.text.split()

    user_id = int(text[1])

    give_premium(user_id)

    await message.answer("✅ Premium видано")
