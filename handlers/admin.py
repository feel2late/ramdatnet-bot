import mainmenu, config, psycopg2, requests, urllib3
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters import Text
urllib3.disable_warnings()


conn = psycopg2.connect(
  database="postgres", 
  user="postgres", 
  password="psqluser", 
  host="localhost", 
  port="5432"
)
cursor = conn.cursor()

class FSMAdmin(StatesGroup):
    user_telegram_id = State()
    action = State()


async def manual_control(message:types.Message):
    """Ручная блокировка пользователей по user telegram id"""
    
    if message.from_user.id in config.admins:
        await FSMAdmin.user_telegram_id.set()
        admin_kb = ReplyKeyboardMarkup(resize_keyboard=True)
        button_cancel = KeyboardButton('Отмена')
        admin_kb.add(button_cancel)
        await message.reply('Укажи user_telegram_id', reply_markup=admin_kb)
    else:
        await message.answer('Доступ запрещён')

async def cancel_handler(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply('Отменено', reply_markup=mainmenu.main_kb(message.from_user.id))

async def get_user_telegram_id(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_telegram_id'] = message.text
    await FSMAdmin.next()
    main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    button_block = KeyboardButton('Заблокировать')
    button_unblock = KeyboardButton('Разблокировать')
    button_cancel = KeyboardButton('Отмена')
    main_kb.add(button_block).add(button_unblock).add(button_cancel)
    await message.reply('Выбери действие', reply_markup=main_kb)
   
async def select_action(message: types.Message, state: FSMContext):
    data = await state.get_data()
    cursor.execute("SELECT rdn1_id, rdn2_id, blocked FROM access WHERE user_telegram_id = %s", (data['user_telegram_id'],))
    result = cursor.fetchone()
    rdn1_id = result[0]
    rdn2_id = result[1]
    if message.text == "Заблокировать":
        requests.put(f'https://146.185.251.151:61236/07Tm1I9T_4ZU6pJmzGGCxQ/access-keys/{rdn1_id}/data-limit', json={"limit": {"bytes": 1000000}}, verify=False)
        requests.put(f'https://45.10.43.184:9615/ZQDD1CinJTLL1jP0x0xSSw/access-keys/{rdn2_id}/data-limit', json={"limit": {"bytes": 1000000}}, verify=False)
        await message.answer(f'ID {rdn1_id}, {rdn2_id} для пользователя с user_telegram_id {data["user_telegram_id"]} заблокированы', reply_markup=mainmenu.main_kb(message.from_user.id))
    elif message.text == "Разблокировать":
        requests.delete(f'https://146.185.251.151:61236/07Tm1I9T_4ZU6pJmzGGCxQ/access-keys/{rdn1_id}/data-limit', verify=False)
        requests.delete(f'https://45.10.43.184:9615/ZQDD1CinJTLL1jP0x0xSSw/access-keys/{rdn2_id}/data-limit', verify=False)
        await message.answer(f'ID {rdn1_id}, {rdn2_id} для пользователя с user_telegram_id {data["user_telegram_id"]} разблокированы', reply_markup=mainmenu.main_kb(message.from_user.id))
    await state.finish()

def register_handlers_admin(dp : Dispatcher):
    dp.register_message_handler(cancel_handler, commands='cancel', state='*')
    dp.register_message_handler(cancel_handler, Text(equals='Отмена', ignore_case=True), state='*')
    dp.register_message_handler(manual_control, commands='manual_control', state=None)
    dp.register_message_handler(get_user_telegram_id, state=FSMAdmin.user_telegram_id)
    dp.register_message_handler(select_action, state=FSMAdmin.action)
