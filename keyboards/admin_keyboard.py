from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

button_cancel = KeyboardButton("/add_product")
button_logout = KeyboardButton("/logout")
admin_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True)
admin_menu_kb.add(button_cancel).add(button_logout)


button_cancel = KeyboardButton("/cancel")
add_product_kd = ReplyKeyboardMarkup(resize_keyboard=True)
add_product_kd.add(button_cancel)
