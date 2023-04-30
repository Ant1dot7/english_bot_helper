import os
from aiogram import types, Dispatcher
from buttons import client_buttons
from aiogram.dispatcher.filters import Text
from create_bot import dp, bot
from dotenv import load_dotenv
from buttons.admin_buttons import start_menu_buttons_admin
from data_base.data_base import get_audio
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

load_dotenv()

text = {}  # словарь для хранения текста под конкретный аудио


async def start_command(message: types.Message):
    """Начало работы бота"""

    await message.delete()
    if message.from_user.id == int(os.getenv('id_admin')):
        await message.answer('Привет admin', reply_markup=start_menu_buttons_admin())
    else:
        await message.answer('Привет!\nЯ помогу тебе освоить английский язык!\nВыбери то, что хочешь потренеровать.', reply_markup=client_buttons.start_menu_butons())


async def listening(mesasge: types.Message):
    """Выбор сложности аудио-текста"""

    await mesasge.delete()
    await mesasge.answer('Выбери сложность текста, который хочешь прослушать', reply_markup=client_buttons.listening_menu())


async def listening_easy_text(message: types.Message):
    """Получаем запрос на уровень сложности аудио-текста и формируем ответ в виде inline кнопок"""

    answer_for_listening = {
        'Easy texts': [client_buttons.listening_inline_but()[1], 'Вот простые тексты:'],
        'Medium texts': [client_buttons.listening_inline_but()[2], 'Вот средние тексты:'],
        'Hard texts': [client_buttons.listening_inline_but()[3], 'Вот сложные тексты:']
    }
    command = message.text
    await message.delete()
    await message.answer(text=answer_for_listening[command][1], reply_markup=answer_for_listening[command][0])


@dp.callback_query_handler(lambda c: c.data.startswith('text_'))
async def listening_callback_button(callback: types.CallbackQuery):
    """Получаем данные из кнопки и выдаем нужный аудио-текст"""

    title = callback.data.split('_')[-1]
    audio_text = await get_audio(title)
    text[audio_text[0]] = audio_text[3]
    show_text_button = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='Показать текст', callback_data=f'show_text_{audio_text[0]}'))
    await bot.send_document(callback.from_user.id, audio_text[1], reply_markup=show_text_button)
    await callback.answer()


@dp.callback_query_handler(Text(startswith='show_text'))
async def show_text(callback: types.CallbackQuery):
    """Функция, которая позволяет показать текст для выбранного аудио"""

    title = callback.data.split('_')[-1]
    try:
        await bot.send_message(callback.from_user.id, text[title])
    except KeyError:
        await bot.send_message(callback.from_user.id, 'Данные могли устареть. Выберите текст сначала')
    await callback.answer()


def register_handlers(dp: Dispatcher):
    """Регистрация хендлеров"""

    dp.register_message_handler(start_command, commands=['start'])
    dp.register_message_handler(listening, Text(equals='Аудирование', ignore_case=True))
    dp.register_message_handler(listening_easy_text, Text(endswith='texts'))
