from aiogram.types import InlineKeyboardButton,InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

cb = CallbackData('btn','action')

def auth_menu(menu=None):
    if menu =='Auth':
        keyboard = InlineKeyboardMarkup(resize_keyboard=True)
        keyboard.row(InlineKeyboardButton(text='🌟 Коллекция скинов',callback_data=cb.new(action='skins')),
                     InlineKeyboardButton(text='🛍️ Магазин',callback_data=cb.new(action='store')))

        keyboard.add(InlineKeyboardButton(text='ℹИнформация по аккаунту',callback_data=cb.new(action='account')),
                    InlineKeyboardButton(text='🚪 Выход',callback_data=cb.new(action='exit')))
    elif menu =='Login':
        keyboard = InlineKeyboardMarkup(resize_keyboard=True)
        keyboard.add(InlineKeyboardButton(text='🔑 Войти',callback_data=cb.new(action='login')),
                     InlineKeyboardButton(text='👨‍💻 Поддержка',callback_data=cb.new(action='support')))
    elif menu =='Cancel':
        keyboard = InlineKeyboardMarkup(resize_keyboard=True)
        keyboard.add(InlineKeyboardButton(text='🚫 Отмена',callback_data=cb.new(action='cancel')))

    else:
        keyboard = InlineKeyboardMarkup(resize_keyboard=True)
        keyboard.add(InlineKeyboardButton(text='🔙 Назад',callback_data=cb.new(action='back')))
    return keyboard