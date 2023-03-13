from tzlocal import get_localzone
from aiogram import Bot, Dispatcher, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from database.sql_bd import DataBase
from config import token_coinmarketcap, AVAILABLE_NETWORK, token_telegram, token_etherscan


st = MemoryStorage()
scheduler = AsyncIOScheduler(timezone=str(get_localzone()))
db = DataBase(path="server.db")
bot = Bot(token=token_telegram, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=st)

from handlers.other import WalletsHandler
wallets_processing = WalletsHandler(network=AVAILABLE_NETWORK, db=db, token_coinmarketcap=token_coinmarketcap,
                                    token_etherscan=token_etherscan)
