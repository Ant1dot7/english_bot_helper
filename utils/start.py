from aiogram import types, Dispatcher
from buttons.client_buttons import start_menu_butons
from buttons.admin_buttons import start_menu_buttons_admin
import os
import aioredis
import json
import csv


async def start_command(message: types.Message):
    """Начало работы бота"""

    await message.delete()
    if message.from_user.id == int(os.getenv('id_admin')):
        await message.answer('Привет admin', reply_markup=start_menu_buttons_admin())
    else:
        await message.answer('''Привет! \U0001F44B
Я помогу тебе освоить английский язык! \U0001F1EC\U0001F1E7
Выбери то, что хочешь потренеровать. \U0001F3CB\U0000FE0F\U0000200D\U00002642\U0000FE0F''', reply_markup=start_menu_butons())


async def get_all_words():
    """Запись слов из csv файла в redis"""
    all_words = {}
    with open('utils/words.csv', 'r', encoding='utf-8') as file:
        words_2000 = csv.reader(file)
        for i, word in enumerate(words_2000):
            check_index = i // 10  # Определяем, в какой блок добавляем текущий элемент
            if check_index not in all_words:
                all_words[check_index] = ''  # Создаем новый блок, если его еще нет
            all_words[check_index] += ': '.join(word) + '\n'  # Добавляем текущий элемент в соответствующий блок
    async with aioredis.from_url("redis://localhost") as redis:
        await redis.set('words_to_translate', json.dumps(all_words))
        print("Слова из csv прочитаны")


def register_handlers_start(dp: Dispatcher):
    dp.register_message_handler(start_command, commands=['start'])
