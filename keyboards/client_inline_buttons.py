from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


buy_button = InlineKeyboardButton(text="Купить", callback_data="buy")
buy_inline_kd = InlineKeyboardMarkup(row_width=1)
buy_inline_kd.add(buy_button)


async def get_products_list_inl_kb(products: list) -> InlineKeyboardMarkup:
    inl_kb = InlineKeyboardMarkup(row_width=1)
    for pr in products:
        # <pr[1] - name of product>, <pr[2] - price of product>, <pr[4] - id of product>
        inl_kb.add(InlineKeyboardButton(text=f"{pr[1]} - {pr[2]}$", callback_data=f"prod_id:{pr[4]}"))

    return inl_kb
