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
                   'name TEXT PRIMARY KEY,'
                   'price INTEGER,'
                   'description TEXT)')

    cursor.execute('CREATE TABLE IF NOT EXISTS delivery( '
                   'photo TEXT,'
                   'name TEXT PRIMARY KEY,'
                   'price INTEGER,'
                   # 'photo BLOB NOT NULL, '
                   'description TEXT)')

    cursor.execute('CREATE TABLE IF NOT EXISTS sale( '
                   'photo TEXT,'
                   'name TEXT PRIMARY KEY,'
                   'price INTEGER,'
                   # 'photo BLOB NOT NULL, '
                   'description TEXT)')

    database.commit()


async def add_product(state: FSMContext):
    async with state.proxy() as data:
        cursor.execute('INSERT INTO product VALUES (?, ?, ?, ?)', tuple(data.values()))
        database.commit()


async def get_all_product(message: types.Message):
    for pr in cursor.execute('SELECT * FROM product').fetchall():
        await bot.send_photo(message.from_user.id, pr[0], f"Name: {pr[1]} | Price: {pr[2]}\nDescription: {pr[-1]}")


async def add_client(message: types.Message):
    pass
