from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
import sqlite3


def admin_but():
    button_add_category = KeyboardButton('Добавить категорию')
    button_add_audio = KeyboardButton('Добавить аудио')
    admin_buttons = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(button_add_category).add(button_add_audio)
    return admin_buttons


def categories_but():
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
    start_buttons_admin = ReplyKeyboardMarkup(resize_keyboard=True).add('Аудирование').add('Слова').add('/admin')  # row, insert, add
    return start_buttons_admin
