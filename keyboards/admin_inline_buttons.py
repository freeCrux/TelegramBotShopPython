from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


cancel_button = InlineKeyboardButton(text="Отменить ввод", callback_data="cancel_input")
cancel_input_inline_kd = InlineKeyboardMarkup(row_width=1)
cancel_input_inline_kd.add(cancel_button)


def get_product_editor_menu_inline_kd_root(prod_id: int) -> InlineKeyboardMarkup:
    change_button = InlineKeyboardButton(text="Изменить товар", callback_data=f"id_product_to_change:{prod_id}")
    delete_button = InlineKeyboardButton(text="Удалить товар", callback_data=f"id_product_to_delete:{prod_id}")
    product_editor = InlineKeyboardMarkup(row_width=2)
    product_editor.row(change_button, delete_button)

    return product_editor


def get_products_list_inl_kb_root(products: list, mode: str) -> InlineKeyboardMarkup:
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


def get_delivers_list_inl_kb_root(delivers: list) -> InlineKeyboardMarkup:
    inl_kb = InlineKeyboardMarkup(row_width=1)
    for d in delivers:
        # <d[0] - ID of the product that is attached to the delivery>,
        # <d[2] - date of adding>, <d[4] - id of delivery>
        inl_kb.add(InlineKeyboardButton(text=f"Product ID: {d[0]} | Date of Adding {d[4]}",
                                             callback_data=f"delivery_id_root:{d[5]}"), )

    return inl_kb


def get_delivery_editor_menu_inline_kd_root(del_id: int) -> InlineKeyboardMarkup:
    delete_button = InlineKeyboardButton(text="Удалить доставку", callback_data=f"id_delivery_to_delete:{del_id}")
    menu_inline_kd = InlineKeyboardMarkup(row_width=2)
    menu_inline_kd.add(delete_button)

    return menu_inline_kd


def get_sales_list_inl_kb_root(sales: list) -> InlineKeyboardMarkup:
    inl_kb = InlineKeyboardMarkup(row_width=1)
    for sl in sales:
        # <sl[3] - date of sale>, <sl[0] - ID of sale>, <sl[2] - delivery id that refer to sale>
        inl_kb.add(InlineKeyboardButton(text=f"Date: {sl[3]} | ID: {sl[0]}", callback_data=f"sale_id:{sl[2]}"))

    return inl_kb


def get_wallet_address_list_inl_kb_root(addresses: list) -> InlineKeyboardMarkup:
    inl_kb = InlineKeyboardMarkup(row_width=1)
    for address in addresses:
        # <address[0] - ID of address>, <address[2] - balance>, <address[3] - usedUntil>, <address[4] - network>
        # <address[5] - frozen>
        inl_kb.add(InlineKeyboardButton(
            text=f"ID: {address[0]} | Balance: {address[2]} {address[4]}\n"
                 f"Usage until: {address[3]} | Frozen: {address[5]}",
            callback_data=f"address_id:{address[0]}"))

    return inl_kb


def get_wallet_address_editor_menu_inline_kd_root(address_id: int) -> InlineKeyboardMarkup:
    """
    :return: Menu of inline buttons, such us delete_button with callback_data - id_address_to_delete:{address_id}
             and freeze_button with callback_data - id_address_to_freeze:{address_id}
    """
    delete_button = InlineKeyboardButton(text="Удалить адрес", callback_data=f"id_address_to_delete:{address_id}")
    freeze_button = InlineKeyboardButton(text="Заморозить адрес", callback_data=f"id_address_to_freeze:{address_id}")
    menu_inline_kd = InlineKeyboardMarkup(row_width=2)
    menu_inline_kd.row(delete_button, freeze_button)

    return menu_inline_kd
