from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


cancel_button = InlineKeyboardButton(text="Отменить ввод", callback_data="cancel_input")
cancel_input_inline_kd = InlineKeyboardMarkup(row_width=1)
cancel_input_inline_kd.add(cancel_button)


async def get_product_editor_menu_inline_kd(prod_id: int) -> InlineKeyboardMarkup:
    change_button = InlineKeyboardButton(text="Изменить товар", callback_data=f"id_product_to_change:{prod_id}")
    delete_button = InlineKeyboardButton(text="Удалить товар", callback_data=f"id_product_to_delete:{prod_id}")
    product_editor_ = InlineKeyboardMarkup(row_width=2)
    product_editor_.row(change_button, delete_button)

    return product_editor_


async def get_products_list_inl_kb(products: list, mode: str) -> InlineKeyboardMarkup:
    """
    :param mode: prod_id_for_redactor for callback which show all products,
                 prod_id_for_delivery for callback which add new delivery
    :param products: all product in BD
    :return: inline keyboard by all products
    """
    inl_kb = InlineKeyboardMarkup(row_width=1)
    for pr in products:
        # <pr[1] - name of product>, <pr[2] - price of product>, <pr[4] - id of product>
        inl_kb.add(InlineKeyboardButton(text=f"{pr[1]} - {pr[2]}$", callback_data=f"{mode}:{pr[4]}"), )

    return inl_kb


async def get_delivers_list_inl_kb(delivers: list) -> InlineKeyboardMarkup:
    inl_kb = InlineKeyboardMarkup(row_width=1)
    for d in delivers:
        # <d[0] - ID of the product that is attached to the delivery>,
        # <d[2] - date of adding>, <d[4] - id of delivery>
        inl_kb.add(InlineKeyboardButton(text=f"Product ID: {d[0]} | Date of Adding {d[4]}",
                                             callback_data=f"delivery_id:{d[5]}"), )

    return inl_kb


async def get_delivery_editor_menu_inline_kd(del_id: int) -> InlineKeyboardMarkup:
    delete_button = InlineKeyboardButton(text="Удалить доставку", callback_data=f"id_delivery_to_delete:{del_id}")
    menu_inline_kd = InlineKeyboardMarkup(row_width=2)
    menu_inline_kd.add(delete_button)

    return menu_inline_kd
