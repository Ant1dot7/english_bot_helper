import os

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv

from buttons import client_buttons
from buttons.admin_buttons import start_menu_buttons_admin
from create_bot import bot, dp
from data_base.data_base import get_audio

load_dotenv()

text = {}  # словарь для хранения текста под конкретный аудио


async def start_command(message: types.Message):
    """Начало работы бота"""

    await message.delete()
    if message.from_user.id == int(os.getenv('id_admin')):
        await message.answer('Привет admin', reply_markup=start_menu_buttons_admin())
    else:
        await message.answer('''Привет! \U0001F44B
Я помогу тебе освоить английский язык! \U0001F1EC\U0001F1E7
Выбери то, что хочешь потренеровать. \U0001F3CB\U0000FE0F\U0000200D\U00002642\U0000FE0F''', reply_markup=client_buttons.start_menu_butons())


async def listening(mesasge: types.Message):
    """Выбор сложности аудио-текста"""

    await mesasge.delete()
    await mesasge.answer('''\U0001F3B5 В данном разделе будут представлены аудио записи для аудирования \U0001F3B5
Выбери сложность записи, которую хочешь прослушать \U0001F3A7''',
                         reply_markup=client_buttons.listening_menu())


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
    dp.register_message_handler(listening, Text(equals=['\U0001F3B5 Аудирование \U0001F3B5', '/audir'], ignore_case=True))
    dp.register_message_handler(listening_easy_text, Text(endswith='texts'))
