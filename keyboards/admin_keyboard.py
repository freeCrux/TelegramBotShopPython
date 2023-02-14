from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

add_product_button = KeyboardButton("/add_product")
show_product_button = KeyboardButton("/show_product")
add_delivery_button = KeyboardButton("/add_delivery")
show_delivery_button = KeyboardButton("/show_delivery")
show_client_info = KeyboardButton("/client_info")
button_logout = KeyboardButton("/logout")

admin_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True)
admin_menu_kb.row(add_product_button, show_product_button)
admin_menu_kb.row(add_delivery_button, show_delivery_button)
admin_menu_kb.row(show_client_info)
admin_menu_kb.add(button_logout)
