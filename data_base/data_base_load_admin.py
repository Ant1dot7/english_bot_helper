import sqlite3


async def add_cat(state):
    """Добавление категорий в базу данных через /admin в боте"""

    base = sqlite3.connect('data_base/english_texts.db')
    async with state.proxy() as data:
        title = data.get('title')
        query = "INSERT INTO category (title) VALUES (?)"
        base.execute(query, (title,))
        base.commit()


async def add_audio(state):
    """Добавление аудио в базу данных через /admin в боте"""

    base = sqlite3.connect('data_base/english_texts.db')
    cur = base.cursor()
    async with state.proxy() as data:
        title = data['title']
        audio_file = data['audio']
        category_name = data['category']
        description = data['description']
        category_id = await get_category_id(category_name, cur)
        cur.execute("INSERT INTO audio (title, file, cat, description) VALUES (?, ?, ?, ?)", (title, audio_file, category_id, description))
        base.commit()


async def get_category_id(category_name, cur):
    """Получение категории для добавления аудио в бд"""

    # Получаем ID категории по её названию
    cur.execute("SELECT id FROM category WHERE title=?", (category_name,))
    result = cur.fetchone()
    category_id = result[0]
    return category_id


async def add_picture(state):
    """Загружаем в бд картинку и описание для <Что на фото?>"""

    base = sqlite3.connect('data_base/english_texts.db')
    cur = base.cursor()
    async with state.proxy() as data:
        picture = data['picture']
        description = data['description']
        cur.execute('INSERT INTO pictures (path, value) VALUES (?, ?)', (picture, description))
        base.commit()
