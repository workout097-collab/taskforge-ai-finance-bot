from datetime import datetime, timedelta
from main_keyboard import get_main_keyboard
import sqlite3
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
import matplotlib.pyplot as plt
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from reportlab.pdfgen import canvas
from aiogram.types import FSInputFile
from translations import translations
from database import (
    get_total_users,
    get_total_expenses_count,
    get_total_tasks_count,
    get_premium_users_count
)
from database import (
    clear_expenses_db,
    delete_goal_db,
    delete_task_db,
    give_premium,
    save_user,
    get_premium_user,
    add_premium_user
)

from database import  (get_month_expenses_db)

from database import (
    set_language_db,
    get_language_db
)
from dotenv import load_dotenv
import os
import asyncio
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

@dp.message(Command("english"))
async def english_lang(message: Message):

    user_id = message.from_user.id

    set_language_db(user_id, "en")

    await message.answer(
        "🇬🇧 English enabled",
        reply_markup=get_main_keyboard(language)
    )

@dp.message(Command("ukrainian"))
async def ukrainian_lang(message: Message):

    user_id = message.from_user.id

    set_language_db(user_id, "ua")

    await message.answer(
        "🇺🇦 Українська увімкнена",
        reply_markup=get_main_keyboard("ua")
    )




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

    language = get_language_db(user_id)
    t = translations[language]

    clear_expenses_db(user_id)

    await message.answer(t["expenses_cleared"])

@dp.message(F.text == "+ Add Expense")
async def expense_menu(message: Message):
    user_id = message.from_user.id

    language = get_language_db(user_id)
    t = translations[language]

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
async def tasks_button(message: Message):

    user_id = message.from_user.id

    language = get_language_db(user_id)
    t = translations[language]

    await message.answer(
        "📝 Tasks menu:\n\n"
        "/task Buy milk\n"
        "/tasks\n"
        "/done 1"
    )

@dp.message(Command("task"))
async def add_task(message: Message):
    user_id = message.from_user.id

    language = get_language_db(user_id)
    t = translations[language]

    text = message.text.replace("/task ", "")

    add_task_db(user_id, text)

    await message.answer(
        f"{t['task_added']}\n\n{text}"
    )

@dp.message(F.text == "➕ Add Expense")
async def add_expense_help(message: Message):
    user_id = message.from_user.id
    language = get_language_db(user_id)
    t = translations[language]

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

    language = get_language_db(user_id)
    t = translations[language]

    tasks = get_tasks_db(user_id)

    if not tasks:
        await message.answer(t["no_tasks"])
        return

    text = f"{t['tasks']}\n\n"

    for index, task in enumerate(tasks, start=1):

        status = "✅" if task[3] == 1 else "⬜"

        text += f"{status} #{task[0]} {task[2]}\n"

    await message.answer(text)

@dp.message(Command("done"))
async def complete_task(message: Message):
    user_id = message.from_user.id

    language = get_language_db(user_id)
    t = translations[language]

    text = message.text.split()

    task_id = int(text[1])

    complete_task_db(user_id, task_id)

    await message.answer(t["task_completed"])


@dp.message(Command("help"))
async def help_command(message: Message):
    user_id = message.from_user.id

    language = get_language_db(user_id)
    t = translations[language]
    text = (
        f"{t['bot_commands']}\n\n"

        f"{t['expenses_section']}\n"
        "/add food 300\n"
        "/expenses\n"
        "/delete_task TASK_ID\n"
        "/clear_expenses\n"

        f"\n{t['analytics']}\n"
        "/stats\n"
        "/chart\n"
        "/insights\n"
        "/warnings\n"
        "/month\n\n"

        f"{t['budget_section']}\n"
        "/budget 5000\n"
        "/budget_status\n\n"

        f"{t['goals_section']}\n"
        "/goal 10000 MacBook\n"
        "/goal_status\n\n"

        f"{t['subscriptions_section']}\n"
        "/subscribe Netflix 40\n"
        "/subscriptions\n\n"

        f"{t['currency_section']}\n"
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

        language = get_language_db(user_id)
        t = translations[language]

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

    language = get_language_db(user_id)
    t = translations[language]

    text = message.text.split()

    name = text[1]
    amount = int(text[2])

    add_subscription_db(user_id, name, amount)

    currency = get_currency_db(user_id)

    await message.answer(
        f"{t['subscription_added']}\n\n"
        f"{name} — {amount} {currency}/month"
    )


@dp.message(Command("subscriptions"))
async def show_subscriptions(message: Message):
    user_id = message.from_user.id

    language = get_language_db(user_id)
    t = translations[language]

    subscriptions = get_subscriptions_db(user_id)

    currency = get_currency_db(user_id)

    text = f"{t['subscriptions']}\n\n"

    total = 0

    for sub in subscriptions:

        text += f"{sub[2]} — {sub[3]} {currency}/month\n"

        total += sub[3]

    text += f"\n{t['total']}: {total} {currency}/month"

    await message.answer(text)

@dp.message(Command("delete_goal"))
async def delete_goal(message: Message):
    user_id = message.from_user.id

    language = get_language_db(user_id)
    t = translations[language]

    delete_goal_db(user_id)

    await message.answer("🎯 Goal deleted")

@dp.message(Command("goal"))
async def goal_handler(message: Message):


    try:

        user_id = message.from_user.id

        language = get_language_db(user_id)
        t = translations[language]

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
            f"{t['goal_created']}\n\n"
            f"{goal_name} — "
            f"{goal_amount} {currency}"
        )

    except:

        await message.answer(
            t["goal_format"]
        )

