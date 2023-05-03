from aiogram.utils import executor
from handler import client, admin, words
from create_bot import dp
from data_base import data_base


async def on_startup(_):
    print('Bot run online')
    await data_base.sql_start()


client.register_handlers(dp)
admin.rester_handlers_admin(dp)
words.register_words_hendlers(dp)
executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
