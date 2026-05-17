from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from translations import translations

def get_main_keyboard(language="en"):

    if language == "ua":

        keyboard = ReplyKeyboardMarkup(

            keyboard=[

                [
                    KeyboardButton(text="➕ Додати витрату"),
                    KeyboardButton(text="📊 Аналітика")
                ],

                [
                    KeyboardButton(text="🎯 Цілі"),
                    KeyboardButton(text="✅ Задачі")
                ],

                [
                    KeyboardButton(text="💰 Бюджет"),
                    KeyboardButton(text="📄 Звіт")
                ],

                [
                    KeyboardButton(text="💳 Підписки"),
                    KeyboardButton(text="💱 Валюта")
                ],

                [
                    KeyboardButton(text="🌍 Мова"),
                    KeyboardButton(text="👑 Преміум")
                ]

            ],

            resize_keyboard=True
        )

    else:

        keyboard = ReplyKeyboardMarkup(

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

                [
                    KeyboardButton(text="💳 Subscriptions"),
                    KeyboardButton(text="💱 Currency")
                ],

                [
                    KeyboardButton(text="🌍 Language"),
                    KeyboardButton(text="👑 Premium")
                ]

            ],

            resize_keyboard=True
        )

    return keyboard

