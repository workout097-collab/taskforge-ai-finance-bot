from datetime import datetime, timedelta
from aiogram.types import Message
import io
import httpx
from premium_limits import can_add_expense
from database import is_premium
from main_keyboard import get_main_keyboard
from premium_limits import can_add_expense, can_use_ai_insight
from ai_insights import get_ai_advice
import sqlite3
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
import matplotlib.pyplot as plt
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from reportlab.pdfgen import canvas
from translations import translations
import csv
from aiogram.types import FSInputFile
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
    create_premium_table,
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
create_premium_table()
import stripe
BOT_TOKEN = os.getenv("BOT_TOKEN")


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

from aiogram.types import LabeledPrice, PreCheckoutQuery, Message
from aiogram import F

# ... всі імпорти ...

# ========== ОПЛАТА ==========
PREMIUM_STARS = 500


@dp.message(Command("buy_premium"))
async def buy_premium(message: Message):
    user_id = message.from_user.id
    await bot.send_invoice(
        chat_id=user_id,
        title="TaskForge AI Premium",
        description="Безліміт витрат, AI-поради, голосові витрати, CSV/PDF звіти",
        payload="premium_monthly",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="Premium місяць", amount=PREMIUM_STARS)],
        start_parameter="premium_subscription"
    )


@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, ok=True)


@dp.message(F.successful_payment)
async def successful_payment(message: Message):
    user_id = message.from_user.id
    trial_end = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    add_premium_user(user_id, 1, trial_end)
    await message.answer("✅ Дякуємо за покупку! Premium активовано на 30 днів.")


# ========== ГОЛОС (тільки один обробник) ==========
@dp.message(F.voice)
async def handle_voice(message: Message):
    user_id = message.from_user.id
    language = get_language_db(user_id)
    t = translations[language]

    if not is_premium(user_id):
        await message.answer("🔒 Голосові витрати — Premium фіча. Купи /premium за $5/міс")
        return

    processing_msg = await message.answer("🎙️ Обробляю голосове...")

    try:
        file = await bot.get_file(message.voice.file_id)
        voice_bytes = await bot.download_file(file.file_path)

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"},
                files={"file": ("voice.ogg", voice_bytes, "audio/ogg")},
                data={"model": "whisper-1", "language": "uk"}
            )
            result = response.json()
            text = result.get("text", "")

        if not text:
            await processing_msg.edit_text("❌ Не вдалося розпізнати. Спробуй ще раз.")
            return

        # Перевірка на ціль
        if "хочу" in text.lower() or "ціль" in text.lower() or "накопичити" in text.lower():
            parts = text.lower().split()
            goal_amount = None
            goal_name = []
            for word in parts:
                if word.isdigit():
                    goal_amount = int(word)
                elif word not in ["хочу", "ціль", "накопичити"]:
                    goal_name.append(word)
            if goal_amount:
                goal_name_str = " ".join(goal_name)
                set_goal_db(user_id, goal_name_str, goal_amount)
                await processing_msg.edit_text(
                    f"🎯 Ціль додано: {goal_name_str} — {goal_amount} {get_currency_db(user_id)}")
                return

        # Перевірка на задачу
        if "задача" in text.lower() or "зробити" in text.lower() or "треба" in text.lower():
            task_text = text.replace("задача", "").replace("зробити", "").replace("треба", "").strip()
            if task_text:
                add_task_db(user_id, task_text)
                await processing_msg.edit_text(f"✅ Задачу додано: {task_text}")
                return

        # Додавання витрати (основний сценарій)
        words = text.lower().split()
        amount = None
        category = "other"

        # Словник слів-чисел (українською)
        number_words = {
            "один": 1, "два": 2, "три": 3, "чотири": 4, "п'ять": 5,
            "шість": 6, "сім": 7, "вісім": 8, "дев'ять": 9, "десять": 10,
            "двадцять": 20, "тридцять": 30, "сорок": 40, "п'ятдесят": 50,
            "шістдесят": 60, "сімдесят": 70, "вісімдесят": 80, "дев'яносто": 90,
            "сто": 100, "двісті": 200, "триста": 300, "п'ятсот": 500,
            "тисяча": 1000
        }

        # Шукаємо цифру або слово-число
        amount = None
        for word in words:
            if word.isdigit():
                amount = int(word)
                break
            if word in number_words:
                amount = number_words[word]
                break

        if not amount:
            number_words = {"п'ятдесят": 50, "сто": 100, "двісті": 200, "триста": 300, "п'ятсот": 500}
            for word, val in number_words.items():
                if word in text.lower():
                    amount = val
                    break

        category_map = {
            "кава": "food", "їжа": "food", "обід": "food",
            "таксі": "transport", "транспорт": "transport", "бензин": "transport",
            "кіно": "entertainment", "фільм": "entertainment",
            "ліки": "health", "лікар": "health"
        }

        for word, cat in category_map.items():
            if word in text.lower():
                category = cat
                break

        if amount:
            add_expense_db(user_id, category, amount)
            currency = get_currency_db(user_id)
            await processing_msg.edit_text(f"✅ Додано: {category} — {amount} {currency}\n🎤 Розпізнано: \"{text}\"")
        else:
            await processing_msg.edit_text(f"❌ Не знайшов суму. Скажи, наприклад: 'кава 50'\nРозпізнано: \"{text}\"")

    except Exception as e:
        await processing_msg.edit_text(f"❌ Помилка: {str(e)}")

