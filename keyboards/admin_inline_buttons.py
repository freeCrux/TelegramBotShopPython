# Inline Buttons
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


cancel_button = InlineKeyboardButton(text="Отменить ввод", callback_data="cancel_input")
cancel_input_inline_kd = InlineKeyboardMarkup(row_width=1)
cancel_input_inline_kd.add(cancel_button)


product_edit_button = InlineKeyboardButton(text="Изменить товар", callback_data="product_edit")
product_delete_button = InlineKeyboardButton(text="Удалить товар", callback_data="product_delete")
product_editor_menu_inline_kd = InlineKeyboardMarkup(row_width=2)
product_editor_menu_inline_kd.row(product_edit_button, product_delete_button)