@dp.message(Command("goal_status"))
async def goal_status_handler(message: Message):

    user_id = message.from_user.id

    language = get_language_db(user_id)
    t = translations[language]

    goal = get_goal_db(user_id)

    if not goal:
        await message.answer(
            t["goal_not_set"]
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
        f"{t['goal_status']}\n\n"
        f"🎯 {goal_name}\n"
        f"💰 Goal: {goal_amount} {currency}\n"
        f"💵 Saved: {saved} {currency}\n"
        f"📈 Progress: {progress:.1f}%"
    )

    await message.answer(text)

@dp.message(Command("currency"))
async def currency_handler(message: Message):

    user_id = message.from_user.id

    language = get_language_db(user_id)
    t = translations[language]

    text = message.text.split()

    if len(text) != 2:
        await message.answer(
            t["currency_format"]
        )

        return

    currency = text[1].upper()

    allowed = ["USD", "EUR", "PLN", "UAH"]

    if currency not in allowed:
        await message.answer(
            t["currency_available"]
        )

        return

    set_currency_db(user_id, currency)

    await message.answer(
        f"{t['currency_changed']} {currency}"
    )

@dp.message(Command("insights"))
async def insights_handler(message: Message):

    user_id = message.from_user.id

    language = get_language_db(user_id)
    t = translations[language]

    await message.answer(
        t["premium_required"]
    )

    expenses = get_expenses_db(user_id)

    if not expenses:
        await message.answer(
            t["no_expenses"]
        )

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
    f"{t['ai_analysis']}\n\n"
    f"{t['top_expense']} {top_category} — {top_amount}$\n\n"
    f"⚠️ {top_category} {t['expense_percent']} {percent}%\n\n"
    )

    if percent > 50:
            text += (
                f"{t['reduce_expenses']} "
                f"{top_category}"
            )

    else:
         text += t["good_balance"]

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

    language = get_language_db(user_id)
    t = translations[language]

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

    language = get_language_db(user_id)
    t = translations[language]

    expenses = get_expenses_db(user_id)

    if not expenses:
        await message.answer(t["no_expenses"])
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

    text = f"{t['warnings_title']}\n\n"

    for category, amount in stats.items():

        percent = (amount / total) * 100

        if percent >= 50:

            text += (
                f"{t['big_expenses']} "
                f"{category} ({percent:.1f}%)\n"
            )

    if total > 1000:

        text += f"\n{t['too_much_spending']}"

    elif total < 200:

        text += f"\n{t['good_control']}"

    await message.answer(text)

@dp.message(Command("report"))
async def report_handler(message: Message):
    user_id = message.from_user.id

    language = get_language_db(user_id)
    t = translations[language]

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

    language = get_language_db(user_id)
    t = translations[language]

    expenses = get_expenses_db(user_id)

    if not expenses:
        await message.answer(t["no_expenses"])
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

    text = f"{t['statistics']}\n\n"

    total = 0

    for category, amount in stats.items():

        total += amount

        print(category)
        print(type(category))

        translated_category = t["categories"].get(category, category)

        text += f"{translated_category} — {amount}$\n"

    text += (
        f"\n{t['total']}: "
        f"{total} {currency}"
    )

    await message.answer(text)


@dp.message(Command("recommend"))
async def recommend_handler(message: Message):

    user_id = message.from_user.id

    language = get_language_db(user_id)
    t = translations[language]

    expenses = get_expenses_db(user_id)

    if not expenses:
        await message.answer(t["no_expenses"])
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
        f"{t['recommendations_title']}\n\n"
        f"{t['biggest_expense']}{biggest_category}\n"
        f"{t['expense_percent']} {percent:.1f}%\n\n"
        f"{t['reduce_expenses']} "
        f"{biggest_category} 20%,\n"
        f"{t['save_money']} {save_money}$"
    )

    await message.answer(text)

    await report_handler(message)

    user_id = message.from_user.id

    expenses = get_expenses_db(user_id)

    if not expenses:
        await message.answer(t["no_expenses"])
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
        caption=t["financial_report_caption"]
    )

@dp.message(Command("month"))
async def month_stats(message: Message):

    user_id = message.from_user.id

    language = get_language_db(user_id)
    t = translations[language]

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

    text = f"{t['month_stats']}\n\n"

    currency = get_currency_db(user_id)

    for category, amount in stats.items():
        translated_category = t["categories"].get(category, category)

        text += f"{translated_category} - {amount}{currency}\n"

        currency = get_currency_db(user_id)

    text += f"\n💰 {t['total']}: {total}{currency}"

    await message.answer(text)


