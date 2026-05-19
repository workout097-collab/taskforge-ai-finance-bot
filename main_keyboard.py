from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from translations import translations

def get_main_keyboard(language="en"):
    if language == "ua":
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="➕ Додати витрату"), KeyboardButton(text="📊 Аналітика")],
                [KeyboardButton(text="🎯 Цілі"), KeyboardButton(text="✅ Задачі")],
                [KeyboardButton(text="💰 Бюджет"), KeyboardButton(text="📄 Звіт")],
                [KeyboardButton(text="💳 Підписки"), KeyboardButton(text="💱 Валюта")],
                [KeyboardButton(text="🏠 Дім"), KeyboardButton(text="🚗 Транспорт"), KeyboardButton(text="👑 Преміум")],
                [KeyboardButton(text="🌍 Мова")]
            ],
            resize_keyboard=True
        )
    else:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="➕ Add Expense"), KeyboardButton(text="📊 Analytics")],
                [KeyboardButton(text="🎯 Goals"), KeyboardButton(text="✅ Tasks")],
                [KeyboardButton(text="💰 Budget"), KeyboardButton(text="📄 Report")],
                [KeyboardButton(text="💳 Subscriptions"), KeyboardButton(text="💱 Currency")],
                [KeyboardButton(text="🏠 Home"), KeyboardButton(text="🚗 Transport"), KeyboardButton(text="👑 Premium")],
                [KeyboardButton(text="🌍 Language")]
            ],
            resize_keyboard=True
        )
    return keyboard
