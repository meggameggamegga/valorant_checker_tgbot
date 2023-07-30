from aiogram.dispatcher.filters.state import StatesGroup, State


class StartState(StatesGroup):
    log_pass = State()


#dp.message_handler(Command('start'))#state
#sync def start_cmnd(message:types.Message):
#   await message.answer('Привет')


#dp.message_handler(content_types=types.ContentTypes.TEXT)
#sync def auth_cmnd(message: types.Message):
#   #Тут проверяю все и тд. и тп
#   await message.edit_text('Хочу отредачить уже тут')