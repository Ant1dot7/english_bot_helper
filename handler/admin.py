import os

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv

from buttons import admin_buttons
from create_bot import bot, dp
from data_base import data_base_load_admin

load_dotenv()


class FSMAudio(StatesGroup):
    """Машина-стояния для загрузки аудио (для аудирования) в бд"""

    title = State()
    audio = State()
    category = State()
    description = State()


class FSMCategory(StatesGroup):
    """Машина-стояния для загрузки категории под АУДИО файл в бд"""
    title = State()


class FSMLoadPicture(StatesGroup):
    """Машина-стояния для загрузки картинок для раздела
       <Что на фото> в бд"""
    picture = State()
    description = State()


async def make_changes_command(message: types.Message):
    """Первое меню кнопок после нажатия </admin>"""

    if message.from_user.id == int(os.getenv('id_admin')):
        await bot.send_message(message.from_user.id, 'Что вы ходите добавить?', reply_markup=admin_buttons.admin_but())
    await message.delete()


async def command_load_picture(message: types.Message):
    """Начало загрузки картинки и её описания для раздела <Что на фото>"""

    if message.from_user.id == int(os.getenv('id_admin')):
        await FSMLoadPicture.picture.set()
        await message.reply('Пришли картинку')


async def load_picture(message: types.Message, state: FSMContext):
    """Принимаем картинку для раздела <Что на фото>"""

    if message.from_user.id == int(os.getenv('id_admin')):
        picture = message.photo[0]['file_id']
        async with state.proxy() as data:
            data['picture'] = picture
        await FSMLoadPicture.next()
        await message.reply('Пришли описание')


async def load_description_picture(message: types.Message, state: FSMContext):
    """Принимаем описание для картинки и загружаем данные в бд"""

    if message.from_user.id == int(os.getenv('id_admin')):
        async with state.proxy() as data:
            data['description'] = message.text
        await data_base_load_admin.add_picture(state)
        await state.finish()
        await message.answer('Картинка успешно добавлена')


async def command_load_category(message: types.Message):
    """Начало загрузки Категории под аудио"""

    if message.from_user.id == int(os.getenv('id_admin')):
        await FSMCategory.title.set()
        await message.reply('Напиши название категории')


async def load_category(message: types.Message, state: FSMContext):
    """Получаем название категории и добавляем её в бд"""

    if message.from_user.id == int(os.getenv('id_admin')):
        async with state.proxy() as data:
            data['title'] = message.text
        await data_base_load_admin.add_cat(state)
        await state.finish()
        await message.answer(f'Категория {message.text} успешно добавлена.')


async def command_load_audio(message: types.Message):
    """Начало загрузки Аудио файла для аудирования"""

    if message.from_user.id == int(os.getenv('id_admin')):
        await FSMAudio.title.set()
        await message.reply('Напиши название Аудио')


async def load_title_audio(message: types.Message, state: FSMContext):
    """Получаем названия аудио-текста"""

    if message.from_user.id == int(os.getenv('id_admin')):
        async with state.proxy() as data:
            data['title'] = message.text
        await FSMAudio.next()
        await message.reply('Теперь пришли аудио')


async def load_audio(message: types.Message, state: FSMContext):
    """Получаем аудио файл"""

    if message.from_user.id == int(os.getenv('id_admin')):
        if message.document:
            audio_file = await bot.get_file(message.document.file_id)
        else:
            audio_file = await bot.get_file(message.audio.file_id)
        async with state.proxy() as data:
            data['audio'] = audio_file.file_id
        await FSMAudio.next()
        await message.reply('Теперь введи категорию', reply_markup=admin_buttons.categories_but())


async def load_cat_for_audio(message: types.Message, state: FSMContext):
    """Получаем категорию сложности аудио файла"""

    if message.from_user.id == int(os.getenv('id_admin')):
        async with state.proxy() as data:
            data['category'] = message.text
        await FSMAudio.next()
        await message.reply('Теперь введи текст к этому аудио')


async def load_text_for_audio(message: types.Message, state: FSMContext):
    """Получаем текст, который звучит в аудио"""

    if message.from_user.id == int(os.getenv('id_admin')):
        async with state.proxy() as data:
            data['description'] = message.text
        await data_base_load_admin.add_audio(state)
        await state.finish()
        await message.answer('Аудио успешно добавлено.')


def rester_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(make_changes_command, commands=['admin'])
    # категории
    dp.register_message_handler(load_category, state=FSMCategory.title)
    dp.register_message_handler(command_load_category, Text(equals='Добавить категорию', ignore_case=True))
    # аудио
    dp.register_message_handler(load_title_audio, state=FSMAudio.title)
    dp.register_message_handler(load_audio, content_types=[types.ContentType.DOCUMENT, types.ContentType.AUDIO], state=FSMAudio.audio)
    dp.register_message_handler(load_cat_for_audio, state=FSMAudio.category)
    dp.register_message_handler(load_text_for_audio, state=FSMAudio.description)
    dp.register_message_handler(command_load_audio, Text(equals='Добавить аудио', ignore_case=True))
    # картинки
    dp.register_message_handler(load_description_picture, state=FSMLoadPicture.description)
    dp.register_message_handler(load_picture, content_types=types.ContentType.PHOTO, state=FSMLoadPicture.picture)
    dp.register_message_handler(command_load_picture, Text(equals='Добавить картинку', ignore_case=True))
