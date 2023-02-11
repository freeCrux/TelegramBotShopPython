from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def get_buy_inl_kb(prod_id: int) -> InlineKeyboardMarkup:
    buy_button = InlineKeyboardButton(text="Купить", callback_data=f"buy_prod_id:{prod_id}")
    inl_kb = InlineKeyboardMarkup(row_width=1)
    inl_kb.add(buy_button)

    return inl_kb


async def get_products_list_inl_kb(products: list) -> InlineKeyboardMarkup:
    inl_kb = InlineKeyboardMarkup(row_width=1)
    for pr in products:
        # <pr[1] - name of product>, <pr[2] - price of product>, <pr[4] - id of product>
        inl_kb.add(InlineKeyboardButton(text=f"{pr[1]} - {pr[2]}$", callback_data=f"prod_id:{pr[4]}"))

    return inl_kb
