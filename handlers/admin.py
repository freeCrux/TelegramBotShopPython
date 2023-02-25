from aiogram import executor, types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove, CallbackQuery

from Utils.wallet import update_wallet_balance
from config import (available_network,
                    admin_login,
                    admin_password,
                    admins_id_list)
from bot_init import bot, dp

# <Buttons>
from keyboards.admin_keyboard import admin_menu_kb
from keyboards.admin_inline_buttons import *
from keyboards.client_keyboard import client_menu_kb
from keyboards.client_inline_buttons import get_sales_list_inl_kb

from database import sql_db

# from Utils.CustomFilter import AdminFilter


from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from config import admins_id_list

NAME_LIMIT_SIZE = 64
PRICE_LIMIT_SIZE = 6
DESCRIPTION_LIMIT_SIZE = 960 - NAME_LIMIT_SIZE - PRICE_LIMIT_SIZE


# -------------------------------- #
# Custom admin filter for handlers #
# -------------------------------- #


class AdminFilter(BoundFilter):
    key = 'is_admin'

    def __init__(self):
        pass

    async def check(self, message: types.Message) -> bool:
        user_id = message.from_user.id
        if user_id in admins_id_list:
            return True
        return False


# ----------------------------------- #
# Admin input fields and cancel input #
# ----------------------------------- #


class ProductStatesGroup(StatesGroup):
    product_id = State()
    photo = State()
    name = State()
    price = State()
    description = State()


class AuthorizationStatesGroup(StatesGroup):
    login = State()
    password = State()


class DeliveryStatesGroup(StatesGroup):
    prod_id = State()
    photo = State()
    address = State()
    description = State()


class ClientStatesGroup(StatesGroup):
    client_id = State()


class WalletAddressGroup(StatesGroup):
    address = State()
    network = State()


async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await callback.message.answer("Вы отменили ввод", reply_markup=admin_menu_kb)
    await callback.answer("Ввод отменен!")


async def cmd_menu(message: types.Message):
    await bot.send_message(message.from_user.id, "Ты Админ можешь действовать.", reply_markup=admin_menu_kb)


# ----------------------------------- #
# Logout and register a user as admin #
# ----------------------------------- #


async def register(message: types.Message):
    await AuthorizationStatesGroup.login.set()
    await bot.send_message(message.from_user.id, "Введи логин от аккаунта большого босса - админа")


async def get_login(message: types.Message, state: FSMContext):
    if message.text == admin_login:
        await AuthorizationStatesGroup.password.set()
        await bot.send_message(message.from_user.id, "Попытай свою удачю, введи пароль")
    else:
        await bot.send_message(message.from_user.id, "Кого ты пытаешься обнамуть по просто работяга, неверный логин")
        await state.finish()
    await bot.delete_message(message.chat.id, message.message_id)


async def get_password(message: types.Message, state: FSMContext):
    if message.text == admin_password:
        admins_id_list.append(message.from_user.id)
        await bot.send_message(message.from_user.id,
                               "Внимание! Ты стал биг боссом - админом. Теперь разрешаю наворотить дел!",
                               reply_markup=admin_menu_kb)
    else:
        await bot.send_message(message.from_user.id, "Не растраивайся! Попытай удачу позже!")
    await state.finish()
    await bot.delete_message(message.chat.id, message.message_id)


async def logout(message: types.Message):
    admins_id_list.pop(admins_id_list.index(message.from_user.id))
    await bot.send_message(message.from_user.id, "Вы покинули пост администратора", reply_markup=client_menu_kb)


# ------- #
# Product #
# ------- #


async def add_product(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id,
                           "Вы в режиме добавляения нового товара для отмены нажмите кнопку ниже",
                           reply_markup=cancel_input_inline_kd)
    await ProductStatesGroup.photo.set()
    async with state.proxy() as data:
        # -1 if prod is not exist
        data["product_id"] = -1
    await bot.send_message(message.from_user.id, "Пришлите одно фото для нового товара",
                           reply_markup=ReplyKeyboardRemove())


