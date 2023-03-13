from aiogram import executor
from bot_init import dp, scheduler, db, wallets_processing
import datetime
from handlers import client, admin


async def on_startup(_):
    client.register_client_handlers(dp=dp)
    admin.register_admin_handlers(dp=dp)

    scheduler.add_job(wallets_processing.processing_addresses_that_over_wait_and_update_coins_rate,
                      "interval", seconds=300, start_date=datetime.datetime.now(), args=())


async def on_shutdown(_):
    db.sql_close()


if __name__ == '__main__':
    scheduler.start()
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)

