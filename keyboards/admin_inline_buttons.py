from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


cancel_button = InlineKeyboardButton(text="Отменить ввод", callback_data="cancel_input")
cancel_input_inline_kd = InlineKeyboardMarkup(row_width=1)
cancel_input_inline_kd.add(cancel_button)


async def get_product_editor_menu_inline_kd(prod_id: int) -> InlineKeyboardMarkup:
    product_change_button = InlineKeyboardButton(text="Изменить товар", callback_data=f"id_product_to_change:{prod_id}")
    product_delete_button = InlineKeyboardButton(text="Удалить товар", callback_data=f"id_product_ro_delete:{prod_id}")
    product_editor_menu_inline_kd = InlineKeyboardMarkup(row_width=2)
    product_editor_menu_inline_kd.row(product_change_button, product_delete_button)

    return product_editor_menu_inline_kd


async def get_products_list_inl_kb(products: list, mode: str) -> InlineKeyboardMarkup:
    """
    :param mode: prod_id_for_redactor for callback which show all products,
                 prod_id_for_delivery for callback which add new delivery
    :param products: all product in BD
    :return: inline keyboard by all products
    """
    prod_inl_kb = InlineKeyboardMarkup(row_width=1)
    for pr in products:
        # <pr[1] - name of product>, <pr[2] - price of product>, <pr[4] - id of product>
        prod_inl_kb.add(InlineKeyboardButton(text=f"{pr[1]} - {pr[2]}$", callback_data=f"{mode}:{pr[4]}"), )

    return prod_inl_kb
