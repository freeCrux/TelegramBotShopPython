from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import available_network


def get_buy_inl_kb(prod_id: int) -> InlineKeyboardMarkup:
    buy_button = InlineKeyboardButton(text="Купить", callback_data=f"buy_prod_id:{prod_id}")
    inl_kb = InlineKeyboardMarkup(row_width=1)
    inl_kb.add(buy_button)

    return inl_kb


def get_products_list_inl_kb(products: list) -> InlineKeyboardMarkup:
    inl_kb = InlineKeyboardMarkup(row_width=1)
    for pr in products:
        # <pr[1] - name of product>, <pr[2] - price of product>, <pr[4] - id of product>
        inl_kb.add(InlineKeyboardButton(text=f"{pr[1]} - {pr[2]}$", callback_data=f"prod_id:{pr[4]}"))

    return inl_kb


def get_sales_list_inl_kb(sales: list) -> InlineKeyboardMarkup:
    inl_kb = InlineKeyboardMarkup(row_width=1)
    for sl in sales:
        # <sl[3] - date of sale>, <sl[0] - ID of sale>, <sl[2] - delivery id that refer to sale>
        inl_kb.add(InlineKeyboardButton(text=f"Date: {sl[3]} | ID: {sl[0]}", callback_data=f"delivery_id:{sl[2]}"))

    return inl_kb


def get_address_network_inl_kb() -> InlineKeyboardMarkup:
    inl_kb = InlineKeyboardMarkup(row_width=1)
    for network in available_network:
        inl_kb.add(InlineKeyboardButton(text=f"Сеть: {network}", callback_data=f"network:{network}"))

    return inl_kb
