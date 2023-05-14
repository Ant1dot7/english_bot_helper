import sqlite3
from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)


def start_menu_butons():
    """Создание кнопок на стартовом меню"""

    button_listening = KeyboardButton('\U0001F3B5 Аудирование \U0001F3B5')
    button_word = KeyboardButton('\U0001F4DD Слова \U0001F4DD')
    button_test = KeyboardButton('\U0001F4DA Тесты \U0001F4DA')
    menu_buttons = ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder='Choose one').add(button_listening).add(button_word).add(button_test)  # row, insert, add
    return menu_buttons


def listening_menu():
    """Создание кнопок после выбора <Аудирование> """

    easy_texts = KeyboardButton('\U0001F600 Easy texts')
    medium_texts = KeyboardButton('\U0001F914 Medium texts')
    hard_texts = KeyboardButton('\U0001F92F Hard texts')
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


def words_menu():
    """Создание кнопок после выбора <Слова> """

    begin = KeyboardButton('\U0001F3C1 Начать \U0001F3C1')
    repeat_words = KeyboardButton('\U0001F504 Повторить слова \U0001F504')
    del_words = KeyboardButton('\U0000274C Удалить сохраненные записи \U0000274C')
    word_buttons = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(begin).add(repeat_words).add(del_words)
    return word_buttons


def tests_inline_button():
    """Создаем кнопки со всеми тестами"""

    base = sqlite3.connect('data_base/english_texts.db')
    cur = base.cursor()
    cur.execute(f"SELECT * FROM test ")
    all_tests = cur.fetchall()
    base.close()
    tests_buttons = InlineKeyboardMarkup(row_width=2)
    for test in all_tests:
        button = InlineKeyboardButton(test[1] + '\U0001F4DA', callback_data=f'test_{test[1]}')
        tests_buttons.insert(button)
    return tests_buttons


def answer_for_test_button():
    """Четыре кнопки с выбором ответа"""

    answer_button = InlineKeyboardMarkup(row_width=2)
    A = InlineKeyboardButton('A', callback_data='answer_A')
    B = InlineKeyboardButton('B', callback_data='answer_B')
    C = InlineKeyboardButton('C', callback_data='answer_C')
    D = InlineKeyboardButton('D', callback_data='answer_D')
    answer_button.insert(A).insert(B).insert(C).insert(D)
    return answer_button


def button_show_more_remember_button(number):
    show_more = InlineKeyboardButton(text="Показать ещё \U0001F4DC", callback_data='more_word')
    remember_button = InlineKeyboardButton(text="Сохранить для повторения \U0001F4BE", callback_data=f'save_{number}')
    kb = InlineKeyboardMarkup(row_width=1).add(show_more).add(remember_button)
    return kb
