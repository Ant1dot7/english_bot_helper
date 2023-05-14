from aiogram.utils import executor
from create_bot import dp
from data_base import data_base
from handler import admin, audir, words, tests
from utils import start


async def on_startup(_):
    print('Bot run online')
    await data_base.sql_start()
    await start.get_all_words()


audir.register_audir_handlers(dp)
admin.rester_handlers_admin(dp)
words.register_words_handlers(dp)
tests.register_test_handlers(dp)
start.register_handlers_start(dp)
executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
