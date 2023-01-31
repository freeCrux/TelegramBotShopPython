from aiogram import Bot, Dispatcher
from config import token_telegram
from aiogram.contrib.fsm_storage.memory import MemoryStorage

st = MemoryStorage()
bot = Bot(token=token_telegram)
dp = Dispatcher(bot, storage=st)

