import sqlite3


async def sql_start():
    """Создание базы данных"""

    global base, cur
    base = sqlite3.connect('data_base/english_texts.db')
    cur = base.cursor()
    if base:
        print('Data base connected OK!')
    base.execute('CREATE TABLE IF NOT EXISTS audio(title TEXT, file TEXT, cat INTEGER, description TEXT, FOREIGN KEY (cat) REFERENCES category(id))')
    base.execute('CREATE TABLE IF NOT EXISTS category(id INTEGER PRIMARY KEY, title TEXT)')
    base.execute('CREATE TABLE IF NOT EXISTS words_repeat(id INTEGER PRIMARY KEY, user_id INTEGER, words TEXT)')
    base.commit()


async def add_cat(state):
    """Добавление категорий в базу данных через /admin в боте"""

    async with state.proxy() as data:
        title = data.get('title')
        query = "INSERT INTO category (title) VALUES (?)"
        base.execute(query, (title,))
        base.commit()


async def add_audio(state):
    """Добавление аудио в базу данных через /admin в боте"""

    async with state.proxy() as data:
        title = data['title']
        audio_file = data['audio']
        category_name = data['category']
        description = data['description']
        category_id = await get_category_id(category_name)
        cur.execute("INSERT INTO audio (title, file, cat, description) VALUES (?, ?, ?, ?)", (title, audio_file, category_id, description))
        base.commit()


async def get_category_id(category_name):
    """Получение категории для добавления аудио в бд"""

    # Получаем ID категории по её названию
    cur.execute("SELECT id FROM category WHERE title=?", (category_name,))
    result = cur.fetchone()
    category_id = result[0]
    return category_id


async def get_audio(title):
    """Получаем аудио по запросу из инлайн кнопки"""

    base = sqlite3.connect('data_base/english_texts.db')
    cur = base.cursor()
    cur.execute("SELECT * FROM audio WHERE title = ?", (title,))
    audio_text = cur.fetchone()
    return audio_text


async def save_words_to_repeat(id, words):
    """Сохраняем выбранный пользователем список слов в базу данных"""

    result = base.execute("SELECT words FROM words_repeat WHERE user_id = ?", (id,)).fetchone()
    if result is not None and words in result[0]:
        return True
    else:
        count = base.execute("SELECT COUNT(*) FROM words_repeat WHERE user_id = ?", (id,)).fetchone()[0]
        if count == 0:
            base.execute("INSERT INTO words_repeat(user_id, words) VALUES (?, ?)", (id, words))
        else:
            base.execute("UPDATE words_repeat SET words = words || ? WHERE user_id = ?", (words, id))
        base.commit()


async def get_words_to_repeat(id):
    """Выдаем сохраненный список слов по запросу 'повторения слов' """

    result = base.execute("SELECT words FROM words_repeat WHERE user_id = ?", (id,)).fetchone()
    return result[0] if result else None



# async def add_cat(state):
#     cur.execute("INSERT INTO category (title) VALUES ('Простые тексты')")
#     base.commit()
#     base.close()
