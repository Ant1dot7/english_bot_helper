import os
from aiogram import types, Dispatcher
from buttons import client_buttons
from aiogram.dispatcher.filters import Text
from create_bot import dp
from dotenv import load_dotenv
from buttons.admin_buttons import start_menu_buttons_admin

load_dotenv()


async def start_command(message: types.Message):
    await message.delete()
    if message.from_user.id == int(os.getenv('id_admin')):
        await message.answer('Привет admin', reply_markup=start_menu_buttons_admin())
    else:
        await message.answer('Привет!\nЯ помогу тебе освоить английский язык!\nВыбери то, что хочешь потренеровать.', reply_markup=client_buttons.start_menu_butons())





async def listening(mesasge: types.Message):
    await mesasge.delete()
    await mesasge.answer('Выбери сложность текста, который хочешь прослушать', reply_markup=client_buttons.listening_menu())


async def listening_easy_text(message: types.Message):
    await message.delete()
    await message.answer('Вот простые тексты:', reply_markup=client_buttons.easy_texts_inline_but())


@dp.callback_query_handler(lambda c: c.data.startswith('button_'))
async def process_callback_button(callback: types.CallbackQuery):
    button_number = int(callback.data.split("_")[1])
    message_text = f"Нажата {button_number}"
    await callback.message.answer(message_text)
    await callback.answer()


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_command, commands=['start'])
    dp.register_message_handler(listening, Text(equals='Аудирование', ignore_case=True))
    dp.register_message_handler(listening_easy_text, Text(equals='easy_texts', ignore_case=True))
