from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


cancel_button = InlineKeyboardButton(text="Отменить ввод", callback_data="cancel_input")
cancel_input_inline_kd = InlineKeyboardMarkup(row_width=1)
cancel_input_inline_kd.add(cancel_button)


product_edit_button = InlineKeyboardButton(text="Изменить товар", callback_data="product_edit")
product_delete_button = InlineKeyboardButton(text="Удалить товар", callback_data="product_delete")
product_editor_menu_inline_kd = InlineKeyboardMarkup(row_width=2)
product_editor_menu_inline_kd.row(product_edit_button, product_delete_button)


async def get_products_inl_kb(products: list) -> InlineKeyboardMarkup:
    prod_inl_kb = InlineKeyboardMarkup(row_width=1)
    for pr in products:
        # <pr[1] - name of product>, <pr[2] - price of product>
        prod_inl_kb.add(InlineKeyboardButton(text=f"{pr[1]} - {pr[2]}$", callback_data=pr[1]))

    return prod_inl_kb
