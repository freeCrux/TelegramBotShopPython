from aiogram import executor, types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove, CallbackQuery

from config import admin_login, admin_password, admins_id_list
from bot_init import bot, dp

# <Buttons>
from keyboards.admin_keyboard import (
    admin_menu_kb,
    add_product_kd,
)
from keyboards.admin_inline_buttons import (
    cancel_input_inline_kd,
    get_product_editor_menu_inline_kd,
    get_products_list_inl_kb,
)
from keyboards.client_keyboard import client_menu_kb

from database import sql_db


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


async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await callback.message.answer("Вы отменили добавление нового продукта", reply_markup=admin_menu_kb)
    await callback.answer("Ввод отменен!")


async def cmd_menu(message: types.Message):
    await bot.send_message(message.from_user.id, "Right now u can add a new product", reply_markup=admin_menu_kb)


# ------------------------------------------- #
# Verify, logout and register a user as admin #
# ------------------------------------------- #


def verify(user_id: int) -> bool:
    if user_id in admins_id_list:
        return True
    return False


async def register(message: types.Message, state: FSMContext):
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


async def add_product(message: types.Message):
    await bot.send_message(message.from_user.id,
                           "Вы в режиме добавляения нового товара для отмены нажмите кнопку ниже",
                           reply_markup=cancel_input_inline_kd)
    await ProductStatesGroup.photo.set()
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


async def price_is_invalid(message: types.Message):
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


async def set_description_new_prod(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["description"] = message.text
        if data["product_id"] == -1:
            await sql_db.add_product(state=data)
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
    await bot.send_message(message.from_user.id, "Список всех товаров",
                           reply_markup=await get_products_list_inl_kb(products=all_products))
    await bot.send_message(message.from_user.id, "Вы можете отредактировать товары",
                           reply_markup=admin_menu_kb)


async def redactor_of_product(callback: types.CallbackQuery):
    product_id = int(callback.data.split(':')[1])
    prod_data: tuple = await sql_db.get_product(prod_id=product_id)
    await bot.send_photo(callback.message.chat.id, prod_data[0],
                         f"Название: {prod_data[1]} | Цена: {prod_data[2]}\nОписание: {prod_data[-1]}\n"
                         f"Кол-во доступных доставок: "
                         f"{await sql_db.counter_deliveries_by_product(prod_id=product_id)}",
                         reply_markup=await get_product_editor_menu_inline_kd(prod_id=product_id))


async def edit_product(callback: types.CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split(':')[1])
    prod_data: tuple = await sql_db.get_product(prod_id=product_id)
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


async def delete_product(callback: types.CallbackQuery):
    product_id = int(callback.data.split(':')[1])
    await sql_db.delete_product(prod_id=product_id)
    products = await sql_db.get_all_product_list()
    await callback.message.answer("Товар успешно удален",
                                  reply_markup=await get_products_list_inl_kb(products=products))


# -------- #
# Delivery #
# -------- #


async def add_delivery(message: types.Message):
    await bot.send_message(message.from_user.id,
                           "Вы в режиме добавляения новой доставки для отмены нажмите кнопку ниже",
                           reply_markup=cancel_input_inline_kd)
    await DeliveryStatesGroup.prod_id.set()
    await bot.send_message(message.from_user.id, "Выбирите продукт доставки",
                           reply_markup=ReplyKeyboardRemove())


async def select_product_id_new_delivery(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["prod_id"] = int(message.text)
        print(message.text)
    await DeliveryStatesGroup.next()
    await bot.send_message(message.from_user.id, "Пришлите одно фото места доставки")


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


async def show_delivers(message: types.Message):
    pass


def register_admin_handlers(dp: Dispatcher):
    # <Cancel input when add new product or edit product>
    dp.register_callback_query_handler(cancel_handler, text="cancel_input", state="*")

    # <Show admin menu>
    dp.register_message_handler(cmd_menu, lambda message: verify(message.from_user.id), commands=["admin"])

    # <Register user as admin>
    dp.register_message_handler(register, lambda message: not verify(message.from_user.id),
                                commands=["admin"], state=None)
    dp.register_message_handler(get_login, state=AuthorizationStatesGroup.login)
    dp.register_message_handler(get_password, state=AuthorizationStatesGroup.password)

    # <Logout admin and show user menu>
    dp.register_message_handler(logout, lambda message: verify(message.from_user.id), commands=["logout"])

    # <Add new product or edit existing product>
    dp.register_message_handler(show_all_products, lambda message: verify(message.from_user.id),
                                commands=["show_product"], state=None)
    dp.register_callback_query_handler(redactor_of_product, lambda message: verify(message.from_user.id),
                                       Text(startswith="prod_id_for_redactor:", ignore_case=True), state=None)
    dp.register_callback_query_handler(edit_product, lambda message: verify(message.from_user.id),
                                       Text(startswith="id_product_to_change:", ignore_case=True))
    dp.register_callback_query_handler(delete_product, lambda message: verify(message.from_user.id),
                                       Text(startswith="id_product_ro_delete:", ignore_case=True))

    dp.register_message_handler(add_product, lambda message: verify(message.from_user.id),
                                commands=["add_product"], state=None)
    dp.register_message_handler(set_photo_new_prod, content_types=["photo"], state=ProductStatesGroup.photo)
    dp.register_message_handler(set_name_new_prod, state=ProductStatesGroup.name)
    dp.register_message_handler(price_is_invalid, lambda message: not message.text.isdigit(),
                                state=ProductStatesGroup.price)
    dp.register_message_handler(set_price_new_prod, lambda message: message.text.isdigit(),
                                state=ProductStatesGroup.price)
    dp.register_message_handler(set_description_new_prod, state=ProductStatesGroup.description)

    # <Add new delivery or delete existing delivery>
    dp.register_message_handler(add_delivery, lambda message: verify(message.from_user.id),
                                commands=["add_delivery"], state=None)
    dp.register_message_handler(select_product_id_new_delivery, state=DeliveryStatesGroup.prod_id)
    dp.register_message_handler(set_photo_new_delivery, content_types=["photo"], state=DeliveryStatesGroup.photo)
    dp.register_message_handler(set_address_new_delivery, state=DeliveryStatesGroup.address)
    dp.register_message_handler(set_description_new_delivery, state=DeliveryStatesGroup.description)

