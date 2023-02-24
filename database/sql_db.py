import sqlite3
from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram.dispatcher.storage import FSMContextProxy

from bot_init import bot

from datetime import datetime

from Utils import ValueIsNoneException
from Utils.wallet import update_currency_rate_satoshi, get_wallet_balance


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
                   'id INTEGER PRIMARY KEY AUTOINCREMENT,'
                   'available BOOLEAN DEFAULT TRUE)')

    cursor.execute('CREATE TABLE IF NOT EXISTS sale( '
                   'id INTEGER PRIMARY KEY AUTOINCREMENT,'
                   'buyerId BIGINT,'
                   'deliveryId INTEGER,'
                   'dateSales TEXT,'
                   'paid INTEGER)')

    cursor.execute('CREATE TABLE IF NOT EXISTS wallet( '
                   'id INTEGER PRIMARY KEY AUTOINCREMENT,'
                   'address TEXT,'
                   'balance TEXT,'
                   'usedUntil TEXT DEFAULT "free",'
                   'network TEXT,'
                   'frozen BOOLEAN DEFAULT FALSE)')

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
    available_prod_id: set = set(
        pr_id[0] for pr_id in cursor.execute('SELECT productId FROM delivery WHERE available = TRUE').fetchall())
    for pr_id in available_prod_id:
        available_prod.append(cursor.execute('SELECT * FROM product WHERE id = ?', (pr_id,)).fetchone())

    return available_prod


async def counter_deliveries_by_product(prod_id: int) -> int:
    available_delivery = cursor.execute('SELECT * FROM delivery WHERE productId = ? AND available = TRUE',
                                        (prod_id,)).fetchall()
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
    name = cursor.execute(f'SELECT name FROM product WHERE id = ?', (prod_id,)).fetchone()[0]
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
    data: tuple = cursor.execute(f'SELECT balance, paid, salesCount  FROM client WHERE id = ?', (client_id,)).fetchone()
    balance: int = data[0]
    paid: int = data[1] + abs(cash) if cash < 0 else data[1]
    sales_count: int = data[5] + 1 if cash < 0 else data[5]
    if cash > 0 or balance + cash >= 0:
        cursor.execute('UPDATE client SET (balance, paid, salesCount) = (?, ?, ?) WHERE id = ?',
                       (balance + cash, paid, sales_count, client_id,))
        database.commit()
    else:
        raise ValueIsNoneException("Not enough money to pay")


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
            (*[val for val in data.values()], str(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),)))
        database.commit()


async def delete_delivery(del_id: int):
    cursor.execute('DELETE FROM delivery WHERE id = ?', (del_id,))
    database.commit()


async def get_delivery_info_from_id(del_id: int) -> tuple:
    data: tuple = cursor.execute('SELECT * FROM delivery WHERE id = ?', (del_id,)).fetchone()
    if data is None:
        raise ValueIsNoneException("Delivery not found")

    return data


async def get_available_delivers_list() -> list:
    return cursor.execute('SELECT * FROM delivery WHERE available = TRUE').fetchall()


async def get_id_available_deliver(prod_id: int) -> int:
    del_id: int = cursor.execute(f'SELECT id FROM delivery WHERE productId = (?) AND available = TRUE',
                                 (prod_id,)).fetchone()[0]
    if del_id is None:
        raise ValueIsNoneException("Not exist available delivery for this product id")

    return del_id


async def get_delivers_from_product_id(prod_id: int) -> tuple:
    return cursor.execute('SELECT * FROM delivery WHERE productId = ?', (prod_id,)).fetchall()[0]


async def change_available_status_delivery(del_id: int):
    cursor.execute('UPDATE delivery SET available = FALSE WHERE id = ?', (del_id,))
    database.commit()


# ------------------ #
# Operation on Sales #
# ------------------ #


async def register_new_sale(buyer_id: int, del_id: int, paid: int):
    cursor.execute('INSERT INTO sale (buyerId, deliveryId, dateSales, paid) VALUES (?, ?, ?, ?)',
                   (buyer_id, del_id, str(datetime.now().strftime("%m/%d/%Y, %H:%M:%S")), paid,))
    database.commit()


async def get_sales_from_client_id(client_id: int) -> list:
    """
    :return: Last 10 sales of client
    """
    sales: list = cursor.execute('SELECT * FROM sale WHERE buyerId = ? ORDER BY id DESC LIMIT 10',
                                 (client_id,)).fetchall()
    return sales


async def get_sale_from_id(sale_id: int) -> tuple:
    data: tuple = cursor.execute('SELECT * FROM sale WHERE id = ?', (sale_id,)).fetchone()
    if data is None:
        raise ValueIsNoneException("Sale not found.")
    return data


# ------------------- #
# Operation on wallet #
# ------------------- #

async def add_new_wallet_address(address: str, network: str):
    wallet_address = cursor.execute(f'SELECT address FROM wallet WHERE address = ?', (address,)).fetchone()
    if wallet_address is None:
        address_balance: int = await get_wallet_balance(address=address)
        # if wallet_balance == -1 then address not found
        if address_balance != -1:
            cursor.execute('INSERT INTO wallet (address, balance, network) VALUES (?, ?, ?)',
                           (address, address_balance, network,))
            database.commit()


async def get_wallet_addresses_list() -> list:
    return cursor.execute('SELECT * FROM wallet').fetchall()


async def get_wallet_address_data(address_id: int) -> tuple:
    return cursor.execute('SELECT * FROM wallet WHERE id = ?', (address_id,)).fetchone()


async def delete_wallet_address(address_id: int):
    cursor.execute('DELETE FROM wallet WHERE id = ?', (address_id,))
    database.commit()


async def change_wallet_address_frozen_status(address_id: int):
    """
    Inverts frozen status of wallet address, True -> False and False -> True.
    """
    frozen_status = cursor.execute('SELECT lock FROM wallet WHERE id = ?', (address_id,)).fetchone()[0]
    if frozen_status is not None:
        frozen_status = True if frozen_status is False else False
        cursor.execute('UPDATE wallet SET (frozen) = (?) WHERE id = ?', (frozen_status, address_id,))
        database.commit()
