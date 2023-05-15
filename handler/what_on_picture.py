from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from create_bot import bot, dp
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from data_base.data_base import get_pictures_to_game
from buttons.client_buttons import start_menu_butons, stop_picture_button
import aioredis
import json


class FSMPicture(StatesGroup):
    first = State()
    second = State()
    third = State()
    fourth = State()
    fifth = State()


async def start_guess(message: types.Message):
    """Начало показа фото. Получаем данные из бд, группируем на
    список по 5 фото и выдаем пользователю по одной."""

    await message.delete()
    global picture
    async with aioredis.from_url("redis://localhost") as redis:
        if not await redis.exists('dict_users_picture'):
            dict_users_picture = {}
        else:
            dict_users_picture = json.loads(await redis.get('dict_users_picture'))
        if str(message.from_user.id) in dict_users_picture:
            dict_users_picture[f'{message.from_user.id}'] += 1
        else:
            dict_users_picture[f'{message.from_user.id}'] = 0
        numer_game = dict_users_picture[f'{message.from_user.id}']
        await redis.set('dict_users_picture', json.dumps(dict_users_picture))
        await FSMPicture.first.set()
        picture = await get_pictures_to_game()
        await bot.send_photo(message.from_user.id, photo=picture[numer_game][0][0], reply_markup=stop_picture_button())


async def cancel_handler(message: types.Message, state: FSMContext):
    """Хендлер остановки показа картинок и выхода из машины-состояния"""

    async with aioredis.from_url("redis://localhost") as redis:
        dict_users_picture = json.loads(await redis.get('dict_users_picture'))
        if str(message.from_user.id) in dict_users_picture:
            del dict_users_picture[f'{message.from_user.id}']
            await redis.set('dict_users_picture', json.dumps(dict_users_picture))

    await state.finish()
    await message.answer('Остановил работу', reply_markup=start_menu_butons())
    await message.delete()


async def first_picture(message: types.Message, state: FSMContext):
    """Проверка ответа на первую фото и выдача второй"""

    async with aioredis.from_url("redis://localhost") as redis:
        dict_users_picture = json.loads(await redis.get('dict_users_picture'))
        numer_game = dict_users_picture[f'{message.from_user.id}']
        if message.text.lower() == picture[numer_game][0][1]:
            await message.answer(f'✅ Правильно это {picture[numer_game][0][1]}')
        else:
            await message.answer(f'❌ Неправильно. Это {picture[numer_game][0][1]}')
        await bot.send_photo(message.from_user.id, photo=picture[numer_game][1][0], reply_markup=stop_picture_button())
        await FSMPicture.next()


async def second_picture(message: types.Message, state: FSMContext):
    """Проверка ответа на второй фото и выдача третьей"""

    async with aioredis.from_url("redis://localhost") as redis:
        dict_users_picture = json.loads(await redis.get('dict_users_picture'))
        numer_game = dict_users_picture[f'{message.from_user.id}']
        if message.text.lower() == picture[numer_game][1][1]:
            await message.answer(f'✅ Правильно это {picture[numer_game][1][1]}')
        else:
            await message.answer(f'❌ Неправильно. Это {picture[numer_game][1][1]}')
        await bot.send_photo(message.from_user.id, photo=picture[numer_game][2][0], reply_markup=stop_picture_button())
        await FSMPicture.next()


async def third_picture(message: types.Message, state: FSMContext):
    """Проверка ответа на третью фото и выдача четвертой"""

    async with aioredis.from_url("redis://localhost") as redis:
        dict_users_picture = json.loads(await redis.get('dict_users_picture'))
        numer_game = dict_users_picture[f'{message.from_user.id}']
        if message.text.lower() == picture[numer_game][2][1]:
            await message.answer(f'✅ Правильно это {picture[numer_game][2][1]}')
        else:
            await message.answer(f'❌ Неправильно. Это {picture[numer_game][2][1]}')
        await bot.send_photo(message.from_user.id, photo=picture[numer_game][3][0], reply_markup=stop_picture_button())
        await FSMPicture.next()


async def fourth_picture(message: types.Message, state: FSMContext):
    """Проверка ответа на четвертую фото и выдача пятой"""

    async with aioredis.from_url("redis://localhost") as redis:
        dict_users_picture = json.loads(await redis.get('dict_users_picture'))
        numer_game = dict_users_picture[f'{message.from_user.id}']
        if message.text.lower() == picture[numer_game][3][1]:
            await message.answer(f'✅ Правильно это {picture[numer_game][3][1]}')
        else:
            await message.answer(f'❌ Неправильно. Это {picture[numer_game][3][1]}')
        await bot.send_photo(message.from_user.id, photo=picture[numer_game][4][0], reply_markup=stop_picture_button())
        await FSMPicture.next()


async def fifth_picture(message: types.Message, state: FSMContext):
    """Проверка ответа на пятую фото. Проверка есть ли ещё фото для пользователя
    Если да, предлагаем пройти ещё, если нет - обнуляем счетчик для пользователя"""

    async with aioredis.from_url("redis://localhost") as redis:
        dict_users_picture = json.loads(await redis.get('dict_users_picture'))
        numer_game = dict_users_picture[f'{message.from_user.id}']
        if message.text.lower() == picture[numer_game][4][1]:
            await message.answer(f'✅ Правильно это {picture[numer_game][4][1]}')
        else:
            await message.answer(f'❌ Неправильно. Это {picture[numer_game][4][1]}')
        if len(picture) - 1 != numer_game:
            await message.answer('Хотите продолжить?', reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add('Продолжить'))
        else:
            await message.answer('Вы прошли все картинки!', reply_markup=start_menu_butons())
            del dict_users_picture[f'{message.from_user.id}']
            await redis.set('dict_users_picture', json.dumps(dict_users_picture))
        await state.finish()


def rester_handlers_picture(dp: Dispatcher):
    dp.register_message_handler(start_guess, Text(equals=['❓ Что на фото? ❓', 'Продолжить'], ignore_case=True))
    dp.register_message_handler(cancel_handler, Text(equals='Остановить ⛔'), state='*')
    dp.register_message_handler(first_picture, state=FSMPicture.first)
    dp.register_message_handler(second_picture, state=FSMPicture.second)
    dp.register_message_handler(third_picture, state=FSMPicture.third)
    dp.register_message_handler(fourth_picture, state=FSMPicture.fourth)
    dp.register_message_handler(fifth_picture, state=FSMPicture.fifth)
