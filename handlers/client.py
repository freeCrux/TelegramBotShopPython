from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text

from Utils import ValueIsNoneException
from keyboards.client_inline_buttons import *
from keyboards.client_keyboard import client_menu_kb
from bot_init import bot, db


async def start_help(message: types.Message):
    db.add_client(client_id=message.from_user.id)
    await bot.send_message(message.from_user.id, "Привет ты попал в магазин выпечки!\n\n"
                                                 "Вы по любым вопросам вы всегда можете обратиться в поддержку "
                                                 "@freecrux\n"
                                                 "В случае проблем с заказом вам понадобиться ваш ИД (/wallet) и ИД "
                                                 "вашего заказа (/myBuy)\n"
                                                 "\nДля покупки вам нужно пополнить счет, введите команду /pay или "
                                                 "выберите в меню пункт [Пополнить баланс]\n\n"
                                                 "Для простотра баланса и общей информации о вас, введите команду "
                                                 "/wallet или"
                                                 "выберите в меню пункт [Баланс]\n\n"
                                                 "Список товараов обновляеться динамически при поступлении нового "
                                                 "товара, для просмтора"
                                                 "товара в наличии введите команду /products или выберите в меню "
                                                 "пункт [Ассортимент]\n\n"
                                                 "Для просмотра последних покупок введите команду "
                                                 "/myBuy или выберите в меню пункт [Мои покупки]",
                           reply_markup=client_menu_kb)


async def show_available_products(message: types.Message):
    products: list = db.get_available_product_list()
    if len(products) > 0:
        await bot.send_message(message.from_user.id, "Весь стафф:\n",
                               reply_markup=get_products_list_inl_kb(products=products))
    else:
        await bot.send_message(message.from_user.id, "К великому сожалению товар закончилю, приходи позже ;)",
                               reply_markup=client_menu_kb)


async def show_product(callback: types.CallbackQuery):
    product_id = int(callback.data.split(':')[1])
    prod_data: tuple = db.get_product_info(prod_id=product_id)
    await bot.send_photo(callback.message.chat.id, prod_data[0],
                         f"Название: {prod_data[1]} | Цена: {prod_data[2]}$\nОписание: {prod_data[3]}",
                         reply_markup=get_buy_inl_kb(prod_id=product_id))


async def show_delivery(client_id: int, delivery_data: tuple):
    product_id: int = delivery_data[0]
    product_name: str = db.get_product_name(prod_id=product_id)
    await bot.send_photo(client_id, delivery_data[1],
                         f"Лот: {product_name} | Адресс: {delivery_data[2]}\n"
                         f"Описание: {delivery_data[3]}",
                         reply_markup=client_menu_kb)


async def buy_product(callback: types.CallbackQuery):
    product_id = int(callback.data.split(':')[1])
    product_price: int = db.get_product_price(prod_id=product_id)
    balance: float = db.get_client_balance(client_id=callback.message.chat.id)
    if db.counter_deliveries_by_product(prod_id=product_id) < 1:
        await callback.message.answer("Увы весь товар закончился.")
        await callback.answer("Товар закончился")
    elif balance >= product_price:
        delivery_id = db.get_id_available_deliver(prod_id=product_id)
        try:
            db.change_client_balance(client_id=callback.message.chat.id, cash=(-1) * product_price)
            db.register_new_sale(buyer_id=callback.message.chat.id, del_id=delivery_id, paid=product_price)
            db.change_available_status_delivery(del_id=delivery_id)
            delivery_data: tuple = db.get_delivers_from_product_id(prod_id=product_id)
            await show_delivery(client_id=callback.message.chat.id, delivery_data=delivery_data)
            await callback.answer("Поздравляю с покупкой")
        except ValueIsNoneException:
            await callback.message.answer("Упс, техническая неполадка. Покупка не состоялась.")
            await callback.answer("Ошибка")

    else:
        await callback.answer("На балансе недостаточно средств")


async def show_client_info(message: types.Message):
    data: tuple = db.get_herself_data_for_client(client_id=message.from_user.id)
    await bot.send_message(message.from_user.id, f"Твой ID: {data[0]}\nБаланс счета: {data[1]}$",
                           reply_markup=client_menu_kb)


async def prepare_deposit_cripto(message: types.Message):
    await bot.send_message(message.from_user.id, "Для пополнения счета нужно выбрать сеть, затем если есть свободный "
                                                 "адрес в этой сети вы сможите отправить на него свои монеты (счет "
                                                 "будет пополнен на столько - сколько вы отправите монет), если есть "
                                                 "вопросы вы можете написать в поддержку.",
                           reply_markup=client_menu_kb)
    await bot.send_message(message.from_user.id, "Выберите сеть для транзакции:",
                           reply_markup=get_address_network_inl_kb())


async def get_available_address_for_deposit_cripto(callback: types.CallbackQuery):
    from bot_init import wallets_processing
    network: str = callback.data.split(":")[-1]
    address: tuple = db.get_available_wallet_address(network=network, customer_id=callback.message.chat.id)
    if address is not None:
        db.set_usage_status_wallet_address(address_id=address[0], customer_id=callback.message.chat.id,
                                           payment_time=wallets_processing.get_payment_time())
        await callback.message.answer(f"У вас есть 30 минту что бы отправить транзакцию в сети {address[4]}"
                                      "Деньги зачисляться на баланс в течении часа.")
        await callback.message.answer(f"{address[1]}", reply_markup=client_menu_kb)
    else:
        await callback.message.answer(f"Сейчас не доступных адресов в этой сети, попробуйте позже или "
                                      f"выбирите другую сеть, сети с которыми мы работаем {AVAILABLE_NETWORK}.",
                                      reply_markup=client_menu_kb)
        await callback.answer()


async def show_sales(message: types.Message):
    sales: list = db.get_sales_from_client_id(client_id=message.from_user.id)
    if len(sales) > 0:
        await bot.send_message(message.from_user.id, "Твои последние покупки:",
                               reply_markup=get_sales_list_inl_kb(sales=sales))
    else:
        await bot.send_message(message.from_user.id, "Вы не совершали покупок!",
                               reply_markup=client_menu_kb)


async def show_sale_from_delivery_id(callback: types.CallbackQuery):
    del_id: int = int(callback.data.split(':')[1])
    delivery_data: tuple = db.get_delivery_info_from_id(del_id=del_id)
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
    dp.register_message_handler(prepare_deposit_cripto, commands=["paid"])
    dp.register_message_handler(prepare_deposit_cripto, Text(equals="Пополнить баланс", ignore_case=True))
    dp.register_callback_query_handler(get_available_address_for_deposit_cripto, Text(startswith="network:",
                                                                                      ignore_case=True))

    # <Show sales>
    dp.register_message_handler(show_sales, commands=["myBuy"])
    dp.register_message_handler(show_sales, Text(equals="Мои покупки", ignore_case=True))
    dp.register_callback_query_handler(show_sale_from_delivery_id, Text(startswith="delivery_id:", ignore_case=True))
