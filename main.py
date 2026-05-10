import sqlite3
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from keyboards.main_keyboard import main_keyboard
from aiogram.filters import Command
import matplotlib.pyplot as plt
from aiogram.types import FSInputFile
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from reportlab.pdfgen import canvas
from aiogram.types import FSInputFile



from database import (get_month_expenses_db)
from datetime import datetime

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


load_dotenv(dotenv_path=".env")
init_db()

BOT_TOKEN = os.getenv("BOT_TOKEN")


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()


@dp.message(Command("help"))
async def help_command(message: Message):

    text = (
        "🤖 Команди бота:\n\n"

        "💸 Витрати:\n"
        "/add food 300\n"
        "/expenses\n"
        "/delete 1\n\n"

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
    )

    await message.answer(text)

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

def detect_category(text):

    text = text.lower()

    food_keywords = [
        "mcdonalds",
        "burger",
        "pizza",
        "food",
        "kfc",
        "restaurant",
        "cafe"
    ]

    taxi_keywords = [
        "uber",
        "taxi",
        "bolt"
    ]

    if any(word in text for word in food_keywords):
        return "food"

    if any(word in text for word in taxi_keywords):
        return "taxi"

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


@dp.message(Command("report"))
async def report_handler(message: Message):

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
    await message.answer(
        "Привіт 👋 Я твій AI Finance Bot",
        reply_markup=main_keyboard
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

                if text[1].lower() in [
                    "mcdonalds",
                    "pizza",
                    "burger",
                    "kfc"
                ]:
                    category = "food"

                elif text[1].lower() in [
                    "uber",
                    "taxi",
                    "bolt"
                ]:
                    category = "taxi"

                elif text[1].lower() in [
                    "netflix",
                    "spotify"
                ]:
                    category = "subscriptions"

                else:
                    category = "other"
                amount = int(text[2])

            add_expense_db(user_id, category, amount)

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


@dp.message(Command("expenses"))
async def get_expenses(message: Message):

    user_id = message.from_user.id

    currency = get_currency_db(user_id)

    total = sum(expense[3] for expense in expenses)

    text = "💸 Твої витрати:\n\n"

    for expense in expenses:

        text += (
            f"{expense[0]}. "
            f"{expense[2]} - "
            f"{expense[3]} {currency}\n"
        )

    text += f"\nЗагалом: {total} {currency}"

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


@dp.message(Command("stats"))
async def show_stats(message: Message):
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

    text = "📊 Статистика:\n\n"

    for category, amount in stats.items():
        text += f"{category} — {amount}$\n"

    await message.answer(text)

@dp.message(F.text == "📋 Витрати")
async def expenses_button(message: Message):

    total = sum(expense["amount"] for expense in expenses)

    text = "💸 Твої витрати:\n\n"

    for index, expense in enumerate(expenses, start=1):

        text += (
            f"{index}. "
            f"{expense['category']} - "
            f"{expense['amount']}$\n"
        )

    text += f"\nЗагалом: {total}$"

    await message.answer(text)


@dp.message(F.text == "💰 Всього")
async def total_button(message: Message):
    total = sum(expense[2] for expense in expenses)

    await message.answer(
        f"💰 Загальні витрати: {total}$"
    )

@dp.message(Command("stats"))
async def show_stats(message: Message):

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

    text = "📊 Статистика:\n\n"

    for category, amount in stats.items():
        text += f"{category} — {amount}$\n"

    await message.answer(text)

@dp.message(Command("delete"))
async def delete_expense(message: Message):
    text = message.text.split()

    expense_id = int(text[1])

    delete_expense_db(expense_id)

    await message.answer(
        f"❌ Видалено витрату #{expense_id}"
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
        "interval",
        minutes=1
    )

    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())