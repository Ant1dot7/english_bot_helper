from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from buttons.client_buttons import words_menu, button_show_more_remember_button
from create_bot import bot, dp
from data_base import data_base
import aioredis
import json


async def start_command_words(message: types.Message):
    """Старт работы со словами"""

    await message.delete()
    await message.answer('Я буду показывать тебе слова, если знаешь их жми "Показать ещё".\n' \
                         'Если что то не знаешь - сохрани для повторения.\nНажми "начать", чтобы проверить свои знания',
                         reply_markup=words_menu())


async def first_ten_words(message: types.Message):
    """Первые 10 слов из списка 2000"""

    await message.delete()
    async with aioredis.from_url("redis://localhost") as redis:
        all_words = json.loads(await redis.get('words_to_translate'))
        if not await redis.exists('words_dict_from_user'):
            words_dict_from_user = {}
        else:
            words_dict_from_user = json.loads(await redis.get('words_dict_from_user'))
        words_dict_from_user[message.from_user.id] = 0  # начало отсчета нажатия кнопки
        await redis.set('words_dict_from_user', json.dumps(words_dict_from_user))
    await message.answer(all_words['0'], reply_markup=button_show_more_remember_button(0))


@dp.callback_query_handler(Text(startswith='more_word'))
async def more_word(callback: types.CallbackQuery):
    """Кнопка для показа следующего списка слов"""

    async with aioredis.from_url("redis://localhost") as redis:
        words_dict_from_user = json.loads(await redis.get('words_dict_from_user'))
        all_words = json.loads(await redis.get('words_to_translate'))
        words_dict_from_user[str(callback.from_user.id)] += 1
        await redis.set('words_dict_from_user', json.dumps(words_dict_from_user))
        answer = all_words[f'{words_dict_from_user[str(callback.from_user.id)]}']

    await bot.send_message(callback.from_user.id, answer, reply_markup=button_show_more_remember_button(words_dict_from_user[str(callback.from_user.id)]))
    await callback.answer()


@dp.callback_query_handler(Text(startswith='save'))
async def save_to_repeat(callback: types.CallbackQuery):
    """Сохранение в бд список желаемых слов"""

    async with aioredis.from_url("redis://localhost") as redis:
        all_words = json.loads(await redis.get('words_to_translate'))
    number_words_to_save = callback.data.split('_')[-1]
    words_to_save = all_words[number_words_to_save]
    save = await data_base.save_words_to_repeat(callback.from_user.id, words_to_save)
    await del_button_save(callback)
    if not save:
        await callback.answer('Данный список сохранен')
    else:
        await callback.answer('Вы уже сохраняли этот список', show_alert=True)


async def show_repeat_words(message: types.Message):
    """Показ по запросу слова которые были сохранены пользователем"""

    await message.delete()
    words_to_repeat = await data_base.get_words_to_repeat(message.from_user.id)
    if words_to_repeat:
        await message.answer(words_to_repeat)
    else:
        await message.answer('Вы ещё не сохранили ни одного списка для повторения', reply_markup=words_menu())


async def delete_repeat_words(message: types.Message):
    """Удаление слов для повторения из базы данных"""

    await message.delete()
    await data_base.del_words_to_repeat(message.from_user.id)
    await message.answer('Список слов был удален', reply_markup=words_menu())


async def del_button_save(callback):
    """Удаление кнопки <Сохранить> после её нажатия"""

    keyboard = callback.message.reply_markup.inline_keyboard
    new_keyboard = types.InlineKeyboardMarkup(row_width=1)
    for row in keyboard:
        for button in row:
            if 'save' not in button.callback_data:
                new_keyboard.insert(button)
    await callback.message.edit_reply_markup(reply_markup=new_keyboard)


def register_words_handlers(dp: Dispatcher):
    dp.register_message_handler(delete_repeat_words, Text(equals='\U0000274C Удалить сохраненные записи \U0000274C', ignore_case=True))
    dp.register_message_handler(show_repeat_words, Text(equals='\U0001F504 Повторить слова \U0001F504', ignore_case=True))
    dp.register_message_handler(first_ten_words, Text(equals='\U0001F3C1 Начать \U0001F3C1', ignore_case=True))
    dp.register_message_handler(start_command_words, Text(equals=['\U0001F4DD Слова \U0001F4DD', '/words'], ignore_case=True))
