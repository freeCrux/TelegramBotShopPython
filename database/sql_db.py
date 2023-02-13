import sqlite3
from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram.dispatcher.storage import FSMContextProxy

from bot_init import bot

from datetime import datetime


def sql_connect():
    global database, cursor
    database = sqlite3.connect("server.db")
    cursor = database.cursor()

    cursor.execute('CREATE TABLE IF NOT EXISTS client( '
                   'id INTEGER PRIMARY KEY,'
                   'balance INTEGER DEFAULT 0,'
                   'dateOfLastDeposit TEXT DEFAULT "never",'
                   'paymentOfLastDeposit INTEGER DEFAULT 0,'
                   'paid INTEGER DEFAULT 0,'
                   'salesCount INTEGER DEFAULT 0)')

    cursor.execute('CREATE TABLE IF NOT EXISTS product( '
                   'photo TEXT,'
                   'name TEXT,'
                   'price INTEGER,'
                   'description TEXT,'
                   'id INTEGER PRIMARY KEY AUTOINCREMENT)')

    cursor.execute('CREATE TABLE IF NOT EXISTS delivery( '
                   'productId INTEGER,'
                   'photo TEXT,'
                   'adress TEXT,'
                   'description TEXT,'
                   'dateOfAdding TEXT,'
                   'id INTEGER PRIMARY KEY AUTOINCREMENT)')

    cursor.execute('CREATE TABLE IF NOT EXISTS sale( '
                   'id INTEGER PRIMARY KEY AUTOINCREMENT,'
                   'dateSales TEXT,'
                   'idBuyer BIGINT,'
                   'idDelivary INTEGER,'
                   'idProduct INTEGER)')

    database.commit()


# --------------------- #
# Operation on products #
# --------------------- #


async def add_product(prod_data: FSMContextProxy):
    cursor.execute('INSERT INTO product (photo, name, price, description) VALUES (?, ?, ?, ?)',
                   (prod_data["photo"], prod_data["name"], prod_data["price"], prod_data["description"],))
    database.commit()


async def get_available_product_list() -> list:
    """
    :return: products list that have more one delivery
    """
    available_prod = list()
    available_prod_id: list = [pr_id[0] for pr_id in cursor.execute('SELECT productId FROM delivery').fetchall()]
    for pr_id in available_prod_id:
        available_prod += cursor.execute('SELECT * FROM product WHERE id = ?', (pr_id,)).fetchall()

    return available_prod


async def counter_deliveries_by_product(prod_id: int) -> int:
    available_delivery = cursor.execute('SELECT * FROM delivery WHERE productId = ?', (prod_id,)).fetchall()
    return len(available_delivery)


async def get_all_product_list() -> list:
    return cursor.execute('SELECT * FROM product').fetchall()


async def get_product_info(prod_id: int) -> tuple:
    data = cursor.execute('SELECT * FROM product WHERE id = ?', (prod_id,)).fetchone()
    if data is not None:
        return data
    else:
        raise Exception("Product is not exist")


async def get_product_name(prod_id: int) -> str:
    """
    :return: product name if it`s exist else -> product not found
    """
    name = cursor.execute(f'SELECT name FROM product WHERE id = ?', (prod_id,)).fetchone()
    if name is not None:
        return name

    return "Товар не найден"

async def change_product(prod_data: FSMContextProxy):
    cursor.execute('UPDATE product SET (photo, name, price, description) = (?, ?, ?, ?) WHERE id = ?',
                   (prod_data["photo"], prod_data["name"], prod_data["price"],
                    prod_data["description"], prod_data["product_id"],))
    database.commit()


async def delete_product(prod_id: int):
    cursor.execute('DELETE FROM product WHERE id = ?', (prod_id,))
    database.commit()


async def get_product_price(prod_id: int) -> int:
    price: int = cursor.execute('SELECT price FROM product WHERE id = ?', (prod_id,)).fetchone()[0]

    return price


# -------------------- #
# Operation on clients #
# -------------------- #


def add_client_if_not_exist(func):
    async def wrapper(client_id, *args, **kwargs):
        await add_client(client_id)

        return await func(client_id, *args, **kwargs)
    return wrapper


async def add_client(client_id: int):
    client = cursor.execute(f'SELECT id FROM client WHERE id = ?', (client_id,)).fetchone()
    if client is None:
        cursor.execute('INSERT INTO client (id) VALUES (?)', (client_id,))
        database.commit()


@add_client_if_not_exist
async def get_client_balance(client_id: int) -> int:
    balance: int = cursor.execute(f'SELECT balance FROM client WHERE id = ?', (client_id,)).fetchone()[0]

    return balance


@add_client_if_not_exist
async def change_client_balance(client_id: int, cash: int):
    """
    :param cash: Can be positive if client deposit cash and negative if he buys something
    """
    balance: int = cursor.execute(f'SELECT balance FROM client WHERE id = ?', (client_id,)).fetchone()[0]
    if cash > 0 or balance + cash >= 0:
        cursor.execute('UPDATE client SET (balance) = (?) WHERE id = ?', (balance + cash, client_id,))
    else:
        raise Exception("Not enough money to pay")


@add_client_if_not_exist
async def get_client_data(client_id: int) -> tuple:
    data: tuple = cursor.execute(f'SELECT * FROM client WHERE id = ?', (client_id,)).fetchone()

    return data


# --------------------- #
# Operation on delivers #
# --------------------- #


async def add_delivery(state: FSMContext):
    async with state.proxy() as data:
        cursor.execute(
            'INSERT INTO delivery (productId, photo, adress, description, dateOfAdding) VALUES (?, ?, ?, ?, ?)',
            (*[val for val in data.values()], str(datetime.now(),)))
        database.commit()


async def get_delivery_info_from_id(del_id: int) -> tuple:
    return cursor.execute('SELECT * FROM delivery WHERE id = ?', (del_id,)).fetchone()


async def get_delivers_list() -> list:
    return cursor.execute('SELECT * FROM delivery').fetchall()


async def get_delivers_from_product_id(prod_id: int) -> list:
    return cursor.execute('SELECT * FROM delivery WHERE productId = ?', (prod_id,)).fetchall()


async def delete_delivery(del_id: int):
    cursor.execute('DELETE FROM delivery WHERE id = ?', (del_id,))
    database.commit()
