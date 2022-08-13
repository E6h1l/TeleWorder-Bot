import env
import logging
import sqlite3
import queries
import asyncio
import timer
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


#Open Data Base
db = sqlite3.connect(env.get_db_path(), check_same_thread=False)
#Сhecking the existence of tables
queries.check_tables(db)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=env.get_api_key())
dp = Dispatcher(bot=bot, loop=asyncio.get_event_loop(), storage=MemoryStorage())


class Form(StatesGroup):
    word_add = State()
    word_remove = State()
    notifications_on = State()
    notifications_off = State()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """
    This handler will be add user to data base when user sends `/start` command.
    """

    if not queries.create_user(db, message.from_user.id):
        await message.answer("Ви вже навчаєтесь зі мною &#128521\nДля перегляду списку команд нажміть: <b>/help</b> &#128270", parse_mode='HTML')
        return
    
    await message.answer(f"""Привіт, <b>{message.from_user.first_name}</b> &#128075\nЯ <b>Бот-Словник</b>&#128210
Я допоможу тобі вивчити будь-яку мову!\nДля перегляду списку команд нажміть: <b>/help</b> &#128270""", parse_mode='HTML')


@dp.message_handler(commands=['help'])
async def command_list(message: types.Message):
    """
    This handler will be send list of commands when user sends `/help` command.
    """

    await message.answer("""Оберіть потрібну команду:
- <b>/new</b> &#10133 : додати нове слово 
- <b>/remove</b> &#10134 : видалити додане слово
- <b>/list</b> &#128221 : отримати список усіх доданих слів
- <b>/on</b> &#128994 : увімкнути надсилання слів
- <b>/off</b> &#128997 : вимкнути надсилання слів""", parse_mode='HTML')


@dp.message_handler(commands=['new'])
async def add_word(message: types.Message):
    """
    This handler will be add word to data base of commands when user sends `/new` command.
    """
    await message.answer("Будь ласка, введіть слово та через <b>ПРОБІЛ</b> його переклад:", parse_mode='HTML')
    await Form.word_add.set()


@dp.message_handler(commands=['remove'])
async def add_word(message: types.Message):
    """
    This handler will be remove word from data base of commands when user sends `/remove` command.
    """
    await message.answer("Будь ласка, введіть слово яке потрібно видалити:", parse_mode='HTML')
    await Form.word_remove.set()


@dp.message_handler(commands=['list'])
async def get_word_list(message: types.Message):
    """
    This handler will send list of user`s words when user sends `/list` command.
    """
    words_list = queries.get_words(db, message.from_user.id)

    if not words_list:
        await message.answer("Ви ще не додавали слова&#128521\n<b>/new</b> &#10133 : додати нове слово", parse_mode='HTML')
        return
        
    res_str = ''

    for i in words_list:
        for j in i:
            res_str += "<b>" + j + "</b>"

            if i[0] == j:
                res_str += ' - '
			
        res_str += '\n'
    

    await message.answer(res_str+"\nПовернутися до списку команд: <b>/help</b> &#128270", parse_mode='HTML')


@dp.message_handler(commands=['on'])
async def notifications_settings(message: types.Message):
    """
    This handler will on sending words when user sends `/on` command.
    """
    menu = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    ten_minutes = KeyboardButton(text="кожні 10 хвилин")
    fifteen_minutes = KeyboardButton(text="кожні 15 хвилин")
    thirty_minutes = KeyboardButton(text="кожні 30 хвилин")
    one_hour = KeyboardButton(text="кожні 60 хвилин")

    menu.add(ten_minutes, fifteen_minutes, thirty_minutes, one_hour)

    await message.answer("Оберіть можливий період відправки слів у <b>ХВИЛИНАХ</b> &#8595 :", reply_markup=menu, parse_mode='HTML')
    await Form.notifications_on.set()


