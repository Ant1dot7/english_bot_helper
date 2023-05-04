from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from create_bot import dp, bot
from buttons.client_buttons import words_menu
import csv
from data_base import data_base

words_dict_from_user = {}
words_save_from_user = {}


async def start_command_words(message: types.Message):
    """Старт работы со словами"""

    await message.answer('Я буду показывать тебе слова, если знаешь их жми "Показать ещё".\nНажми "начать", чтобы проверить свои знания',
                         reply_markup=words_menu()
                         )


async def first_ten_words(message: types.Message):
    """Первые 10 слов из списка 2000"""

    words_dict_from_user[message.from_user.id] = 0  # начало отсчета нажатия кнопки
    ans = get_all_words()[words_dict_from_user[message.from_user.id]]  # загружаем слова из списка для конкретного пользователя

    show_more = types.InlineKeyboardButton(text="Показать ещё", callback_data='more_word')
    remember_button = types.InlineKeyboardButton(text="Сохранить для повторения", callback_data=f'save_{words_dict_from_user[message.from_user.id]}')  # кнопка, которая сохраняет конкретный список слов в базу данных
    button = types.InlineKeyboardMarkup(row_width=1).add(show_more).add(remember_button)
    await message.answer(ans, reply_markup=button)


@dp.callback_query_handler(Text(startswith='more_word'))
async def more_word(callback: types.CallbackQuery):
    """Кнопка для показа следующего списка слов"""
    try:
        words_dict_from_user[callback.from_user.id] += 1
    except KeyError:
        words_dict_from_user[callback.from_user.id] = 0
    ans = get_all_words()[words_dict_from_user[callback.from_user.id]]
    show_more = types.InlineKeyboardButton(text="Показать ещё", callback_data='more_word')
    remember_button = types.InlineKeyboardButton(text="Сохранить для повторения", callback_data=f'save_{words_dict_from_user[callback.from_user.id]}')
    button = types.InlineKeyboardMarkup(row_width=1).add(show_more).add(remember_button)
    await bot.send_message(callback.from_user.id, ans, reply_markup=button)
    await callback.answer()


@dp.callback_query_handler(Text(startswith='save'))
async def save_to_repeat(callback: types.CallbackQuery):
    """Сохранение в бд список желаемых слов"""

    words = int(callback.data.split('_')[-1])
    words = get_all_words()[words]
    save = await data_base.save_words_to_repeat(callback.from_user.id, words)
    await del_button_save(callback)
    if not save:
        await callback.answer('Данный список сохранен')
    else:
        await callback.answer('Вы уже сохраняли этот список', show_alert=True)


async def show_repeat_words(message: types.Message):
    """Показ по запросу слова которые были сохранены пользователем"""

    words_to_repeat = await data_base.get_words_to_repeat(message.from_user.id)
    if words_to_repeat:
        await message.answer(words_to_repeat)
    else:
        await message.answer('Вы ещё не сохранили ни одного списка для повторения')


async def del_button_save(callback):
    """Удаление кнопки <Сохранить> после её нажатия"""

    keyboard = callback.message.reply_markup.inline_keyboard
    new_keyboard = types.InlineKeyboardMarkup(row_width=1)
    for row in keyboard:
        for button in row:
            if 'save' not in button.callback_data:
                new_keyboard.insert(button)
    await callback.message.edit_reply_markup(reply_markup=new_keyboard)

async def delete_repeat_words(message: types.Message):
    await data_base.del_words_to_repeat(message.from_user.id)
    await message.answer('Список слов был удален')


def get_all_words():
    """Получение слов из csv файла"""

    all_words = {}
    with open('words.csv', 'r', encoding='utf-8') as file:
        words = csv.reader(file)
        for i, word in enumerate(words):
            check_index = i // 10  # Определяем, в какой блок добавляем текущий элемент
            if check_index not in all_words:
                all_words[check_index] = ''  # Создаем новый блок, если его еще нет
            all_words[check_index] += ': '.join(word) + '\n'  # Добавляем текущий элемент в соответствующий блок
    return all_words


def register_words_hendlers(dp: Dispatcher):
    dp.register_message_handler(delete_repeat_words, Text(equals='Удалить сохраненные записи', ignore_case=True))
    dp.register_message_handler(show_repeat_words, Text(equals='Повторить слова', ignore_case=True))
    dp.register_message_handler(first_ten_words, Text(equals='Начать', ignore_case=True))
    dp.register_message_handler(start_command_words, Text(equals='Слова', ignore_case=True))
