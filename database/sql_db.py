import sqlite3
from aiogram.dispatcher import FSMContext
from aiogram import types
from bot_init import bot


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


async def add_product(state: FSMContext):
    async with state.proxy() as data:
        cursor.execute('INSERT INTO product (photo, name, price, description) VALUES (?, ?, ?, ?)',
                       tuple(data.values()))
        database.commit()


async def get_available_product_list() -> list:
    available_prod = list()
    available_prod_id: list = [pr_id[0] for pr_id in cursor.execute('SELECT productId FROM delivery').fetchall()]
    for pr_id in available_prod_id:
        available_prod += cursor.execute('SELECT * FROM product WHERE id = ?', (pr_id,)).fetchall()

    return available_prod


async def get_all_product_list() -> list:
    return cursor.execute('SELECT * FROM product').fetchall()


async def get_product(prod_id: int) -> tuple:
    return cursor.execute('SELECT * FROM product WHERE id = ?', (prod_id,)).fetchone()


# -------------------- #
# Operation on clients #
# -------------------- #


async def add_client():
    pass


# --------------------- #
# Operation on delivers #
# --------------------- #


async def add_delivery(state: FSMContext):
    async with state.proxy() as data:
        cursor.execute('INSERT INTO delivery (productId, photo, adress, description) VALUES (?, ?, ?, ?)',
                       tuple(data.values()))
        database.commit()


async def get_delivers_list() -> list:
    return cursor.execute('SELECT * FROM delivery').fetchall()


async def get_delivers_from_product_id(prod_id: int) -> list:
    return cursor.execute('SELECT * FROM delivery WHERE productId = ?', (prod_id,)).fetchall()