@dp.message(Command("buy_stripe"))
async def buy_stripe(message: Message):
    user_id = message.from_user.id
    try:
        checkout_session = stripe.checkout.Session.create(
            client_reference_id=str(user_id),
            payment_method_types=["card"],
            line_items=[
                {
                    "price": "price_1TZV2VQQBexcBmcKLJzc6UYA",  # ← заміни на свій price_id
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url="https://t.me/taskforge_ai_bot",
            cancel_url="https://t.me/taskforge_ai_bot"
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="💳 Купити Premium",
                        url=checkout_session.url
                    )
                ]
            ]
        )
        await message.answer(
            "💎 Преміум підписка через Stripe",
            reply_markup=keyboard
        )
    except Exception as e:
        await message.answer(f"Stripe error:\n{e}")

@dp.message(Command("buy_yearly"))
async def buy_yearly(message: Message):
    user_id = message.from_user.id
    try:
        checkout_session = stripe.checkout.Session.create(
            client_reference_id=str(user_id),
            payment_method_types=["card"],
            line_items=[{
                "price": "price_1TZbFsQQBexcBmcKZhHfMCQ8",  # Заміни на свій
                "quantity": 1,
            }],
            mode="subscription",
            success_url="https://t.me/taskforge_ai_bot",
            cancel_url="https://t.me/taskforge_ai_bot"
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="💳 Оформити річну підписку", url=checkout_session.url)]
            ]
        )
        await message.answer(
            "💎 Річний Premium — $40/рік (економія $20)",
            reply_markup=keyboard
        )
    except Exception as e:
        await message.answer(f"Stripe error:\n{e}")


@dp.message(Command("reset_tasks"))
async def reset_tasks(message: Message):
    # Тільки для адміна
    if message.from_user.id != admin_id:
        return

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    # Видалити всі задачі
    cursor.execute("DELETE FROM tasks")

    # Скинути лічильник AUTOINCREMENT
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='tasks'")

    conn.commit()
    conn.close()

    await message.answer("✅ Всі задачі видалені. Лічильник скинуто до 1.")


# ... решта коду (premium_button, add, start і т.д.)


