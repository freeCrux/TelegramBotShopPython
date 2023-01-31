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

    # cursor.execute('CREATE TABLE IF NOT EXISTS delivery( '
    #                'photo TEXT,'
    #                'name TEXT PRIMARY KEY,'
    #                'price INTEGER,'
    #                # 'photo BLOB NOT NULL, '
    #                'description TEXT)')
    #
    # cursor.execute('CREATE TABLE IF NOT EXISTS sale( '
    #                'photo TEXT,'
    #                'name TEXT PRIMARY KEY,'
    #                'price INTEGER,'
    #                # 'photo BLOB NOT NULL, '
    #                'description TEXT)')

    database.commit()


async def add_product(state: FSMContext):
    async with state.proxy() as data:
        cursor.execute('INSERT INTO product (photo, name, price, description) VALUES (?, ?, ?, ?)',
                       tuple(data.values()))
        database.commit()


async def get_product_list() -> list:
    return cursor.execute('SELECT * FROM product').fetchall()


async def get_product(prod_id: int) -> tuple:
    return cursor.execute('SELECT * FROM product WHERE id = ?', (prod_id,)).fetchone()


async def add_client(message: types.Message):
    pass
