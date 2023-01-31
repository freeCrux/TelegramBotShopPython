from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text

from keyboards import client_menu_kb, get_products_inl_kb, buy_inline_kd
from bot_init import bot, dp
from config import client_message_handler_text
from database import sql_db


async def start_help(message: types.Message):
    await sql_db.add_client(message)
    await bot.send_message(message.from_user.id, client_message_handler_text["start"] +
                           client_message_handler_text["help"], reply_markup=client_menu_kb)


async def show_all_products(message: types.Message):
    products: list = await sql_db.get_product_list()

    await bot.send_message(message.from_user.id, "Продукция:\n",
                           reply_markup=await get_products_inl_kb(products=products))


async def show_product(callback: types.CallbackQuery):
    product_id = callback.data.split(':')[1]
    prod_data: tuple = await sql_db.get_product(prod_id=product_id)
    await bot.send_photo(callback.message.chat.id, prod_data[0],
                         f"Name: {prod_data[1]} | Price: {prod_data[2]}\nDescription: {prod_data[-1]}",
                          reply_markup=buy_inline_kd)


async def show_balance(message: types.Message):
    await bot.send_message(message.from_user.id, client_message_handler_text["balance"], reply_markup=client_menu_kb)


async def deposit_money(message: types.Message):
    await bot.send_message(message.from_user.id, client_message_handler_text["deposit"], reply_markup=client_menu_kb)


async def show_my_last_bye(message: types.Message):
    await bot.send_message(message.from_user.id, client_message_handler_text["myLastBuy "], reply_markup=client_menu_kb)


def register_client_handlers(dp: Dispatcher):
    # <Start and help message, add user in BD if he isn`t in BD>
    dp.register_message_handler(start_help, commands=["start", "help"])
    dp.register_message_handler(start_help, Text(equals="Помощь", ignore_case=True))

    # <Show products in stock>
    dp.register_message_handler(show_all_products, commands=["products"])
    dp.register_message_handler(show_all_products, Text(equals="Ассортимент", ignore_case=True))

    # <Show products in stock>
    dp.register_message_handler(show_balance, commands=["balance"])
    dp.register_message_handler(show_balance, Text(equals="Баланс", ignore_case=True))

    # <Show products in stock>
    dp.register_message_handler(deposit_money, commands=["paid"])
    dp.register_message_handler(deposit_money, Text(equals="Пополнить баланс", ignore_case=True))

    # <Show products in stock>
    dp.register_message_handler(show_my_last_bye, commands=["myBuy"])
    dp.register_message_handler(show_my_last_bye, Text(equals="Мои покупки", ignore_case=True))
    dp.register_callback_query_handler(show_product, Text(startswith="prod_id:", ignore_case=True))
