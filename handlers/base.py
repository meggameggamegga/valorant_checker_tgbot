import json
import re

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, state

from checker import ClientAcc
from db.base_db import DataBase
from keyboards.inline import auth_menu, cb

from main import bot,dp
from states.state import StartState
from valo_lib import Auth

db = DataBase('test.db')


from aiogram import types
from aiogram.dispatcher import FSMContext



@dp.message_handler(Command('start'), state='*')
async def start_cmnd(message: types.Message, state: FSMContext):
    cur_state = await state.get_state()
    if cur_state:
        await state.reset_state()

    if not db.user_exist(message.from_user.id):
        db.add_user(message.from_user.id)


    welcome_message = (
        f'👋 Добро пожаловать, {message.from_user.first_name}!\n'
        f'Я бот-чекер игры Valorant. Воспользуйтесь доступными командами для проверки своей коллекции скинов и другой информации. '
        f'Для начала работы нажмите кнопку "Войти".'
    )

    await message.answer(welcome_message, parse_mode=types.ParseMode.MARKDOWN,reply_markup=auth_menu('Login'))

@dp.callback_query_handler(cb.filter(action='exit'),state='*')
@dp.callback_query_handler(cb.filter(action='cancel'),state='*')
@dp.callback_query_handler(cb.filter(action='login'),state='*')
async def auth_cmdn(call:types.CallbackQuery,state:FSMContext):
    cur_state = await state.get_state()
    if cur_state:
        await state.reset_state()
    welcome_message = (
        'Чтобы авторизоваться, напишите ваш логин и пароль через двоеточие.\n'
        '🔐 Пример: *username:password*'
    )
    await call.message.edit_text(welcome_message, parse_mode=types.ParseMode.MARKDOWN,reply_markup=auth_menu())
    await StartState.log_pass.set()



@dp.message_handler(state=StartState.log_pass, content_types=types.ContentTypes.TEXT)
async def auth_cmnd(message:types.Message, state: FSMContext):
    if len(message.text.split(':')) != 2:
        await message.answer('⚠Формат неверный, попробуйте еще раз.',reply_markup=auth_menu('Cancel'))  # reply_markup отмена
    else:
        username, password = message.text.split(':')
        client = ClientAcc(username=username, password=password)
        result = await client.start()
        async with state.proxy() as data:
            data['username'] = username
            data['password'] = password
        if result:
            await message.delete()
            await message.answer(f'✅ Авторизация прошла успешно!\n'
                                 f'👋 Привет, *{result["name"]}*!\n'
                                 f'📍 Твой регион: *{result["region"].upper()}*', reply_markup=auth_menu(menu='Auth'),
                                 parse_mode=types.ParseMode.MARKDOWN)
            await state.reset_state(with_data=False)
        else:
            await message.answer('❌ Аккаунт не валиден',reply_markup=auth_menu('Login'))
            await state.reset_state()

