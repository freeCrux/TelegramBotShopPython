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

    # cursor.execute('CREATE TABLE IF NOT EXISTS sale( '
    #                'photo TEXT,'
    #                'name TEXT PRIMARY KEY,'
    #                'price INTEGER,'
    #                # 'photo BLOB NOT NULL, '
    #                'description TEXT)')

    database.commit()


# --------------------- #
# Operation on products #
# --------------------- #


async def add_product(prod_data: FSMContextProxy):
    cursor.execute('INSERT INTO product (photo, name, price, description) VALUES (?, ?, ?, ?)',
                   (prod_data["photo"], prod_data["name"], prod_data["price"], prod_data["description"],))
    database.commit()


async def get_available_product_list() -> list:
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
    return cursor.execute('SELECT * FROM product WHERE id = ?', (prod_id,)).fetchone()


async def change_product(prod_data: FSMContextProxy):
    cursor.execute('UPDATE product SET (photo, name, price, description) = (?, ?, ?, ?) WHERE id = ?',
                   (prod_data["photo"], prod_data["name"], prod_data["price"],
                    prod_data["description"], prod_data["product_id"],))
    database.commit()


async def delete_product(prod_id: int):
    cursor.execute('DELETE FROM product WHERE id = ?', (prod_id,))
    database.commit()


# -------------------- #
# Operation on clients #
# -------------------- #


async def add_client(message: types.Message):
    pass


# --------------------- #
# Operation on delivers #
# --------------------- #


async def add_delivery(state: FSMContext):
    async with state.proxy() as data:
        cursor.execute(
            'INSERT INTO delivery (productId, photo, adress, description, dateOfAdding) VALUES (?, ?, ?, ?, ?)',
            (*[val for val in data], str(datetime.now(),)))
        database.commit()


async def get_delivery_info_from_id(del_id: int) -> tuple:
    return cursor.execute('SELECT * FROM product WHERE id = ?', (del_id,)).fetchone()


async def get_delivers_list() -> list:
    return cursor.execute('SELECT * FROM delivery').fetchall()


async def get_delivers_from_product_id(prod_id: int) -> list:
    return cursor.execute('SELECT * FROM delivery WHERE productId = ?', (prod_id,)).fetchall()
