from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from texts import TEXTS

def get_main_keyboard(language="en"):

     texts = TEXTS[language]

     keyboard = ReplyKeyboardMarkup(

            keyboard=[

                [
                    KeyboardButton(text=texts["add_expense"]),
                    KeyboardButton(text=texts["analytics"])
                ],

                [
                    KeyboardButton(text=texts["goals"]),
                    KeyboardButton(text=texts["tasks"])
                ],

                [
                    KeyboardButton(text=texts["budget"]),
                    KeyboardButton(text=texts["report"])
                ],

                [
                    KeyboardButton(text=texts["subscriptions"]),
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

