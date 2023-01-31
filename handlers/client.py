from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text

from keyboards import client_menu_kb
from bot_init import bot, dp
from config import client_message_handler_text
from database import sql_db


async def start_help(message: types.Message):
    await sql_db.add_client(message)
    await bot.send_message(message.from_user.id, client_message_handler_text["start"] +
                           client_message_handler_text["help"], reply_markup=client_menu_kb)


async def get_all_products(message: types.Message):
    await sql_db.get_all_product(message=message)


async def get_balance(message: types.Message):
    await bot.send_message(message.from_user.id, client_message_handler_text["balance"], reply_markup=client_menu_kb)


async def deposit_money(message: types.Message):
    await bot.send_message(message.from_user.id, client_message_handler_text["deposit"], reply_markup=client_menu_kb)


async def get_my_last_bye(message: types.Message):
    await bot.send_message(message.from_user.id, client_message_handler_text["myLastBuy "], reply_markup=client_menu_kb)


def register_client_handlers(dp: Dispatcher):
    # <Start and help message, add user in BD if he isn`t in BD>
    dp.register_message_handler(start_help, commands=["start", "help"])
    dp.register_message_handler(start_help, Text(equals="Помощь", ignore_case=True))

    # <Show products in stock>
    dp.register_message_handler(get_all_products, commands=["products"])
    dp.register_message_handler(get_all_products, Text(equals="Ассортимент", ignore_case=True))

    # <Show products in stock>
    dp.register_message_handler(get_balance, commands=["balance"])
    dp.register_message_handler(get_balance, Text(equals="Баланс", ignore_case=True))

    # <Show products in stock>
    dp.register_message_handler(deposit_money, commands=["paid"])
    dp.register_message_handler(deposit_money, Text(equals="Пополнить баланс", ignore_case=True))

    # <Show products in stock>
    dp.register_message_handler(get_my_last_bye, commands=["myBuy"])
    dp.register_message_handler(get_my_last_bye, Text(equals="Мои покупки", ignore_case=True))
