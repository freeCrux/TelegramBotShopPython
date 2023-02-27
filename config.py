import os
from dotenv import load_dotenv


load_dotenv()

token_telegram = os.environ["token_telegram_env"]

token_cripto = ""

# Admin data for verify
admin_login = os.environ["admin_login_env"]
admin_password = os.environ["admin_password_env"]
admins_id_list = list()

available_network = ["BTC"]

# Time for waiting payments it`s hours
WAIT_LIMIT = 1