async def set_photo_new_prod(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["photo"] = message.photo[0].file_id
        if data["product_id"] == -1:
            await bot.send_message(message.from_user.id, "Напишите имя нового товара")
        else:
            await bot.send_message(message.from_user.id,
                                   "Eсли хотите оставить cтарое имя товара скопируейти его и пришлите новым сообщением")
            await bot.send_message(message.from_user.id, data["name"])
    await ProductStatesGroup.next()


async def set_name_new_prod(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["name"] = message.text
        if data["product_id"] != -1:
            await bot.send_message(message.from_user.id, f"Старая цена: {data['price']}$")
    await ProductStatesGroup.next()
    await bot.send_message(message.from_user.id, "Укажите цену товара")


async def processing_invalid_price(message: types.Message):
    return await message.reply("Бро что за дела! Цена должна быть только в цифрах (Пример: 65)")


async def set_price_new_prod(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["price"] = int(message.text)
        if data["product_id"] == -1:
            await bot.send_message(message.from_user.id, "Напишите описание нового товара")
        else:
            await bot.send_message(message.from_user.id,
                                   "Eсли хотите оставить cтарое описание "
                                   "товара скопируейти его и пришлите новым сообщением")
            await bot.send_message(message.from_user.id, data["description"])
    await ProductStatesGroup.next()


async def processing_too_long_message(message: types.Message):
    return await message.reply(f"Дорогой куда разогнался, слишком много символов")


async def set_description_new_prod(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["description"] = message.text
        if data["product_id"] == -1:
            await sql_db.add_product(prod_data=data)
            await bot.send_message(message.from_user.id, "Новый товар добавлен", reply_markup=admin_menu_kb)
        else:
            await sql_db.change_product(prod_data=data)
            await bot.send_message(message.from_user.id, "Товар успешно изменен", reply_markup=ReplyKeyboardRemove())
            await bot.send_photo(message.from_user.id, data['photo'],
                                 f"Название: {data['name']} | Цена: {data['price']}\nОписание: {data['description']}",
                                 reply_markup=admin_menu_kb)
    await state.finish()


async def show_all_products(message: types.Message):
    all_products = await sql_db.get_all_product_list()
    if len(all_products) > 0:
        await bot.send_message(message.from_user.id, "Список всех товаров",
                               reply_markup=await get_products_list_inl_kb_root(
                                   products=all_products, mode="prod_id_for_redactor"))
        await bot.send_message(message.from_user.id, "Вы можете отредактировать товары",
                               reply_markup=admin_menu_kb)
    else:
        await bot.send_message(message.from_user.id, "Нет ни одного товара, но вы можете добавить новый товар командой"
                                                     "/add_product",
                               reply_markup=admin_menu_kb)


async def redactor_of_product(callback: types.CallbackQuery):
    product_id = int(callback.data.split(':')[1])
    prod_data: tuple = await sql_db.get_product_info(prod_id=product_id)
    await bot.send_photo(callback.message.chat.id, prod_data[0],
                         f"Название: {prod_data[1]} | ID: {product_id} | Цена: {prod_data[2]}$\n"
                         f"Кол-во доступных доставок: {await sql_db.counter_deliveries_by_product(prod_id=product_id)}"
                         f"\nОписание: {prod_data[3]}",
                         reply_markup=await get_product_editor_menu_inline_kd_root(prod_id=product_id))
    await callback.answer("Можете редактировать товар")


async def edit_product(callback: types.CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split(':')[1])
    prod_data: tuple = await sql_db.get_product_info(prod_id=product_id)
    await ProductStatesGroup.photo.set()
    async with state.proxy() as data:
        data["product_id"] = product_id
        data["photo"] = prod_data[0]
        data["name"] = prod_data[1]
        data["price"] = prod_data[2]
        data["description"] = prod_data[3]
    await callback.message.answer("Вы в режиме редактирования товара для отмены нажмите кнопку ниже",
                                  reply_markup=cancel_input_inline_kd)
    await bot.send_photo(callback.message.chat.id, prod_data[0],
                         "Старое фото товара если вы хотите оставть его перешлите это сообщение сюда",
                         reply_markup=ReplyKeyboardRemove())
    await callback.answer("Товар в режиме редактирования")


async def delete_product(callback: types.CallbackQuery):
    product_id = int(callback.data.split(':')[1])
    await sql_db.delete_product(prod_id=product_id)
    products = await sql_db.get_all_product_list()
    await callback.message.answer("Товар успешно удален",
                                  reply_markup=await get_products_list_inl_kb_root(
                                      products=products, mode="prod_id_for_redactor"))
    await callback.answer("Продукт удален")


# -------- #
# Delivery #
# -------- #


async def add_delivery(message: types.Message):
    await bot.send_message(message.from_user.id,
                           "Вы в режиме добавляения новой доставки для отмены нажмите кнопку ниже",
                           reply_markup=cancel_input_inline_kd)
    products = await sql_db.get_all_product_list()
    await bot.send_message(message.from_user.id, "Выберите лот который вы доставили",
                           reply_markup=await get_products_list_inl_kb_root(products=products,
                                                                            mode="prod_id_for_delivery"))
    await DeliveryStatesGroup.prod_id.set()


async def select_product_id_new_delivery(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        product_id = int(callback.data.split(':')[1])
        data["prod_id"] = product_id
    await DeliveryStatesGroup.next()
    await callback.message.answer("Пришлите одно фото места доставки",
                                  reply_markup=ReplyKeyboardRemove())
    await callback.answer()


async def set_photo_new_delivery(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["photo"] = message.photo[0].file_id
    await DeliveryStatesGroup.next()
    await bot.send_message(message.from_user.id, "Пришлите адресс (Пример: 12331.123.123123) ")


async def set_address_new_delivery(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["address"] = message.text
    await DeliveryStatesGroup.next()
    await bot.send_message(message.from_user.id, "Оставьте описание для доставки ")


async def set_description_new_delivery(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["description"] = message.text

    await bot.send_message(message.from_user.id, "Доставка оформлена", reply_markup=admin_menu_kb)
    await sql_db.add_delivery(state=state)
    await state.finish()


async def show_list_of_delivers(message: types.Message):
    all_delivers = await sql_db.get_available_delivers_list()
    if len(all_delivers) > 0:
        await bot.send_message(message.from_user.id, "Список доставок",
                               reply_markup=await get_delivers_list_inl_kb_root(all_delivers))
        await bot.send_message(message.from_user.id, "Можете полюбоваться проделанной работой!\n"
                                                     "Мы тут все серьезнае люди так что изменить доставку низя, "
                                                     "можешь только удалить.",
                               reply_markup=admin_menu_kb)
    else:
        await bot.send_message(message.from_user.id, "Нет ни одной доставки, но вы можете загяться делом ;)"
                                                     "/add_delivery",
                               reply_markup=admin_menu_kb)


async def show_delivery(callback: types.CallbackQuery):
    delivery_id = int(callback.data.split(':')[1])
    delivery_data: tuple = await sql_db.get_delivery_info_from_id(del_id=delivery_id)
    product_id_for_delivery: int = delivery_data[0]
    product_name: str = await sql_db.get_product_name(prod_id=product_id_for_delivery)
    await bot.send_photo(callback.message.chat.id, delivery_data[1],
                         f"Лот: {product_name}\nID доствки: {delivery_id}"
                         f"\nАдресс: {delivery_data[2]}\nВремя добавления: {delivery_data[4]}\n"
                         f"Описание: {delivery_data[3]}",
                         reply_markup=await get_delivery_editor_menu_inline_kd_root(del_id=delivery_id))
    await callback.answer("Просмотр доставки")


async def delete_delivery(callback: types.CallbackQuery):
    delivery_id = int(callback.data.split(':')[1])
    await sql_db.delete_delivery(del_id=delivery_id)
    delivers = await sql_db.get_available_delivers_list()
    await callback.message.answer("Доствка успешна удалена",
                                  reply_markup=await get_delivers_list_inl_kb_root(
                                      delivers=delivers))
    await callback.answer("Дело сделано")


# ------ #
# Client #
# ------ #


async def request_client_info(message: types.Message):
    await bot.send_message(message.from_user.id, "Пришлите ID пользователя. Если передумал нажми отмена!",
                           reply_markup=cancel_input_inline_kd)
    await ClientStatesGroup.client_id.set()


async def show_client_info(message: types.Message, state: FSMContext):
    client_id = int(message.text)
    client_data: tuple = await sql_db.get_client_data_for_admin(client_id=client_id)
    if client_data is not None:
        sales = await sql_db.get_sales_from_client_id(client_id=client_id)
        await bot.send_message(message.from_user.id, f"ID: {client_data[0]} | "
                                                     f"Баланс: {client_data[1]}$\n"
                                                     f"Дата последнего депозита: {client_data[2]} | "
                                                     f"Последний депозит: {client_data[3]}$\n"
                                                     f"Общее кол-во сделок: {client_data[5]} | "
                                                     f"Потратил: {client_data[4]}$\n\n"
                                                     f"Последние заказы:",
                               reply_markup=await get_sales_list_inl_kb_root(sales=sales))
    else:
        await bot.send_message(message.from_user.id, "Данный пользователь не найден.")
    await bot.send_message(message.from_user.id, "Можете подробнее узнать о сделках с клиентом",
                           reply_markup=admin_menu_kb)
    await state.finish()


async def show_sale_full_info(callback: types.CallbackQuery):
    sale_id = int(callback.data.split(':')[1])
    sale_data: tuple = await sql_db.get_sale_from_id(sale_id=sale_id)

    delivery_id: int = sale_data[2]
    delivery_data: tuple = await sql_db.get_delivery_info_from_id(del_id=delivery_id)

    product_id: int = delivery_data[0]
    product_name: str = await sql_db.get_product_name(prod_id=product_id)
    await callback.message.answer(f"Данные о сделке:\nID: {sale_id}\nДата совершения: {sale_data[3]}\n"
                                  f"Заплачено: {sale_data[4]}$\n"
                                  f"ID клиента: {sale_data[1]}",
                                  reply_markup=ReplyKeyboardRemove())
    await bot.send_photo(callback.message.chat.id, delivery_data[1],
                         f"Лот: {product_name} | ID доствки: {delivery_id}"
                         f"\nАдресс: {delivery_data[2]}\nВремя добавления: {delivery_data[4]}\n"
                         f"Описание: {delivery_data[3]}",
                         reply_markup=admin_menu_kb)
    await callback.answer()


# ------ #
# Wallet #
# ------ #


async def add_wallet_address(message: types.Message):
    await bot.send_message(message.from_user.id,
                           "Вы в режиме добавляения нового адреса для отмены нажмите кнопку ниже",
                           reply_markup=cancel_input_inline_kd)
    await WalletAddressGroup.address.set()
    await bot.send_message(message.from_user.id, "Пришлите адрес кошелька, все его данные подтянутся автоматически.",
                           reply_markup=ReplyKeyboardRemove())


async def set_address_for_new_wallet_address(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["address"] = message.text
        await bot.send_message(message.from_user.id, f"Укажите сеть например: BTC",
                               reply_markup=ReplyKeyboardRemove())
    await WalletAddressGroup.next()


async def processing_invalid_address_network(message: types.Message):
    return await message.reply(f"Бро такие сети мы не знаем! Вот те с которыми работаем {available_network}")


async def set_network_for_new_wallet_address(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["network"] = message.text
        address_balance: int = await update_wallet_balance(address=data["address"])
        # if wallet_balance == -1 then address not found
        if address_balance != -1:
            await sql_db.add_new_wallet_address(address=data["address"],
                                                network=data["network"], balance=address_balance)
            await bot.send_message(message.from_user.id,
                                   f"\t\tУспешно добавлен!\n\nСеть: {data['network']} Адрес {data['address']}",
                                   reply_markup=admin_menu_kb)
        else:
            await bot.send_message(message.from_user.id, "Такой адрес не существует, попробуйте снова /add_address",
                                   reply_markup=admin_menu_kb)
    await state.finish()


async def show_list_of_wallet_address(message: types.Message):
    addresses = await sql_db.get_wallet_all_addresses_list()
    if len(addresses) > 0:
        await bot.send_message(message.from_user.id, "Список адрессов:",
                               reply_markup=await get_wallet_address_list_inl_kb_root(addresses=addresses))
        await bot.send_message(message.from_user.id, "Для вывода средств с адреса ДОЛЖНЫ его заморозить если он занят"
                                                     "заморозьте его и подождите пока он станет свободный "
                                                     "(на него придет транзакция от покупателя), "
                                                     "для удаления адреса производите ту же операцию.",
                               reply_markup=admin_menu_kb)
    else:
        await bot.send_message(message.from_user.id, "Нет ни одного адреса, но вы можете загяться делом ;)"
                                                     "/add_wallet_address",
                               reply_markup=admin_menu_kb)


async def edit_menu_of_address(callback: types.CallbackQuery):
    address_id = int(callback.data.split(':')[1])
    address: tuple = await sql_db.get_wallet_address_data(address_id=address_id)
    await callback.message.answer(f"АДРЕС: {address[1]}\nИД: {address_id} | Баланс: {address[2]} | Сеть: {address[4]}\n"
                                  f"Используеться до: {address[3]} | Заморожен: {address[5]}",
                                  reply_markup=await get_wallet_address_editor_menu_inline_kd_root(
                                      address_id=address_id))
    await callback.answer()


async def delete_wallet_address(callback: types.CallbackQuery):
    address_id = int(callback.data.split(':')[1])
    await sql_db.delete_wallet_address(address_id=address_id)
    await callback.answer("Адрес удален!")


async def block_or_unblock_wallet_address(callback: types.CallbackQuery):
    """
    If wallet address is blocked then the address don`t use for payments, this is use for withdrawal of money.
    """
    address_id = int(callback.data.split(':')[1])
    address_data: tuple = await sql_db.get_wallet_address_data(address_id=address_id)
    if address_data is not None:
        wallet_address = address_data[1]
        address_balance: int = await update_wallet_balance(address=wallet_address)
        await sql_db.change_wallet_address_frozen_status(address_id=address_id, balance=address_balance)
        await callback.answer("Адрес заморожен!")
    else:
        await callback.answer("Ошибка адрес не найден!")


def register_admin_action(dp: Dispatcher):
    # <Show admin menu>
    dp.register_message_handler(cmd_menu, AdminFilter(), commands=["admin"])
    # <Register user as admin>
    dp.register_message_handler(register, commands=["admin"], state=None)
    dp.register_message_handler(get_login, state=AuthorizationStatesGroup.login)
    dp.register_message_handler(get_password, state=AuthorizationStatesGroup.password)
    # <Logout admin and show user menu>
    dp.register_message_handler(logout, AdminFilter(), commands=["logout"])


def register_action_for_product(dp: Dispatcher):
    dp.register_message_handler(show_all_products, AdminFilter(), commands=["show_product"], state=None)

    dp.register_callback_query_handler(redactor_of_product, AdminFilter(),
                                       Text(startswith="prod_id_for_redactor:", ignore_case=True), state=None)
    dp.register_callback_query_handler(edit_product, AdminFilter(), Text(startswith="id_product_to_change:",
                                                                         ignore_case=True))
    dp.register_callback_query_handler(delete_product, AdminFilter(), Text(startswith="id_product_to_delete:",
                                                                           ignore_case=True))
    # <Add photo>
    dp.register_message_handler(add_product, AdminFilter(), commands=["add_product"], state=None)
    dp.register_message_handler(set_photo_new_prod, content_types=["photo"], state=ProductStatesGroup.photo)
    # <Set name>
    dp.register_message_handler(processing_too_long_message,
                                lambda message: len(message.text) > NAME_LIMIT_SIZE, state=ProductStatesGroup.price)
    dp.register_message_handler(set_name_new_prod, state=ProductStatesGroup.name)
    # <Set price>
    dp.register_message_handler(processing_invalid_price,
                                lambda message: not message.text.isdigit() or int(message.text) > 9999,
                                state=ProductStatesGroup.price)
    dp.register_message_handler(set_price_new_prod, lambda message: message.text.isdigit(),
                                state=ProductStatesGroup.price)
    # <Set description>
    dp.register_message_handler(processing_too_long_message, lambda message: len(message.text) > DESCRIPTION_LIMIT_SIZE,
                                state=ProductStatesGroup.description)
    dp.register_message_handler(set_description_new_prod, state=ProductStatesGroup.description)


def register_action_for_delivery(dp: Dispatcher):
    dp.register_message_handler(show_list_of_delivers, AdminFilter(), commands=["show_delivery"])
    dp.register_callback_query_handler(show_delivery, AdminFilter(),
                                       Text(startswith="delivery_id_root:", ignore_case=True))
    dp.register_callback_query_handler(delete_delivery, AdminFilter(),
                                       Text(startswith="id_delivery_to_delete:", ignore_case=True))
    dp.register_message_handler(add_delivery, AdminFilter(), commands=["add_delivery"], state=None)
    dp.register_callback_query_handler(select_product_id_new_delivery, AdminFilter(),
                                       Text(startswith="prod_id_for_delivery:", ignore_case=True),
                                       state=DeliveryStatesGroup.prod_id)
    dp.register_message_handler(set_photo_new_delivery, content_types=["photo"], state=DeliveryStatesGroup.photo)
    dp.register_message_handler(processing_too_long_message,
                                lambda message: len(message.text) > NAME_LIMIT_SIZE, state=DeliveryStatesGroup.address)
    dp.register_message_handler(set_address_new_delivery, state=DeliveryStatesGroup.address)
    dp.register_message_handler(processing_too_long_message,
                                lambda message: len(message.text) > DESCRIPTION_LIMIT_SIZE,
                                state=DeliveryStatesGroup.description)
    dp.register_message_handler(set_description_new_delivery, state=DeliveryStatesGroup.description)


def register_action_for_client(dp: Dispatcher):
    dp.register_message_handler(request_client_info, AdminFilter(), commands=["client_info"], state=None)
    dp.register_message_handler(show_client_info, state=ClientStatesGroup.client_id)
    dp.register_callback_query_handler(show_sale_full_info, AdminFilter(), Text(startswith="sale_id:",
                                                                                ignore_case=True))


def register_action_for_wallet_address(dp: Dispatcher):
    dp.register_message_handler(add_wallet_address, AdminFilter(), commands=["add_address"], state=None)
    dp.register_message_handler(set_address_for_new_wallet_address, state=WalletAddressGroup.address)
    dp.register_message_handler(processing_invalid_address_network,
                                lambda message: message.text not in available_network, state=WalletAddressGroup.network)
    dp.register_message_handler(set_network_for_new_wallet_address, state=WalletAddressGroup.network)
    dp.register_message_handler(show_list_of_wallet_address, AdminFilter(), commands=["show_addresses"])
    dp.register_callback_query_handler(edit_menu_of_address, AdminFilter(), Text(startswith="address_id:",
                                                                                 ignore_case=True))
    dp.register_callback_query_handler(delete_wallet_address, AdminFilter(), Text(startswith="id_address_to_delete:",
                                                                                  ignore_case=True))
    dp.register_callback_query_handler(block_or_unblock_wallet_address, AdminFilter(),
                                       Text(startswith="id_address_to_freeze:", ignore_case=True))


def register_admin_handlers(dp: Dispatcher):
    # <Cancel input when add new product or edit product>
    dp.register_callback_query_handler(cancel_handler, text="cancel_input", state="*")
    register_admin_action(dp=dp)
    register_action_for_product(dp=dp)
    register_action_for_delivery(dp=dp)
    register_action_for_client(dp=dp)
    register_action_for_wallet_address(dp=dp)