@dp.message_handler(commands=['off'])
async def notifications_settings(message: types.Message):
    """
    This handler will off sending words when user sends `/off` command.
    """
    try:
        queries.insert_notifications_settings(db, 0, 0, message.from_user.id)
        await message.answer('Надсилання слів вимкнене!')
    except IndexError:
        await message.answer('Щось пішло не так, спробуйте ще раз &#128521\n<b>/off</b> &#10133 : налаштування сповіщень', parse_mode='HTML')


@dp.message_handler(state=Form.word_add)
async def start_add_word(message: types.Message, state: FSMContext):
    """
    Function that add words to DB on 'word_add' state 
    """
    async with state.proxy() as proxy:
        try:
            words = message.text.split()
            queries.create_word(db, words[0].lower(), words[1].lower(), message.from_user.id)
            await message.answer(f'Слово <b> {words[0]} </b> додане до списку!\nПовернутися до списку команд: <b>/help</b> &#128270', parse_mode='HTML')
        except IndexError:
            await message.answer('Слово введене неправильно, спробуйте ще раз &#128521\n<b>/new</b> &#10133 : додати нове слово', parse_mode='HTML')

    await state.finish()


@dp.message_handler(state=Form.word_remove)
async def start_remove_word(message: types.Message, state: FSMContext):
    """
    Function that remove words from DB on 'word_remove' state
    """
    async with state.proxy() as proxy:
        if len(tuple(queries.find_word(db, message.from_user.id, message.text.lower()))) == 0:
            await message.answer(f'Такого слова немає в списку, спробуйте ще раз &#128521\n<b>/remove</b> &#10134 : видалити додане слово', parse_mode='HTML')
        else:
            queries.delete_word(db, message.text.lower())
            await message.answer(f'Слово <b>{message.text}</b> видалене зі списку!\nПовернутися до списку команд: <b>/help</b> &#128270', parse_mode='HTML')
    
    await state.finish()


@dp.message_handler(state=Form.notifications_on)
async def set_notifications_settings(message: types.Message, state: FSMContext):
    """
    Function that enable notifications to users on 'notifications_on' state
    """
    async with state.proxy() as proxy:
        try:
            period = int(message.text.split()[1])

            if period not in [10, 15, 30, 60]:
                await message.answer('Час введений неправильно, спробуйте ще раз &#128521\n<b>/on</b> &#10133 : налаштування сповіщень', parse_mode='HTML')
    
            queries.insert_notifications_settings(db, 1, period, message.from_user.id)
            await message.answer('Надсилання слів увімкнене!')
        except Exception:
            await message.answer('Час введений неправильно, спробуйте ще раз &#128521\n<b>/on</b> &#10133 : налаштування сповіщень', parse_mode='HTML')

    await state.finish()


async def create_timers():
    """
    Function that initialize timers for sending users words
    """
    timer1 = timer.Timer(interval=600, first_immediately=True, timer_name="10 minutes timer", callback=sending_words)
    timer2 = timer.Timer(interval=900, first_immediately=True, timer_name="15 minutes timer", callback=sending_words)
    timer3 = timer.Timer(interval=1800, first_immediately=True, timer_name="30 minutes timer", callback=sending_words)
    timer4 = timer.Timer(interval=3600, first_immediately=True, timer_name="1 hour timer", callback=sending_words)


async def sending_words(interval):
    """
    Function that send words to users
    """
    words = queries.get_words_to_send(db, interval)

    if not len(words):
        queries.update_words_status(db, interval)
        return

    for word in words:
        await bot.send_message(word[2], f'<b>{word[0]}</b> - <b>{word[1]}</b>', parse_mode='HTML')
        queries.word_sent(db, word[2], word[0])

        if not queries.count_words_to_send(db, word[2]):
            queries.update_user_words_status(db, word[2])


if __name__ == '__main__':
    dp.loop.create_task(create_timers())
    executor.start_polling(dp, skip_updates=True)