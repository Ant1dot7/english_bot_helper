from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from create_bot import dp, bot
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from data_base import data_base
from buttons import admin_buttons
from dotenv import load_dotenv
import os

load_dotenv()


class FSMAudio(StatesGroup):
    title = State()
    audio = State()
    category = State()
    description = State()


class FSMCategory(StatesGroup):
    title = State()


async def make_changes_command(message: types.Message):
    if message.from_user.id == int(os.getenv('id_admin')):
        await bot.send_message(message.from_user.id, 'Что вы ходите добавить?', reply_markup=admin_buttons.admin_but())
    await message.delete()


async def command_load_category(message: types.Message):
    if message.from_user.id == int(os.getenv('id_admin')):
        await FSMCategory.title.set()
        await message.reply('Напиши название категории')


async def load_category(message: types.Message, state: FSMContext):
    if message.from_user.id == int(os.getenv('id_admin')):
        async with state.proxy() as data:
            data['title'] = message.text
        await data_base.add_cat(state)
        await state.finish()
        await message.answer(f'Категория {message.text} успешно добавлена.')


async def command_load_audio(message: types.Message):
    if message.from_user.id == int(os.getenv('id_admin')):
        await FSMAudio.title.set()
        await message.reply('Напиши название Аудио')


async def load_title_audio(message: types.Message, state: FSMContext):
    if message.from_user.id == int(os.getenv('id_admin')):
        async with state.proxy() as data:
            data['title'] = message.text
        await FSMAudio.next()
        await message.reply('Теперь пришли аудио')


async def load_audio(message: types.Message, state: FSMContext):
    if message.from_user.id == int(os.getenv('id_admin')):
        audio_file = await bot.get_file(message.document.file_id)
        async with state.proxy() as data:
            data['audio'] = audio_file.file_id
        await FSMAudio.next()
        await message.reply('Теперь введи категорию', reply_markup=admin_buttons.categories_but())


async def load_cat_for_audio(message: types.Message, state: FSMContext):
    if message.from_user.id == int(os.getenv('id_admin')):
        async with state.proxy() as data:
            data['category'] = message.text
        await FSMAudio.next()
        await message.reply('Теперь введи текст к этому аудио')


async def load_text_for_audio(message: types.Message, state: FSMContext):
    if message.from_user.id == int(os.getenv('id_admin')):
        async with state.proxy() as data:
            data['description'] = message.text
        await data_base.add_audio(state)
        await state.finish()
        await message.answer(f'Аудио успешно добавлено.')


def rester_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(make_changes_command, commands=['admin'])
    dp.register_message_handler(load_category, state=FSMCategory.title)
    dp.register_message_handler(command_load_category, Text(equals='Добавить категорию', ignore_case=True))
    dp.register_message_handler(load_title_audio, state=FSMAudio.title)
    dp.register_message_handler(load_audio, content_types=['document'], state=FSMAudio.audio)
    dp.register_message_handler(load_cat_for_audio, state=FSMAudio.category)
    dp.register_message_handler(load_text_for_audio, state=FSMAudio.description)
    dp.register_message_handler(command_load_audio, Text(equals='Добавить аудио', ignore_case=True))
