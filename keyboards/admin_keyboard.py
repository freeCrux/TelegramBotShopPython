from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

add_product_button = KeyboardButton("/add_product")
add_delivery_button = KeyboardButton("/add_delivery")
button_logout = KeyboardButton("/logout")
admin_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True)
admin_menu_kb.add(add_product_button).add(add_delivery_button).add(button_logout)


add_product_button = KeyboardButton("/cancel")
add_product_kd = ReplyKeyboardMarkup(resize_keyboard=True)
add_product_kd.add(add_product_button)
