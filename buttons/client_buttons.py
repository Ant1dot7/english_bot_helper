from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
import sqlite3


def start_menu_butons():
    """Создание кнопок на стартовом меню"""

    button_listening = KeyboardButton('Аудирование')
    button_word = KeyboardButton('Слова')
    menu_buttons = ReplyKeyboardMarkup(resize_keyboard=True).add(button_listening).add(button_word)  # row, insert, add
    return menu_buttons


def listening_menu():
    """Создание кнопок после выбора <Аудирование> """

    easy_texts = KeyboardButton('Easy texts')
    medium_texts = KeyboardButton('Medium texts')
    hard_texts = KeyboardButton('Hard texts')
    texts_buttons = ReplyKeyboardMarkup(resize_keyboard=True).add(easy_texts).add(medium_texts).insert(hard_texts)
    return texts_buttons


def listening_inline_but():
    """Создание инлайн кнопок после выбора сложности аудио-текста
    Сначала получаем из бд категории сложности, затем формируем для каждой сложности список из имеющихся аудио-текстов
    И передаем данные через словарь в функцию вызова
    """

    base = sqlite3.connect('data_base/english_texts.db')
    cur = base.cursor()
    listening_texts_buttons_dick = {}
    for i in range(1, 4):
        cur.execute(f"SELECT * FROM audio WHERE cat = {i}")
        records = cur.fetchall()  # получили все записи под конкретную категорию
        listening_text_buttons = InlineKeyboardMarkup(row_width=2)
        for rec in records:
            button = InlineKeyboardButton(rec[0], callback_data=f'text_{rec[0]}')  # создаем кнопку каждой записи
            listening_text_buttons.insert(button)
        listening_texts_buttons_dick[i] = listening_text_buttons  # сформированную группу кнопок передаем в словарь под номером категории
    return listening_texts_buttons_dick


show_text = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='Показать текст', callback_data='show_text'))
