import os
from dotenv import load_dotenv


load_dotenv()
token_telegram = os.environ["token_telegram_env"]
token_coinmarketcap = os.environ["token_coinmarketcap"]
token_etherscan = os.environ["token_etherscan"]
admin_login = os.environ["admin_login_env"]
admin_password = os.environ["admin_password_env"]

admins_id_list = list()
AVAILABLE_NETWORK = ("BTC", "USDT",)
