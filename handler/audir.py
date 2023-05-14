import os
import aioredis
from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv

from buttons import client_buttons
from buttons.admin_buttons import start_menu_buttons_admin
from create_bot import bot, dp
from data_base.data_base import get_audio

load_dotenv()


async def listening(message: types.Message):
    """Выбор сложности аудио-текста"""

    await message.delete()
    await message.answer('''\U0001F3B5 В данном разделе будут представлены аудио записи для аудирования \U0001F3B5
Выбери сложность записи, которую хочешь прослушать \U0001F3A7''',
                         reply_markup=client_buttons.listening_menu())


async def listening_easy_text(message: types.Message):
    """Получаем запрос на уровень сложности аудио-текста и формируем ответ в виде inline кнопок"""

    answer_for_listening = {
        '\U0001F600 Easy texts': [client_buttons.listening_inline_but()[1], 'Вот простые тексты:'],
        '\U0001F914 Medium texts': [client_buttons.listening_inline_but()[2], 'Вот средние тексты:'],
        '\U0001F92F Hard texts': [client_buttons.listening_inline_but()[3], 'Вот сложные тексты:']
    }
    command = message.text
    await message.delete()
    await message.answer(text=answer_for_listening[command][1], reply_markup=answer_for_listening[command][0])


@dp.callback_query_handler(lambda c: c.data.startswith('text_'))
async def listening_callback_button(callback: types.CallbackQuery):
    """Получаем данные из кнопки и выдаем нужный аудио"""

    title = callback.data.split('_')[-1]
    audio_text = await get_audio(title)
    async with aioredis.from_url("redis://localhost") as redis:
        if not await redis.exists(audio_text[0]):
            await redis.set(audio_text[0], audio_text[3])
    show_text_button = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='Показать текст', callback_data=f'show_text_{audio_text[0]}'))
    await bot.send_audio(callback.from_user.id, audio_text[1], reply_markup=show_text_button)
    await callback.answer()


@dp.callback_query_handler(Text(startswith='show_text'))
async def show_text(callback: types.CallbackQuery):
    """Функция, которая позволяет показать текст для выбранного аудио"""

    title = callback.data.split('_')[-1]
    async with aioredis.from_url("redis://localhost") as redis:
        text = await redis.get(title)
        text = text.decode()
    await bot.send_message(callback.from_user.id, text)
    await callback.answer()


def register_audir_handlers(dp: Dispatcher):
    """Регистрация хендлеров"""

    dp.register_message_handler(listening, Text(equals=['\U0001F3B5 Аудирование \U0001F3B5', '/audir'], ignore_case=True))
    dp.register_message_handler(listening_easy_text, Text(endswith='texts'))
