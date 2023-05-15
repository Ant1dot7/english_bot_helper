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
    base.execute('CREATE TABLE IF NOT EXISTS test(id INTEGER PRIMARY KEY, title TEXT UNIQUE)')
    base.execute("CREATE TABLE IF NOT EXISTS questions(id INTEGER PRIMARY KEY,question TEXT,test_title TEXT,correct_answer TEXT CHECK(correct_answer IN ('A', 'B', 'C', 'D')),FOREIGN KEY(test_title) REFERENCES test(title))")
    base.execute('CREATE TABLE IF NOT EXISTS pictures(id INTEGER PRIMARY KEY, path TEXT UNIQUE, value TEXT)')
    base.commit()


async def get_audio(title):
    """Получаем аудио по запросу из инлайн кнопки"""

    base = sqlite3.connect('data_base/english_texts.db')
    cur = base.cursor()
    cur.execute("SELECT * FROM audio WHERE title = ?", (title,))
    audio_text = cur.fetchone()
    return audio_text


async def save_words_to_repeat(user_id, words):
    """Сохраняем выбранный пользователем список слов в базу данных"""

    result = base.execute("SELECT words FROM words_repeat WHERE user_id = ?", (user_id,)).fetchone()
    if result is not None and words in result[0]:
        return True
    else:
        count = base.execute("SELECT COUNT(*) FROM words_repeat WHERE user_id = ?", (user_id,)).fetchone()[0]
        if count == 0:
            base.execute("INSERT INTO words_repeat(user_id, words) VALUES (?, ?)", (user_id, words))
        else:
            base.execute("UPDATE words_repeat SET words = words || ? WHERE user_id = ?", (words, user_id))
        base.commit()


async def get_words_to_repeat(user_id):
    """Выдаем сохраненный список слов по запросу 'повторения слов' """

    result = base.execute('SELECT words FROM words_repeat WHERE user_id = ?', (user_id,)).fetchone()
    return result[0] if result else None


async def del_words_to_repeat(user_id):
    """Удаление слов для повторения по запросу"""

    cur.execute('DELETE FROM words_repeat WHERE user_id = ?', (user_id,))
    base.commit()


async def get_questions(test):
    """Получение вопросов для теста, по названию теста"""

    cur.execute(f"SELECT * FROM questions WHERE test_title='{test}'")
    questions = cur.fetchall()
    return questions


async def get_pictures_to_game():
    """Получаем все данные для игры Что на фото
       Делим на список по 5 картинок и выдаем по одной"""

    base = sqlite3.connect('data_base/english_texts.db')
    cur = base.cursor()
    cur.execute('SELECT path, value FROM pictures')
    records = cur.fetchall()
    sublist = [records[i:i + 5] for i in range(0, len(records), 5)]
    return sublist
