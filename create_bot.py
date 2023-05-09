import os

from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from dotenv import load_dotenv

load_dotenv()

storage = MemoryStorage()
bot_key = os.getenv('bot_token')
bot = Bot(token=bot_key)
dp = Dispatcher(bot, storage=storage)