@dp.message(Command("start"))
async def start_handler(message: Message):
    user_id = message.from_user.id

    language = get_language_db(user_id)
    t = translations[language]

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

        language = get_language_db(user_id)
        t = translations[language]

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

        language = get_language_db(user_id)

        t = translations[language]

        await message.answer(
            f"{t['added']}\n\n"
            f"{t['category']}: {category}\n"
            f"{t['amount']}: {amount} {currency}"
        )

    except ValueError:

        await message.answer(
            t["amount_must_be_number"]
        )

    except:

        await message.answer(
            t["add_format"]
        )


@dp.message(F.text == "📊 Analytics")
async def analytics_button(message: Message):
    user_id = message.from_user.id

    language = get_language_db(user_id)
    t = translations[language]

    await message.answer(
        "/stats\n/chart\n/insights\n/warnings\n/month"
    )

@dp.message(F.text == "🎯 Goals")
async def goals_button(message: Message):
    user_id = message.from_user.id

    language = get_language_db(user_id)
    t = translations[language]

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
@dp.message(F.text == "💱 Currency")
async def currency_button(message: Message):

    await message.answer(
        "Choose currency:\n\n"
        "/currency USD\n"
        "/currency UAH\n"
        "/currency PLN"
    )

@dp.message(Command("expenses"))
async def show_expenses(message: Message):

    user_id = message.from_user.id

    language = get_language_db(user_id)
    t = translations[language]

    expenses = get_expenses_db(user_id)

    currency = get_currency_db(user_id)
    if not expenses:
        await message.answer(t["no_expenses"])
        return

    text = f"{t['your_expenses']}\n\n"

    for index, expense in enumerate(expenses, start=1):

        translated_category = t["categories"].get(
            expense[2],
            expense[2]
        )
        text += (
            f"#{index} | "
            f"{translated_category} - "
            f"{expense[3]} {currency}\n"
        )

    await message.answer(text)



@dp.message(Command("total"))
async def total_expenses(message: Message):
    user_id = message.from_user.id

    language = get_language_db(user_id)
    t = translations[language]
    expenses = get_expenses_db(user_id)

    total = sum(expense[3] for expense in expenses)
    currency = get_currency_db(user_id)

    await message.answer(

        f"💰 {t['total_expenses']}: {total}{currency}"
    )

@dp.message(Command("budget"))
async def set_budget(message: Message):

        try:

            user_id = message.from_user.id

            language = get_language_db(user_id)
            t = translations[language]

            text = message.text.split()

            amount = int(text[1])

            set_budget_db(user_id, amount)

            currency = get_currency_db(user_id)

            await message.answer(
                f"💰 {t['budget_set']}: {amount}{currency}"
            )

        except:

            await message.answer(
                t["budget_format"]
            )
@dp.message(Command("budget_status"))
async def budget_status(message: Message):

            user_id = message.from_user.id

            language = get_language_db(user_id)
            t = translations[language]

            budget = get_budget_db(user_id)

            if budget is None:
                await message.answer(
                    t["budget_not_set"]
                )

                return

            expenses = get_expenses_db(user_id)

            total_spent = sum(expense[3] for expense in expenses)

            left = budget - total_spent

            currency = get_currency_db(user_id)

            text = (
                f"💰 {t['budget']}: {budget}{currency}\n\n"
                f"🧾 {t['spent']}: {total_spent}{currency}\n\n"
                f"💵 {t['left']}: {left}{currency}"

            )

            await message.answer(text)

@dp.message(F.text == "🌍 Language")
async def language_button(message: Message):

    await message.answer(
        "Choose language:\n\n"
        "/english\n"
        "/ukrainian"
    )

@dp.message(Command("delete"))
async def delete_expense(message: Message):

    try:


        text = message.text.split()

        delete_index = int(text[1])

        user_id = message.from_user.id

        language = get_language_db(user_id)
        t = translations[language]

        expenses = get_expenses_db(user_id)

        if delete_index < 1 or delete_index > len(expenses):

            await message.answer("❌ Wrong expense number")
            return

        real_id = expenses[delete_index - 1][0]

        delete_expense_db(user_id, real_id)

        await message.answer(
                f"{t['expense_deleted']} #{delete_index}"
            )


    except:
        await message.answer(
            t["delete_format"]
    )


@dp.message()
async def message_handler(message: Message):

    user_id = message.from_user.id

    language = get_language_db(user_id)
    t = translations[language]

    await message.answer(
        t["unknown_command"]
        )

async def send_daily_reminder():

    conn = sqlite3.connect("expenses.db")

    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT user_id FROM expenses")

    users = cursor.fetchall()

    conn.close()

    for user in users:

        user_id = user[0]

        language = get_language_db(user_id)
        t = translations[language]

        try:
            await bot.send_message(
                user_id,
                t["daily_reminder"]
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
    user_id = message.from_user.id
    language = get_language_db(user_id)
    t = translations[language]

    admin_id = 1128720977

    if message.from_user.id != admin_id:
        return

    text = message.text.split()

    user_id = int(text[1])

    give_premium(user_id)

    await message.answer(
        t["premium_given"]
    )
