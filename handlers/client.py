from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text

from keyboards.client_inline_buttons import *
from keyboards.client_keyboard import client_menu_kb

from bot_init import bot, dp
from database import sql_db


async def start_help(message: types.Message):
    await sql_db.add_client(client_id=message.from_user.id)
    await bot.send_message(message.from_user.id, "Привет ты попал в магазин выпечки!\n\n"
                           "Вы по любым вопросам вы всегда можете обратиться в поддержку @freecrux\n"
                           "В случае проблем с заказом вам понадобиться ваш ИД (/wallet) и ИД вашего заказа (/myBuy)\n"
                           "\nДля покупки вам нужно пополнить счет, введите команду /pay или "
                           "выберите в меню пункт [Пополнить баланс]\n\n"
                           "Для простотра баланса и общей информации о вас, введите команду /wallet или "
                           "выберите в меню пункт [Баланс]\n\n"
                           "Список товараов обновляеться динамически при поступлении нового товара, для просмтора "
                           "товара в наличии введите команду /products или выберите в меню пункт [Ассортимент]\n\n"
                           "Для просмотра последних покупок введите команду "
                           "/myBuy или выберите в меню пункт [Мои покупки]", reply_markup=client_menu_kb)


async def show_available_products(message: types.Message):
    products: list = await sql_db.get_available_product_list()
    if len(products) > 0:
        await bot.send_message(message.from_user.id, "Весь стафф:\n",
                               reply_markup=await get_products_list_inl_kb(products=products))
    else:
        await bot.send_message(message.from_user.id, "К великому сожалению товар закончилю, приходи позже ;)",
                               reply_markup=client_menu_kb)


async def show_product(callback: types.CallbackQuery):
    product_id = int(callback.data.split(':')[1])
    prod_data: tuple = await sql_db.get_product_info(prod_id=product_id)
    await bot.send_photo(callback.message.chat.id, prod_data[0],
                         f"Название: {prod_data[1]} | Цена: {prod_data[2]}$\nОписание: {prod_data[3]}",
                         reply_markup=await get_buy_inl_kb(prod_id=product_id))


async def buy_product(callback: types.CallbackQuery):
    product_id = int(callback.data.split(':')[1])
    product_price: int = await sql_db.get_product_price(prod_id=product_id)
    client_id = callback.message.chat.id
    balance: int = await sql_db.get_client_balance(client_id=client_id)
    if balance >= product_price:
        await sql_db.change_client_balance(client_id=client_id, cash=(-1) * product_price)
        # TODO add sales
        await callback.answer("Поздравляю с покупкой")
    else:
        await callback.answer("На балансе недостаточно средств")


async def show_client_info(message: types.Message):
    data: tuple = await sql_db.get_client_data(client_id=message.from_user.id)
    await bot.send_message(message.from_user.id, f"Твой ID: {data[0]}\nБаланс счета: {data[1]}$",
                           reply_markup=client_menu_kb)


async def deposit_money(message: types.Message):
    await bot.send_message(message.from_user.id, "deposit", reply_markup=client_menu_kb)


async def show_my_last_bye(message: types.Message):
    await bot.send_message(message.from_user.id, "myLastBuy", reply_markup=client_menu_kb)


def register_client_handlers(dp: Dispatcher):
    # <Start and help message, add user in BD if he isn`t in BD>
    dp.register_message_handler(start_help, commands=["start", "help"])
    dp.register_message_handler(start_help, Text(equals="Помощь", ignore_case=True))

    # <Show products in stock>
    dp.register_message_handler(show_available_products, commands=["products"])
    dp.register_message_handler(show_available_products, Text(equals="Ассортимент", ignore_case=True))
    dp.register_callback_query_handler(show_product, Text(startswith="prod_id:", ignore_case=True))
    dp.register_callback_query_handler(buy_product, Text(startswith="buy_prod_id:", ignore_case=True))

    # <Show products in stock>
    dp.register_message_handler(show_client_info, commands=["balance"])
    dp.register_message_handler(show_client_info, Text(equals="Баланс", ignore_case=True))

    # <Show products in stock>
    dp.register_message_handler(deposit_money, commands=["paid"])
    dp.register_message_handler(deposit_money, Text(equals="Пополнить баланс", ignore_case=True))

    # <Show products in stock>
    dp.register_message_handler(show_my_last_bye, commands=["myBuy"])
    dp.register_message_handler(show_my_last_bye, Text(equals="Мои покупки", ignore_case=True))

