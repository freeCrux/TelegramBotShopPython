from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text

from Utils import ValueIsNoneException
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
                                                 "/myBuy или выберите в меню пункт [Мои покупки]",
                           reply_markup=client_menu_kb)


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


async def show_delivery(client_id: int, delivery_data: tuple):
    product_id: int = delivery_data[0]
    product_name: str = await sql_db.get_product_name(prod_id=product_id)
    await bot.send_photo(client_id, delivery_data[1],
                         f"Лот: {product_name} | Адресс: {delivery_data[2]}\n"
                         f"Описание: {delivery_data[3]}",
                         reply_markup=client_menu_kb)


async def buy_product(callback: types.CallbackQuery):
    product_id = int(callback.data.split(':')[1])
    product_price: int = await sql_db.get_product_price(prod_id=product_id)
    balance: int = await sql_db.get_client_balance(client_id=callback.message.chat.id)
    if await sql_db.counter_deliveries_by_product(prod_id=product_id) < 1:
        await callback.message.answer("Увы весь товар закончился.")
        await callback.answer("Товар закончился")
    elif balance >= product_price:
        delivery_id = await sql_db.get_id_available_deliver(prod_id=product_id)
        try:
            await sql_db.change_client_balance(client_id=callback.message.chat.id, cash=(-1) * product_price)
            await sql_db.register_new_sale(buyer_id=callback.message.chat.id, del_id=delivery_id, paid=product_price)
            await sql_db.change_available_status_delivery(del_id=delivery_id)
            delivery_data: tuple = await sql_db.get_delivers_from_product_id(prod_id=product_id)
            await show_delivery(client_id=callback.message.chat.id, delivery_data=delivery_data)
            await callback.answer("Поздравляю с покупкой")
        except ValueIsNoneException:
            await callback.message.answer("Упс, техническая неполадка. Покупка не состоялась.")
            await callback.answer("Ошибка")

    else:
        await callback.answer("На балансе недостаточно средств")


async def show_client_info(message: types.Message):
    data: tuple = await sql_db.get_client_data(client_id=message.from_user.id)
    await bot.send_message(message.from_user.id, f"Твой ID: {data[0]}\nБаланс счета: {data[1]}$",
                           reply_markup=client_menu_kb)


async def deposit_money(message: types.Message):
    await bot.send_message(message.from_user.id, "deposit", reply_markup=client_menu_kb)


async def show_sales(message: types.Message):
    sales: list = await sql_db.get_sales_from_client_id(client_id=message.from_user.id)
    if len(sales) > 0:
        await bot.send_message(message.from_user.id, "Твои последние покупки:",
                               reply_markup=await get_sales_list_inl_kb(sales=sales))
    else:
        await bot.send_message(message.from_user.id, "Вы не совершали покупок!",
                               reply_markup=client_menu_kb)


async def show_sale_from_delivery_id(callback: types.CallbackQuery):
    del_id: int = int(callback.data.split(':')[1])
    delivery_data: tuple = await sql_db.get_delivery_info_from_id(del_id=del_id)
    await show_delivery(client_id=callback.message.chat.id, delivery_data=delivery_data)
    await callback.answer()


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

    # <Show sales>
    dp.register_message_handler(show_sales, commands=["myBuy"])
    dp.register_message_handler(show_sales, Text(equals="Мои покупки", ignore_case=True))
    dp.register_callback_query_handler(show_sale_from_delivery_id, Text(startswith="delivery_id:", ignore_case=True))
