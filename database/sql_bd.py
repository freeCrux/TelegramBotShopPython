import sqlite3
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.storage import FSMContextProxy
from datetime import datetime
import datetime

from Utils import ValueIsNoneException


class DataBase:
    def __init__(self, path: str):
        self._database = sqlite3.connect(path)
        self._cursor = self._database.cursor()

        self._cursor.execute('CREATE TABLE IF NOT EXISTS client( '
                             'id BIGINT PRIMARY KEY,'
                             'balance REAL DEFAULT 0,'
                             'dateOfLastDeposit TEXT DEFAULT "never",'
                             'paymentOfLastDeposit INTEGER DEFAULT 0,'
                             'paid REAL DEFAULT 0,'
                             'salesCount INTEGER DEFAULT 0)')

        self._cursor.execute('CREATE TABLE IF NOT EXISTS product( '
                             'photo TEXT,'
                             'name TEXT,'
                             'price INTEGER,'
                             'description TEXT,'
                             'id INTEGER PRIMARY KEY AUTOINCREMENT)')

        self._cursor.execute('CREATE TABLE IF NOT EXISTS delivery( '
                             'productId INTEGER,'
                             'photo TEXT,'
                             'adress TEXT,'
                             'description TEXT,'
                             'dateOfAdding TEXT,'
                             'id INTEGER PRIMARY KEY AUTOINCREMENT,'
                             'available BOOLEAN DEFAULT TRUE)')

        self._cursor.execute('CREATE TABLE IF NOT EXISTS sale( '
                             'id INTEGER PRIMARY KEY AUTOINCREMENT,'
                             'buyerId BIGINT,'
                             'deliveryId INTEGER,'
                             'dateSales TEXT,'
                             'paid INTEGER)')

        self._cursor.execute('CREATE TABLE IF NOT EXISTS wallet( '
                             'id INTEGER PRIMARY KEY AUTOINCREMENT,'
                             'address TEXT,'
                             'balance REAL DEFAULT 0,'
                             'usedUntil TEXT DEFAULT "free",'
                             'network TEXT,'
                             'frozen BOOLEAN DEFAULT FALSE,'
                             'idClientForWait BIGINT DEFAULT -1)')

        self._database.commit()

    def sql_close(self):
        self._database.close()

    # --------------------- #
    # Operation on products #
    # --------------------- #

    def add_product(self, prod_data: FSMContextProxy):
        self._cursor.execute('INSERT INTO product (photo, name, price, description) VALUES (?, ?, ?, ?)',
                             (prod_data["photo"], prod_data["name"], prod_data["price"], prod_data["description"],))
        self._database.commit()

    def get_available_product_list(self) -> list:
        """
        :return: products list that have more one delivery
        """
        available_prod = list()
        available_prod_id: set = set(
            pr_id[0] for pr_id in
            self._cursor.execute('SELECT productId FROM delivery WHERE available = TRUE').fetchall())
        for pr_id in available_prod_id:
            available_prod.append(self._cursor.execute('SELECT * FROM product WHERE id = ?', (pr_id,)).fetchone())

        return available_prod

    def counter_deliveries_by_product(self, prod_id: int) -> int:
        available_delivery = self._cursor.execute('SELECT * FROM delivery WHERE productId = ? AND available = TRUE',
                                                  (prod_id,)).fetchall()
        return len(available_delivery)

    def get_all_product_list(self) -> list:
        return self._cursor.execute('SELECT * FROM product').fetchall()

    def get_product_info(self, prod_id: int) -> tuple:
        data = self._cursor.execute('SELECT * FROM product WHERE id = ?', (prod_id,)).fetchone()
        if data is not None:
            return data
        else:
            raise Exception("Product is not exist")

    def get_product_name(self, prod_id: int) -> str:
        """
        :return: product name if it`s exist else -> product not found
        """
        name = self._cursor.execute(f'SELECT name FROM product WHERE id = ?', (prod_id,)).fetchone()[0]
        if name is not None:
            return name

        return "Товар не найден"

    def change_product(self, prod_data: FSMContextProxy):
        self._cursor.execute('UPDATE product SET (photo, name, price, description) = (?, ?, ?, ?) WHERE id = ?',
                             (prod_data["photo"], prod_data["name"], prod_data["price"],
                              prod_data["description"], prod_data["product_id"],))
        self._database.commit()

    def delete_product(self, prod_id: int):
        self._cursor.execute('DELETE FROM product WHERE id = ?', (prod_id,))
        self._database.commit()

    def get_product_price(self, prod_id: int) -> int:
        price: int = self._cursor.execute('SELECT price FROM product WHERE id = ?', (prod_id,)).fetchone()[0]

        return price

    # -------------------- #
    # Operation on clients #
    # -------------------- #

    def add_client(self, client_id: int):
        client = self._cursor.execute(f'SELECT id FROM client WHERE id = ?', (client_id,)).fetchone()
        if client is None:
            self._cursor.execute('INSERT INTO client (id) VALUES (?)', (client_id,))
            self._database.commit()

    def add_client_if_not_exist(func):
        def wrapper(self, client_id, *args, **kwargs):
            self.add_client(client_id)
            return func(self, client_id, *args, **kwargs)

        return wrapper

    @add_client_if_not_exist
    def get_client_balance(self, client_id: int) -> float:
        balance: float = self._cursor.execute(f'SELECT balance FROM client WHERE id = ?', (client_id,)).fetchone()[0]

        return balance

    @add_client_if_not_exist
    def change_client_balance(self, client_id: int, cash: float):
        """
        :param cash: Can be positive if client deposit cash and negative if he buys something
        """
        data: tuple = self._cursor.execute(f'SELECT balance, paid, salesCount  FROM client WHERE id = ?',
                                           (client_id,)).fetchone()
        balance: float = data[0]
        paid: float = data[1] + abs(cash) if cash < 0 else data[1]
        sales_count: int = data[2] + 1 if cash < 0 else data[2]
        if cash > 0 or balance + cash >= 0:
            self._cursor.execute('UPDATE client SET (balance, paid, salesCount) = (?, ?, ?) WHERE id = ?',
                                 (balance + cash, paid, sales_count, client_id,))
            self._database.commit()
        else:
            raise ValueIsNoneException("Not enough money to pay")

    @add_client_if_not_exist
    def get_herself_data_for_client(self, client_id: int) -> tuple:
        """
        Used in client handlers for getting data about client
        """
        data: tuple = self._cursor.execute(f'SELECT * FROM client WHERE id = ?', (client_id,)).fetchone()

        return data

    def get_client_data_for_admin(self, client_id: int) -> tuple or None:
        """
        Used in admins handlers for getting data about every user. Return None if client id isn`t exist.
        """
        data: tuple = self._cursor.execute(f'SELECT * FROM client WHERE id = ?', (client_id,)).fetchone()

        return data

    # --------------------- #
    # Operation on delivers #
    # --------------------- #

    def add_delivery(self, state: FSMContext):
        with state.proxy() as data:
            self._cursor.execute(
                'INSERT INTO delivery (productId, photo, adress, description, dateOfAdding) VALUES (?, ?, ?, ?, ?)',
                (*[val for val in data.values()], str(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), )))
            self._database.commit()

    def delete_delivery(self, del_id: int):
        self._cursor.execute('DELETE FROM delivery WHERE id = ?', (del_id,))
        self._database.commit()

    def get_delivery_info_from_id(self, del_id: int) -> tuple:
        data: tuple = self._cursor.execute('SELECT * FROM delivery WHERE id = ?', (del_id,)).fetchone()
        if data is None:
            raise ValueIsNoneException("Delivery not found")

        return data

    def get_available_delivers_list(self) -> list:
        return self._cursor.execute('SELECT * FROM delivery WHERE available = TRUE').fetchall()

    def get_id_available_deliver(self, prod_id: int) -> int:
        del_id: int = self._cursor.execute(f'SELECT id FROM delivery WHERE productId = (?) AND available = TRUE',
                                           (prod_id,)).fetchone()[0]
        if del_id is None:
            raise ValueIsNoneException("Not exist available delivery for this product id")

        return del_id

    def get_delivers_from_product_id(self, prod_id: int) -> tuple:
        return self._cursor.execute('SELECT * FROM delivery WHERE productId = ?', (prod_id,)).fetchall()[0]

    def change_available_status_delivery(self, del_id: int):
        self._cursor.execute('UPDATE delivery SET available = FALSE WHERE id = ?', (del_id,))
        self._database.commit()

    # ------------------ #
    # Operation on Sales #
    # ------------------ #

    def register_new_sale(self, buyer_id: int, del_id: int, paid: int):
        self._cursor.execute('INSERT INTO sale (buyerId, deliveryId, dateSales, paid) VALUES (?, ?, ?, ?)',
                             (buyer_id, del_id, str(datetime.now().strftime("%m/%d/%Y, %H:%M:%S")), paid,))
        self._database.commit()

    def get_sales_from_client_id(self, client_id: int) -> list:
        """
        :return: Last 10 sales of client
        """
        sales: list = self._cursor.execute('SELECT * FROM sale WHERE buyerId = ? ORDER BY id DESC LIMIT 10',
                                           (client_id,)).fetchall()
        return sales

    def get_sale_from_id(self, sale_id: int) -> tuple:
        data: tuple = self._cursor.execute('SELECT * FROM sale WHERE id = ?', (sale_id,)).fetchone()
        if data is None:
            raise ValueIsNoneException("Sale not found.")
        return data

    # ------------------- #
    # Operation on wallet #
    # ------------------- #

    def add_new_wallet_address(self, address: str, network: str, balance: int):
        wallet_address = self._cursor.execute(f'SELECT address FROM wallet WHERE address = ?', (address,)).fetchone()
        if wallet_address is None:
            self._cursor.execute('INSERT INTO wallet (address, balance, network) VALUES (?, ?, ?)',
                                 (address, balance, network,))
            self._database.commit()

    def get_wallet_all_addresses_list(self) -> list:
        return self._cursor.execute('SELECT * FROM wallet').fetchall()

    def get_wallet_address_data(self, address_id: int) -> tuple:
        return self._cursor.execute('SELECT * FROM wallet WHERE id = ?', (address_id,)).fetchone()

    def delete_wallet_address(self, address_id: int):
        self._cursor.execute('DELETE FROM wallet WHERE id = ?', (address_id,))
        self._database.commit()

    def change_wallet_address_frozen_status(self, address_id: int, balance: int):
        """
        Inverts frozen status of wallet address, True -> False and False -> True.
        """
        frozen_status: bool = self._cursor.execute('SELECT frozen FROM wallet WHERE id = ?', (address_id,)).fetchone()[
            0]
        if frozen_status is not None:
            frozen_status = False if frozen_status else True
            self._cursor.execute('UPDATE wallet SET (frozen, balance) = (?, ?) WHERE id = ?',
                                 (frozen_status, balance, address_id,))
            self._database.commit()

    def get_available_wallet_address(self, network: str, customer_id: int) -> tuple:
        return self._cursor.execute('SELECT * FROM wallet WHERE network = ? and frozen = FALSE and usedUntil = "free"'
                                    ' and idClientForWait != ?',
                                    (network, customer_id,)).fetchone()

    def set_usage_status_wallet_address(self, address_id: int, customer_id: int, payment_time: int):
        """
        Setting time for payments.
        """
        address_id = self._cursor.execute('SELECT id FROM wallet WHERE id = ?', (address_id,)).fetchone()
        if address_id is not None:
            wait_time = datetime.datetime.today() + datetime.timedelta(minutes=payment_time)
            self._cursor.execute('UPDATE wallet SET (usedUntil, idClientForWait) = (?, ?) WHERE id = ?',
                                 (wait_time, customer_id, address_id[0],))
            self._database.commit()

    def get_id_wallet_addresses_that_over_wait(self) -> list:
        """
        :return: List of addresses id that already have over wait.
        """
        addresses: list = self._cursor.execute('SELECT id, usedUntil FROM wallet WHERE usedUntil != "free"').fetchall()
        result_id = list()
        if addresses is not None:
            cur_time = (datetime.datetime.today())
            for a in addresses:
                if cur_time > a[1]:
                    result_id.append(a[0])

        return result_id

    def set_usage_status_how_free_wallet_address(self, address_id: int):
        address: tuple = self._cursor.execute('SELECT id FROM wallet WHERE id = ?', (address_id,)).fetchone()
        if address is not None:
            self._cursor.execute('UPDATE wallet SET (usedUntil, idClientForWait) = (?, ?) WHERE id = ?',
                                 ("free", -1, address_id,))
            self._database.commit()

    def update_wallet_address_balance(self, address_id: int, balance: float):
        address: tuple = self._cursor.execute('SELECT id FROM wallet WHERE id = ?', (address_id,)).fetchone()
        if address is not None:
            self._cursor.execute('UPDATE wallet SET (balance) = (?) WHERE id = ?', (balance, address_id,))
            self._database.commit()
