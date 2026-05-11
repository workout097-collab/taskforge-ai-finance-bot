from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="➕ Add Expense"),
            KeyboardButton(text="📊 Analytics")
        ],
        [
            KeyboardButton(text="🎯 Goals"),
            KeyboardButton(text="✅ Tasks")
        ],
        [
            KeyboardButton(text="💰 Budget"),
            KeyboardButton(text="📄 Report")
        ],
        [   KeyboardButton(text="💳 Subscriptions"),
            KeyboardButton(text="⚙️ Settings")
        ]
    ],
    resize_keyboard=True
)