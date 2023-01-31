from aiogram import executor, types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove, CallbackQuery

from config import admin_login, admin_password, admins_id_list
from bot_init import bot, dp
from keyboards import (
    admin_menu_kb,
    add_product_kd,
    cancel_input_inline_kd,
    client_menu_kb,
)

from database import sql_db


# ----------------------------------- #
# Admin input fields and cancel input #
# ----------------------------------- #


class FSMProduct(StatesGroup):
    photo = State()
    name = State()
    price = State()
    description = State()


class FSMAuthorization(StatesGroup):
    login = State()
    password = State()


class FSMDelivery(StatesGroup):
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
    await FSMAuthorization.login.set()
    await bot.send_message(message.from_user.id, "Send login")


async def get_login(message: types.Message, state: FSMContext):
    if message.text == admin_login:
        await FSMAuthorization.password.set()
        await bot.send_message(message.from_user.id, "Send password")
    else:
        await bot.send_message(message.from_user.id, "Wrong login")
        await state.finish()
    await bot.delete_message(message.chat.id, message.message_id)


async def get_password(message: types.Message, state: FSMContext):
    if message.text == admin_password:
        admins_id_list.append(message.from_user.id)
        await bot.send_message(message.from_user.id, "U are admin", reply_markup=admin_menu_kb)
    else:
        await bot.send_message(message.from_user.id, "Wrong password")
    await state.finish()
    await bot.delete_message(message.chat.id, message.message_id)


async def logout(message: types.Message):
    admins_id_list.pop(admins_id_list.index(message.from_user.id))
    await bot.send_message(message.from_user.id, "Now u are not admin", reply_markup=client_menu_kb)


# ------- #
# Product #
# ------- #


async def add_product(message: types.Message):
    await bot.send_message(message.from_user.id,
                           "Вы в режиме добавляения нового товара для отмены нажмите кнопку ниже",
                           reply_markup=cancel_input_inline_kd)
    await FSMProduct.photo.set()
    await bot.send_message(message.from_user.id, "Send the photo of new product",
                           reply_markup=ReplyKeyboardRemove())


async def set_photo_new_prod(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["photo"] = message.photo[0].file_id
    await FSMProduct.next()
    await bot.send_message(message.from_user.id, "Write the name")


async def set_name_new_prod(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["name"] = message.text
    await FSMProduct.next()
    await bot.send_message(message.from_user.id, "Write the price")


async def price_is_invalid(message: types.Message):
    return await message.reply("Price gotta be a digits only (for example: 150)")


async def set_price_new_prod(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["price"] = int(message.text)
    await FSMProduct.next()
    await bot.send_message(message.from_user.id, "Set the description")


async def set_description_new_prod(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["description"] = message.text

    await bot.send_message(message.from_user.id, "New product added", reply_markup=admin_menu_kb)
    await sql_db.add_product(state=state)
    await state.finish()


# -------- #
# Delivery #
# -------- #


async def add_delivery(message: types.Message):
    await bot.send_message(message.from_user.id,
                           "Вы в режиме добавляения новой доставки для отмены нажмите кнопку ниже",
                           reply_markup=cancel_input_inline_kd)
    await FSMDelivery.prod_id.set()
    await bot.send_message(message.from_user.id, "Выбирите продукт доставки",
                           reply_markup=ReplyKeyboardRemove())


async def select_product_id_new_delivery(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["prod_id"] = int(message.text)
        print(message.text)
    await FSMDelivery.next()
    await bot.send_message(message.from_user.id, "Пришлите одно фото места доставки")


async def set_photo_new_delivery(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["photo"] = message.photo[0].file_id
    await FSMDelivery.next()
    await bot.send_message(message.from_user.id, "Пришлите адресс (Пример: 12331.123.123123) ")


async def set_address_new_delivery(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["address"] = message.text
    await FSMDelivery.next()
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
    # <Cancel input new product>
    dp.register_callback_query_handler(cancel_handler, text="cancel_input", state="*")

    # <Show admin menu>
    dp.register_message_handler(cmd_menu, lambda message: verify(message.from_user.id), commands=["admin"])

    # <Register>
    dp.register_message_handler(register, lambda message: not verify(message.from_user.id),
                                commands=["admin"], state=None)
    dp.register_message_handler(get_login, state=FSMAuthorization.login)
    dp.register_message_handler(get_password, state=FSMAuthorization.password)

    # <Logout admin and show user menu>
    dp.register_message_handler(logout, lambda message: verify(message.from_user.id), commands=["logout"])

    # <Add new product>
    dp.register_message_handler(add_product, lambda message: verify(message.from_user.id),
                                commands=["add_product"], state=None)
    dp.register_message_handler(set_photo_new_prod, content_types=["photo"], state=FSMProduct.photo)
    dp.register_message_handler(set_name_new_prod, state=FSMProduct.name)
    dp.register_message_handler(price_is_invalid, lambda message: not message.text.isdigit(), state=FSMProduct.price)
    dp.register_message_handler(set_price_new_prod, lambda message: message.text.isdigit(), state=FSMProduct.price)
    dp.register_message_handler(set_description_new_prod, state=FSMProduct.description)

    # <Add new delivery>
    dp.register_message_handler(add_delivery, lambda message: verify(message.from_user.id),
                                commands=["add_delivery"], state=None)
    dp.register_message_handler(select_product_id_new_delivery, state=FSMDelivery.prod_id)
    dp.register_message_handler(set_photo_new_delivery, content_types=["photo"], state=FSMDelivery.photo)
    dp.register_message_handler(set_address_new_delivery, state=FSMDelivery.address)
    dp.register_message_handler(set_description_new_delivery, state=FSMDelivery.description)

    # <Show all delivery>
