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