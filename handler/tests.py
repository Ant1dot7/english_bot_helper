from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from create_bot import dp, bot
from buttons.client_buttons import tests_inline_button, answer_for_test_button
from data_base.data_base import get_questions
import asyncio
import aioredis
import json


# answer_dict = {}


async def get_tests(message: types.Message):
    """Выдаем все тесты пользователю для выбора"""

    await message.delete()
    await message.answer('Вот тесты для прохождения \U0001F4DA:', reply_markup=tests_inline_button())


@dp.callback_query_handler(Text(startswith='test_'))
async def start_test(callback: types.CallbackQuery):
    """Начало теста. Получаем тест из ответа пользователя, заносим
    в словарь и присваиваем номер вопроса для конкретного пользователя"""

    test = callback.data.split('_')[-1]
    questions = await get_questions(test)
    async with aioredis.from_url("redis://localhost") as redis:
        if not await redis.exists('english_tests'):
            answer_dict = {}
        else:
            answer_dict = json.loads(await redis.get('english_tests'))
        answer_dict[callback.from_user.id] = [questions, 1]
        await redis.set('english_tests', json.dumps(answer_dict))
    await bot.send_message(callback.from_user.id, f'Вопрос 1 из {len(answer_dict[callback.from_user.id][0])}:\n{questions[0][1]}', reply_markup=answer_for_test_button())
    await callback.answer()


@dp.callback_query_handler(Text(startswith='answer_'))
async def get_answer(callback: types.CallbackQuery):
    """После ответа на первый вопрос (и последующие) проверяем на правильность ответа.
    Узнаем был ли это последний вопрос в данном тесте или нет. Если да завершаем. Иначе выдаем следующий вопрос"""

    user = str(callback.from_user.id)
    async with aioredis.from_url("redis://localhost") as redis:
        answer_dict = json.loads(await redis.get('english_tests'))
        number_questions = answer_dict[user][1]
        answer = callback.data.split('_')[-1]
        last_questions = answer_dict[user][0][number_questions - 1]  # получаем предыдущий вопрос чтоб ответить, был ли правильный ответ
        if answer == last_questions[-1]:
            await bot.send_message(user, '✅ Ваш ответ правильный ✅')
        else:
            await bot.send_message(user, f'❌ Вы ошиблись ❌.\nПравильный ответ: {last_questions[-1]}')

        await bot.edit_message_reply_markup(user, message_id=callback.message.message_id, reply_markup=None)
        await asyncio.sleep(2)
        if len(answer_dict[user][0]) == number_questions:  # проверяем последний ли вопрос в тесте или нет
            del answer_dict[user]
            await bot.send_message(user, 'Вот тесты для прохождения \U0001F4DA:', reply_markup=tests_inline_button())
            await callback.answer()
        else:
            questions = answer_dict[user][0][number_questions]
            answer_dict[user][1] += 1
            await redis.set('english_tests', json.dumps(answer_dict))
            await bot.send_message(user, f'Вопрос {answer_dict[user][1]} из {len(answer_dict[user][0])}\n{questions[1]}', reply_markup=answer_for_test_button())
            await callback.answer()


def register_test_handlers(dp: Dispatcher):
    dp.register_message_handler(get_tests, Text(equals=['\U0001F4DA Тесты \U0001F4DA', '/tests'], ignore_case=True))