@dp.callback_query_handler(cb.filter(action='skins'))  # state
async def get_my_skins(call:types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        username = data['username']
        password = data['password']
    client = ClientAcc(username=username, password=password)
    items = await client.start('e7c63390-eda7-46e0-bb7a-a6abdacd2433')
    # Тут хранятся все мои ID скинов
    my_skin_codes = [item['ItemID'] for item in items['Entitlements']]
    # ID всех скинов
    with open('new_skins.json', 'r', encoding='UTF8') as skins_file:
        skins_data = json.load(skins_file)
    skin_names = []
    # Итерируется по значениям ключей ID скина
    for skin in skins_data.values():
        # Если скин ID в моем инвентаре
        if skin['uuid'] in my_skin_codes:
            # Добавляем в список
            skin_names.append(skin['names'])

    if skin_names:
        answer_skins = '🎮 Твоя коллекция скинов 🎮:\n\n'
        for index, skin_name in enumerate(skin_names, start=1):
            answer_skins += f'{index}. {skin_name}\n'
    else:
        answer_skins = '🚫 У вас пока нет скинов в коллекции. 🚫'

    await call.message.edit_text(f'{answer_skins}\n'
                         f'🛍️ Всего скинов: {len(skin_names)}',reply_markup=auth_menu('Auth'))



@dp.callback_query_handler(cb.filter(action='store'))#state
async def get_my_skins(call:types.CallbackQuery,state:FSMContext):
    answer_text = '🎁 Ваш магазин состоит из 🎁:\n\n'
    async with state.proxy() as data:
        username = data['username']
        password = data['password']
    client = ClientAcc(username=username,password=password)
    items_store = await client.start(store=True)
    # Мои скины
    skin_names = {}
    # Получить скины из магазина (ItemsID)
    my_skins_store =[items for items in items_store['SkinsPanelLayout']['SingleItemOffers']]

    #Берем базу со скинами
    with open('new_skins.json', 'r', encoding='UTF8') as skins_file:
        skins_data = json.load(skins_file)
    for skin in skins_data.values():
        # Если скин ID в моем инвентаре
        if skin['uuid'] in my_skins_store:
            for items in items_store['SkinsPanelLayout']['SingleItemStoreOffers']:
                price = [price for price in items['Cost'].values()][0]
                #rint(price)
                skin_names[skin["names"]]=price
    time_store = items_store['SkinsPanelLayout']['SingleItemOffersRemainingDurationInSeconds']
    for name,price in skin_names.items():
        answer_text+=f'{name}-{price}\n'
    await call.message.edit_text(f'{answer_text}\n'
                         f'⏳ Время окончания: {int(time_store/3600)}ч.',reply_markup=auth_menu('Auth'))


@dp.callback_query_handler(cb.filter(action='account'))
async def get_account_info(call:types.CallbackQuery,state:FSMContext):
    ranks = {
        0: "UNRANKED",
        1: "Unused1",
        2: "Unused2",
        3: "IRON 1",
        4: "IRON 2",
        5: "IRON 3",
        6: "BRONZE 1",
        7: "BRONZE 2",
        8: "BRONZE 3",
        9: "SILVER 1",
        10: "SILVER 2",
        11: "SILVER 3",
        12: "GOLD 1",
        13: "GOLD 2",
        14: "GOLD 3",
        15: "PLATINUM 1",
        16: "PLATINUM 2",
        17: "PLATINUM 3",
        18: "DIAMOND 1",
        19: "DIAMOND 2",
        20: "DIAMOND 3",
        21: "ASCENDANT 1",
        22: "ASCENDANT 2",
        23: "ASCENDANT 3",
        24: "IMMORTAL 1",
        25: "IMMORTAL 2",
        26: "IMMORTAL 3",
        27: "RADIANT"
    }
    async with state.proxy() as data:
        username = data['username']
        password = data['password']
    client = ClientAcc(username=username,password=password)
    accounts = await client.start(account=True)
    rank = ranks[accounts['Rank']]
    last_match = accounts['last_match']
    VP = accounts['VP']
    Kingdom = accounts['Kingdom']
    RP = accounts['RadiantPoints']
    await call.message.edit_text(f'🏆 Информация о игроке\n'
                         f'🔹Ранг:{rank}\n'
                         f'🔹VP:{VP}\n'
                         f'🔹Kingdom:{Kingdom}\n'
                         f'🔹RP:{RP}\n'
                         f'🔹Дата последнего матча:{last_match}',reply_markup=auth_menu('Auth'))



@dp.callback_query_handler(cb.filter(action='support'),state='*')
async def support_cmnd(call:types.CallbackQuery,state:FSMContext):
    cur_state = await state.get_state()
    if cur_state:
        await state.reset_state()
    await call.message.edit_text(f'По всем вопросом обращайтесь @meggameggamegga',reply_markup=auth_menu('Login'))

@dp.callback_query_handler(cb.filter(action='back'),state='*')
async def back_cmnd(call:types.CallbackQuery,state:FSMContext):
    cur_state = await state.get_state()
    if cur_state:
        await state.reset_state()
    welcome_message = (
        f'👋 Добро пожаловать, {call.from_user.first_name}!\n'
        f'Я бот-чекер игры Valorant. Воспользуйтесь доступными командами для проверки своей коллекции скинов и другой информации. '
        f'Для начала работы нажмите кнопку "Войти".'
    )

    await call.message.edit_text(welcome_message, parse_mode=types.ParseMode.MARKDOWN, reply_markup=auth_menu('Login'))