import os
from dotenv import load_dotenv


load_dotenv()

token_telegram = os.environ["token_telegram_env"]

token_cripto = ""

# Admin data for verify
admin_login = os.environ["admin_login_env"]
admin_password = os.environ["admin_password_env"]
admin = int(os.environ["admin_for_test"])
admins_id_list = list()
admins_id_list.append(admin)

client_message_handler_text = {
    "start": "Привет ты попал в магазин выпечки!\n\n",
    "help": "Вы по любым вопросам вы всегда можете обратиться в поддержку @freecrux\n"
            "В случае проблем с заказом вам понадобиться ваш ИД (/wallet) и ИД вашего заказа (/myBuy)\n\n"
            "Для покупки вам нужно пополнить счет, введите команду /pay или "
            "выберите в меню пункт [Пополнить баланс]\n\n"
            "Для простотра баланса и общей информации о вас, введите команду /wallet или "
            "выберите в меню пункт [Баланс]\n\n"
            "Список товараов обновляеться динамически при поступлении нового товара, для просмтора "
            "товара в наличии введите команду /products или выберите в меню пункт [Ассортимент]\n\n"
            "Для просмотра последних покупок введите команду /myBuy или выберите в меню пункт [Мои покупки]",
    "myLastBuy": "У вас нет покупок",
    "balance": "Твой баланс",
    "deposit": "Скинь деньгу сюда 000000111",
}

admin_message_handler_text = {
    "admin": "",
    "register": "",
    "logout": "",
    "getLogin": "",
    "getPassword": "",

    "addNewProduct": "",
    "setProductName": "",
    "setProductPrice": "",
    "setProductPhoto": "",
    "setProductDescription": "",

    "deleteProduct": "",
    "editProduct": "",

    "addDelivery": "",
    "getActiveDelivery": "",
    "deleteDelivery": "",

    "cancelInput": "",

    "getLastSales": "",
    "getSalesById": "",

    "getAllDelivery": "",
    "getDelivery": "",
}
