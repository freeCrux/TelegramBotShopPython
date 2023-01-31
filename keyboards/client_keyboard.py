from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


products_button = KeyboardButton("Ассортимент")
balance_button = KeyboardButton("Баланс")
paid_button = KeyboardButton("Пополнить баланс")
buy_button = KeyboardButton("Мои покупки")
help_button = KeyboardButton("Помощь")

client_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True)
client_menu_kb.add(products_button)
client_menu_kb.add(balance_button)
client_menu_kb.add(paid_button)
client_menu_kb.row(buy_button, help_button)
