from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from create_bot import dp, bot
from buttons.client_buttons import words_buttons
import csv

words_dict_from_user = {}


async def start_command_words(message: types.Message):
    """Старт работы со словами"""

    await message.answer('Я буду показывать тебе слова, если знаешь их жми "Показать ещё".\nНажми "начать", чтобы проверить свои знания',
                         reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton('Начать'))
                         )


async def first_ten_words(message: types.Message):
    """Первые 10 слов из списка 2000"""

    words_dict_from_user[message.from_user.id] = 0
    ans = get_all_words()[words_dict_from_user[message.from_user.id]]
    await message.answer(ans, reply_markup=words_buttons())


@dp.callback_query_handler(Text(startswith='more_word'))
async def more_word(callback: types.CallbackQuery):
    """Кнопка для показа следующего списка слов"""

    words_dict_from_user[callback.from_user.id] += 1
    ans = get_all_words()[words_dict_from_user[callback.from_user.id]]
    await bot.send_message(callback.from_user.id, ans, reply_markup=words_buttons())
    await callback.answer()


def get_all_words():
    """Получение слоов из csv файла"""

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
    dp.register_message_handler(first_ten_words, Text(equals='Начать', ignore_case=True))
    dp.register_message_handler(start_command_words, Text(equals='Слова', ignore_case=True))
