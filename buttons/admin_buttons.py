import sqlite3
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def admin_but():
    """Админ кнопки на добавление новых позиций в бд"""

    button_add_category = KeyboardButton('Добавить категорию')
    button_add_audio = KeyboardButton('Добавить аудио')
    button_add_picture = KeyboardButton('Добавить картинку')
    admin_buttons = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(button_add_category).add(button_add_audio).add(button_add_picture)
    return admin_buttons


def categories_but():
    """Админ кнопки на выбор категорий для добавления аудио"""

    base = sqlite3.connect('data_base/english_texts.db')
    cur = base.cursor()
    cur.execute('SELECT * FROM category')
    categories = cur.fetchall()
    cat_but = []
    for category in categories:
        title = category[1]  # Значение поля title текущей записи
        button = KeyboardButton(title)  # Создание новой кнопки
        cat_but.append(button)  # Добавление кнопки в список
    categories_buttons = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(*cat_but)
    return categories_buttons


def start_menu_buttons_admin():
    """Админ меню при старте с кнопкой </admin>"""

    start_buttons_admin = ReplyKeyboardMarkup(resize_keyboard=True).\
        insert('\U0001F3B5 Аудирование \U0001F3B5').insert('\U0001F4DD Слова \U0001F4DD').\
        insert('\U0001F4DA Тесты \U0001F4DA').insert('❓ Что на фото? ❓').insert('/admin')  # row, insert, add
    return start_buttons_admin
