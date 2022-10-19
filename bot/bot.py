import math

from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

from settings import bot_config
from api_request import request
from database.orm import add_user, set_user_city, create_report, get_user_city, get_reports


bot = Bot(token=bot_config.bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class ChoiceCityWeather(StatesGroup):
    waiting_city = State()


class SetUserCity(StatesGroup):
    waiting_user_city = State()


@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    add_user(message.from_user.id)
    markup = types.reply_keyboard.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton('Погода в моём городе')
    btn2 = types.KeyboardButton('Погода в другом месте')
    btn3 = types.KeyboardButton('История')
    btn4 = types.KeyboardButton('Установить свой город')
    markup.add(btn1, btn2, btn3, btn4)
    text = f'Привет {message.from_user.first_name}, я бот, который расскжет тебе о погоде на сегодня'
    await message.answer(text, reply_markup=markup)


@dp.message_handler(regexp='Меню')
async def start_message(message: types.Message):
    markup = types.reply_keyboard.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton('Погода в моём городе')
    btn2 = types.KeyboardButton('Погода в другом месте')
    btn3 = types.KeyboardButton('История')
    btn4 = types.KeyboardButton('Установить свой город')
    markup.add(btn1, btn2, btn3, btn4)
    text = f'Привет {message.from_user.first_name}, я бот, который расскжет тебе о погоде на сегодня'
    await message.answer(text, reply_markup=markup)


@dp.message_handler(regexp='Погода в моём городе')
async def get_user_city_weather(message):
    markup = types.reply_keyboard.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('Меню')
    markup.add(btn1)
    city = get_user_city(message.from_user.id)
    if city is None:
        text = 'Пожалуйста установите город проживания'
        markup = types.reply_keyboard.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        btn1 = types.KeyboardButton('Установить свой город')
        markup.add(btn1)
        await message.answer(text, reply_markup=markup)
        return
    data = request.get_weather(city)
    create_report(
        message.from_user.id,
        data['temp'],
        data['feels_like'],
        data['wind_speed'],
        data['pressure_mm'],
        city
    )
    text = f' Погода в {city}\n' \
           f'Температура: {data["temp"]} C\n' \
           f'Ощущается как: {data["feels_like"]} C \n' \
           f'Скорость ветра: {data["wind_speed"]}м/с\n' \
           f'Давление: {data["pressure_mm"]}мм'
    await message.answer(text, reply_markup=markup)


@dp.message_handler(regexp='Погода в другом месте')
async def city_start(message):
    markup = types.reply_keyboard.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('Меню')
    markup.add(btn1)
    text = 'Введите название города'
    await message.answer(text, reply_markup=markup)
    await ChoiceCityWeather.waiting_city.set()


@dp.message_handler(state=ChoiceCityWeather.waiting_city)
async def city_chosen(message: types.Message, state: FSMContext):
    if message.text[0].islower():
        await message.answer('Названия городов пишутся с большой буквы)')
        return
    await state.update_data(waiting_city=message.text)
    markup = types.reply_keyboard.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton('Погода в моём городе')
    btn2 = types.KeyboardButton('Погода в другом месте')
    btn3 = types.KeyboardButton('История')
    btn4 = types.KeyboardButton('Установить свой город')
    markup.add(btn1, btn2, btn3, btn4)
    city = await state.get_data()
    data = request.get_weather(city.get('waiting_city'))
    create_report(
        message.from_user.id,
        data['temp'],
        data['feels_like'],
        data['wind_speed'],
        data['pressure_mm'],
        city.get('waiting_city')
    )
    text = f' Погода в {city.get("waiting_city")}\n'\
           f'Температура: {data["temp"]} C\n'\
           f'Ощущается как: {data["feels_like"]} C \n'\
           f'Скорость ветра: {data["wind_speed"]}м/с\n'\
           f'Давление: {data["pressure_mm"]}мм'
    await message.answer(text, reply_markup=markup)
    await state.finish()


@dp.message_handler(regexp='Установить свой город')
async def set_user_city_start(message: types.Message):
    markup = types.reply_keyboard.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('Меню')
    markup.add(btn1)
    text = 'В каком городе проживаете?'
    await message.answer(text, reply_markup=markup)
    await SetUserCity.waiting_user_city.set()


@dp.message_handler(state=SetUserCity.waiting_user_city)
async def user_city_chosen(message: types.Message, state: FSMContext):
    if message.text[0].islower():
        await message.answer('Названия городов пишутся с большой буквы)')
        return
    await state.update_data(waiting_user_city=message.text)
    user_data = await state.get_data()
    set_user_city(message.from_user.id, user_data.get('waiting_user_city'))
    markup = types.reply_keyboard.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton('Погода в моём городе')
    btn2 = types.KeyboardButton('Погода в другом месте')
    btn3 = types.KeyboardButton('История')
    btn4 = types.KeyboardButton('Установить свой город')
    markup.add(btn1, btn2, btn3, btn4)
    text = f'Запомнил, {user_data.get("waiting_user_city")} ваш город'
    await message.answer(text, reply_markup=markup)
    await state.finish()


@dp.message_handler(regexp='История')
async def get_reports(message: types.Message):
    current_page = 1
    reports = get_reports(message.from_user.id)
    total_pages = math.ceil(len(reports) / 4)
    text = 'История запросов:'
    inline_markup = types.InlineKeyboardMarkup()
    for report in reports[:current_page*4]:
        inline_markup.add(types.InlineKeyboardButton(
            text=f'{report.city} {report.date.day}.{report.date.month}.{report.date.year}',
            callback_data=f'report_{report.id}'
        ))
    current_page += 1
    inline_markup.row(
        types.InlineKeyboardButton(text=f'{current_page-1}/{total_pages}', callback_data='None'),
        types.InlineKeyboardButton(text='Вперёд', callback_data=f'next_{current_page}')
    )
    await message.answer(text, reply_markup=inline_markup)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
