from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton
)

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📋 Витрати"),
            KeyboardButton(text="📊 Статистика")
        ],
        [
            KeyboardButton(text="💰 Всього")
        ]
    ],
    resize_keyboard=True
)

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton
)

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="➕ Add Expense"),
            KeyboardButton(text="📊 Analytics")
        ],
        [
            KeyboardButton(text="🎯 Goals"),
            KeyboardButton(text="💳 Subscriptions")
        ],
        [
            KeyboardButton(text="💰 Budget"),
            KeyboardButton(text="⚙️ Settings")
        ]
    ],
    resize_keyboard=True
)