def add_recurring_expense_db(user_id, name, amount, category, frequency):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    from datetime import datetime, timedelta
    if frequency == "daily":
        next_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    elif frequency == "weekly":
        next_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    else:  # monthly
        next_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

    cursor.execute("""
        INSERT INTO recurring_expenses (user_id, name, amount, category, frequency, next_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, name, amount, category, frequency, next_date))

    conn.commit()
    conn.close()


def get_recurring_expenses_db(user_id):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recurring_expenses WHERE user_id = ?", (user_id,))
    result = cursor.fetchall()
    conn.close()
    return result


def check_recurring_expenses():
    """Автоматично додає витрати, які мають настати сьогодні"""
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT * FROM recurring_expenses WHERE next_date <= ?", (today,))
    expenses = cursor.fetchall()

    for exp in expenses:
        # Додаємо витрату
        add_expense_db(exp[1], exp[4], exp[3])

        # Оновлюємо next_date
        from datetime import datetime, timedelta
        if exp[5] == "daily":
            new_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        elif exp[5] == "weekly":
            new_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        else:
            new_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        cursor.execute("UPDATE recurring_expenses SET next_date = ? WHERE id = ?", (new_date, exp[0]))

    conn.commit()
    conn.close()


@dp.message(Command("recurring"))
async def add_recurring(message: Message):
    user_id = message.from_user.id

    if not is_premium(user_id):
        await message.answer("🔒 Регулярні платежі — Premium фіча. /premium")
        return

    # /recurring Netflix 40 monthly
    parts = message.text.split()
    if len(parts) < 4:
        await message.answer("❌ Формат: /recurring назва сума частота (daily/weekly/monthly)")
        return

    name = parts[1]
    amount = int(parts[2])
    frequency = parts[3]

    if frequency not in ["daily", "weekly", "monthly"]:
        await message.answer("❌ Частота: daily, weekly або monthly")
        return

    category = detect_category(name)
    add_recurring_expense_db(user_id, name, amount, category, frequency)

    await message.answer(f"✅ Додано регулярний платіж: {name} — {amount} {get_currency_db(user_id)} ({frequency})")


@dp.message(Command("recurring_list"))
async def list_recurring(message: Message):
    user_id = message.from_user.id
    recurring = get_recurring_expenses_db(user_id)

    if not recurring:
        await message.answer("📭 Немає регулярних платежів")
        return

    text = "🔄 Регулярні платежі:\n\n"
    for r in recurring:
        text += f"• {r[2]} — {r[3]} {get_currency_db(user_id)} ({r[5]}) — наступний: {r[6]}\n"

    await message.answer(text)

@dp.message(F.text.in_(["👑 Premium", "👑 Преміум"]))
async def premium_button(message: Message):
    user_id = message.from_user.id
    language = get_language_db(user_id)
    t = translations[language]

    # Перевіряємо, чи вже Premium
    #if is_premium(user_id):
        #await message.answer("✅ У вас вже активний Premium!\n\nДякуємо за підтримку 💙")
        #return

    # Показуємо опис і пропонуємо купити
    await message.answer(
        t["premium_text"] + "\n\n💰 Натисніть /buy_premium для оформлення",
        parse_mode="Markdown"
    )

@dp.message(Command("advice"))
async def advice_command(message: Message):
    user_id = message.from_user.id
    language = get_language_db(user_id)

    # Перевірка ліміту
    can_use, msg = can_use_ai_insight(user_id)
    if not can_use:
        await message.answer(msg)
        return

    await message.answer("🤔 Аналізую витрати...")
    advice = await get_ai_advice(user_id, language)
    await message.answer(advice)


# Додай у send_daily_reminder або окремий scheduler
async def check_subscriptions():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT user_id FROM subscriptions")
    users = cursor.fetchall()

    for (user_id,) in users:
        subscriptions = get_subscriptions_db(user_id)
        total = sum(s[3] for s in subscriptions)

        await bot.send_message(
            user_id,
            f"📅 Нагадування: у тебе {len(subscriptions)} підписок на загальну суму {total} {get_currency_db(user_id)}/міс. \nСписок: /subscriptions"
        )
    conn.close()


# У main() додати:
scheduler.add_job(check_subscriptions, "cron", day_of_week="mon", hour=10, minute=0)

# Додай нові кнопки в клавіатуру
TEMPLATES = {
    "🏠 Дім": [("Продукти", 200), ("Комуналка", 150)],
    "🚗 Транспорт": [("Таксі", 50), ("Бензин", 100)],
    "🍕 Їжа": [("Кава", 30), ("Обід", 120)],
}


@dp.message(F.text.in_(["🏠 Дім", "🚗 Транспорт", "🍕 Їжа"]))
async def apply_template(message: Message):
    user_id = message.from_user.id
    template_name = message.text
    items = TEMPLATES[template_name]

    for category, amount in items:
        add_expense_db(user_id, category.lower(), amount)

    await message.answer(f"✅ Додано шаблон {template_name}: {len(items)} витрат")

@dp.message(Command("english"))
async def english_lang(message: Message):

    user_id = message.from_user.id

    set_language_db(user_id, "en")

    await message.answer(
        "🇬🇧 English enabled",
        reply_markup=get_main_keyboard("en")
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

    #if message.from_user.id != 1128720977:
      #  return

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

@dp.message(F.text.in_(["✅ Tasks", "✅ Задачі"]))
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

@dp.message(F.text.in_(["➕ Add Expense", "➕ Додати витрату"]))
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


@dp.message(Command("export"))
async def export_csv(message: Message):
    user_id = message.from_user.id
    language = get_language_db(user_id)
    t = translations[language]

    if not is_premium(user_id):
        await message.answer("🔒 " + t["premium_required"])
        return

    expenses = get_expenses_db(user_id)
    if not expenses:
        await message.answer(t["no_expenses"])
        return

    csv_name = f"reports/export_{user_id}.csv"
    with open(csv_name, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Category", "Amount", "Date"])
        for e in expenses:
            writer.writerow([e[0], e[2], e[3], e[4]])

    await message.answer_document(
        document=FSInputFile(csv_name),
        caption="📊 Your expenses exported to CSV"
    )


@dp.message(Command("subscribe"))
async def subscribe_command(message: Message):
    user_id = message.from_user.id  # ← спочатку визнач user_id

    if not is_premium(user_id):
        subscriptions = get_subscriptions_db(user_id)
        if len(subscriptions) >= 3:
            await message.answer("❌ Ліміт 3 підписки в безкоштовній версії. Купи Premium за $5/міс.")
            return

    language = get_language_db(user_id)
    t = translations[language]

    text = message.text.split()
    name = text[1]
    amount = int(text[2])
    add_subscription_db(user_id, name, amount)
    currency = get_currency_db(user_id)

    await message.answer(f"{t['subscription_added']}\n\n{name} — {amount} {currency}/month")


@dp.message(F.text.in_(["💳 Subscriptions", "💳 Підписки"]))
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

    if not is_premium(user_id):
        await message.answer(t["premium_required"])
        return

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
        stats[category] = stats.get(category, 0) + amount

    top_category = max(stats, key=stats.get)
    top_amount = stats[top_category]
    percent = round((top_amount / total) * 100)

    currency = get_currency_db(user_id)  # ← Отримуємо валюту користувача

    text = (
        f"{t['ai_analysis']}\n\n"
        f"{t['top_expense']} {top_category} — {top_amount} {currency}\n\n"
        f"⚠️ {top_category} {t['expense_percent']} {percent}%\n\n"
    )

    if percent > 50:
        text += f"{t['reduce_expenses']} {top_category}"
    else:
        text += t["good_balance"]

    await message.answer(text)


@dp.message(F.text.in_(["📄 Report", "📄 Звіт"]))
async def report_handler(message: Message):
    user_id = message.from_user.id
    language = get_language_db(user_id)
    t = translations[language]

    if not is_premium(user_id):
        await message.answer("🔒 " + t["premium_required"])
        return

    expenses = get_expenses_db(user_id)
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Створюємо папку reports, якщо немає
    os.makedirs("reports", exist_ok=True)

    pdf_name = f"reports/report_{user_id}_{current_date}.pdf"
    pdf = canvas.Canvas(pdf_name)

    # TITLE
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawString(180, 800, "TaskForge AI")
    pdf.setFont("Helvetica", 16)
    pdf.drawString(200, 770, "Finance Report")

    # USER INFO
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 730, f"User ID: {user_id}")
    pdf.drawString(50, 710, f"Date: {current_date}")

    # LINE
    pdf.line(50, 690, 550, 690)

    # EXPENSES TITLE
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, 660, "Expenses")

    y = 630
    total = 0
    pdf.setFont("Helvetica", 12)

    if not expenses:
        pdf.drawString(50, y, "No expenses yet")
    else:
        currency = get_currency_db(user_id)
        for expense in expenses:
            category = expense[2]
            amount = expense[3]
            total += amount
            pdf.drawString(70, y, f"• {category} — {amount} {currency}")
            y -= 25
            if y < 100:  # Нова сторінка
                pdf.showPage()
                y = 800

        # TOTAL
        pdf.line(50, y, 550, y)
        y -= 30
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, y, f"Total: {total} {currency}")

    # FOOTER
    pdf.setFont("Helvetica-Oblique", 10)
    pdf.drawString(180, 50, "Generated by TaskForge AI")
    pdf.save()

    await message.answer_document(
        document=FSInputFile(pdf_name),
        caption="📄 Your finance report is ready"
    )

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
        stats[category] = stats.get(category, 0) + amount

    currency = get_currency_db(user_id)  # ← Отримуємо валюту

    text = f"{t['warnings_title']}\n\n"

    for category, amount in stats.items():
        percent = (amount / total) * 100
        if percent >= 50:
            text += f"{t['big_expenses']} {category} ({percent:.1f}%)\n"

    if total > 1000:
        text += f"\n{t['too_much_spending']} ({total} {currency})"
    elif total < 200:
        text += f"\n{t['good_control']}"

    await message.answer(text)


@dp.message(Command("stats"))
async def show_stats(message: Message):
    user_id = message.from_user.id
    language = get_language_db(user_id)
    t = translations[language]

    expenses = get_expenses_db(user_id)

    if not expenses:
        await message.answer(t["no_expenses"])
        return

    # Мапа для нормалізації категорій
    category_normalize = {
        "food": "Їжа",
        "transport": "Транспорт",
        "entertainment": "Розваги",
        "shopping": "Покупки",
        "health": "Здоров'я",
        "work": "Робота",
        "other": "Інше",
        "таксі": "Транспорт",
        "бензин": "Транспорт",
        "кава": "Їжа",
        "їжа": "Їжа",
        "кіно": "Розваги",
        "ліки": "Здоров'я",
    }

    stats = {}
    for expense in expenses:
        category = expense[2].lower()
        amount = expense[3]

        # Нормалізуємо категорію
        normalized = category_normalize.get(category, category.capitalize())
        stats[normalized] = stats.get(normalized, 0) + amount

    # Сортуємо за сумою (від більшої до меншої)
    sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)

    currency = get_currency_db(user_id)
    total = sum(stats.values())

    text = f"{t['statistics']}\n\n"
    for category, amount in sorted_stats:
        text += f"{category} — {amount} {currency}\n"

    text += f"\n{t['total']}: {total} {currency}"

    await message.answer(text)

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
    if premium_user is None:  # Якщо немає запису — даємо триал
        trial_end = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        add_premium_user(user_id, 1, trial_end)


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
        reply_markup=get_main_keyboard(language)

    )

@dp.message(Command("add"))
async def add_expense(message: Message):
    try:
        user_id = message.from_user.id
        language = get_language_db(user_id)
        t = translations[language]

        # === ПЕРЕВІРКА ЛІМІТУ ===
        current_month = datetime.now().strftime("%Y-%m")
        can_add, msg = can_add_expense(user_id, current_month)
        if not can_add:
            await message.answer(msg)
            return
        # === КІНЕЦЬ ПЕРЕВІРКИ ===

        text = message.text.split()
        if len(text) == 2:
            category = "other"
            amount = int(text[1])
        else:
            category = detect_category(text[1])
            amount = int(text[2])

        add_expense_db(user_id, category, amount)
        currency = get_currency_db(user_id)

        await message.answer(
            f"{t['added']}\n\n"
            f"{t['category']}: {category}\n"
            f"{t['amount']}: {amount} {currency}"
        )
    except ValueError:
        await message.answer(t["amount_must_be_number"])
    except:
        await message.answer(t["add_format"])


@dp.message(F.text.in_(["📊 Analytics", "📊 Аналітика"]))
async def analytics_button(message: Message):
    user_id = message.from_user.id

    language = get_language_db(user_id)
    t = translations[language]

    await message.answer(
        "/stats\n/chart\n/insights\n/warnings\n/month"
    )

@dp.message(F.text.in_(["🎯 Goals", "🎯 Цілі"]))
async def goals_button(message: Message):

    user_id = message.from_user.id

    language = get_language_db(user_id)

    t = translations[language]

    await message.answer(
        t["goals_menu"]
    )

@dp.message(F.text == "💳 Subscriptions")
async def subscriptions_button(message: Message):

    await message.answer(
        "/subscribe netflix 40\n/subscriptions"
    )

@dp.message(F.text.in_(["💰 Budget", "💰 Бюджет"]))
async def budget_button(message: Message):

    await message.answer(
        "/budget 5000\n/budget_status"
    )
@dp.message(F.text.in_(["💱 Currency", "💱 Валюта"]))
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

@dp.message(F.text.in_(["🌍 Language", "🌍 Мова"]))
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

    if message.text.startswith("/"):
        return

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



if __name__ == "__main__":
    asyncio.run(main())


