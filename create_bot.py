from aiogram import Bot
from aiogram.dispatcher import Dispatcher
import os
from dotenv import load_dotenv
from aiogram.contrib.fsm_storage.memory import MemoryStorage

load_dotenv()

storage = MemoryStorage()
bot_key = os.getenv('bot_token')
bot = Bot(token=bot_key)
dp = Dispatcher(bot, storage=storage)
