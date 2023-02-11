from aiogram import executor, types
from bot_init import bot, dp
from handlers import client, admin
from database import sql_db


async def on_startup(_):
    print("Bot starting...")
    sql_db.sql_connect()


admin.register_admin_handlers(dp=dp)
client.register_client_handlers(dp=dp)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
