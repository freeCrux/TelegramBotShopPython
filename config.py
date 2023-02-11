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
#admins_id_list.append(admin)
