import logging, messages, db, mainmenu, config, random, asyncio, aioschedule
import traceback
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from buttons import *
from datetime import datetime, timedelta
import server_commands as sc
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from handlers import admin
from glQiwiApi import QiwiP2PClient


storage = MemoryStorage()
bot = Bot(token=config.API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)
qiwi_p2p_client = QiwiP2PClient(secret_p2p=config.QIWI_TOKEN)
logging.basicConfig(level=logging.INFO)
admin.register_handlers_admin(dp)

servers_kb = ReplyKeyboardMarkup(resize_keyboard=True)
servers_kb.add(button_amsterdam, button_london).add(button_cancel)
get_keys_kb = ReplyKeyboardMarkup(resize_keyboard=True)
get_keys_kb.add(button_get_key).add(button_cancel)


@dp.message_handler(content_types=types.ContentTypes.PHOTO)
async def photo_type_selection(message: types.Message):
    button_confirm = InlineKeyboardButton(text='Да, разблокировать доступ', callback_data='confirm_payment')
    button_unconfirm = InlineKeyboardButton(text='Нет, мне нужна помощь', callback_data='unconfirm_payment')
    choice_user_kb = InlineKeyboardMarkup(row_width=1)
    choice_user_kb.add(button_confirm).add(button_unconfirm)
    button_link_user = InlineKeyboardButton(text="Ссылка на пользователя", url=f"tg://user?id={message.from_user.id}")
    link_user_kb = InlineKeyboardMarkup(row_width=1)
    link_user_kb.add(button_link_user)
    await message.answer("Это подтверждение оплаты?", reply_markup=choice_user_kb)
    await bot.send_message(376131047, f'Пользователь с id {message.from_user.id} ({message.from_user.username} / {message.from_user.first_name}) прислал фото', reply_markup=link_user_kb)
    await bot.send_photo(chat_id=376131047, photo=message.photo[-1].file_id)


@dp.callback_query_handler(text="confirm_payment")
async def confirm_payment(callback: types.Message):
    db.add_days(callback.from_user.id)
    next_payment_date = db.when_to_pay(callback.from_user.id)
    
    if not db.is_registered(callback.from_user.id):
        await callback.answer('Я вас не узнаю. Вы зарегистрировались, прежде чем оплачивать?', reply_markup=mainmenu.main_kb(callback.from_user.id))
    else:
        sc.delete_limit(db.get_rdn_id_from_user(callback.from_user.id)[0], db.get_rdn_id_from_user(callback.from_user.id)[1])    
        db.update_flag_blocked(callback.from_user.id, 'false')
        await callback.message.delete()
        await bot.send_message(callback.from_user.id, f"Спасибо, скриншот отправлен на проверку.\n\nДоступ к сервису уже восстановлен.\n\nДата следующей оплаты: до {next_payment_date}\n\nНапомню в день оплаты.")
        await bot.send_message(376131047, f'Пользователь с id {callback.from_user.id} ({callback.from_user.username} / {callback.from_user.first_name}) подтвердил оплату скриншотом')
        #await bot.send_animation(callback.from_user.id, animation='https://i.gifer.com/2Ts.gif')


@dp.callback_query_handler(text="unconfirm_payment")
async def unconfirm_payment(callback: types.Message):
        await callback.message.delete()
        await bot.send_message(callback.from_user.id, f"Ваш скриншот отправлен администратору. Он свяжется с вами в ближайшее время")
        await bot.send_message(376131047, f'Пользователь с id {callback.from_user.id} ({callback.from_user.username} / {callback.from_user.first_name}) нуждается в помощи по скриншоту')


@dp.message_handler(content_types=types.ContentTypes.DOCUMENT)
async def send_to_admin(message: types.Message):
    '''Присылаем документ для подтверждения оплаты'''

    db.add_days(message.from_user.id)
    next_payment_date = db.when_to_pay(message.from_user.id)
    button_link_user = InlineKeyboardButton(text="Ссылка на пользователя", url=f"tg://user?id={message.from_user.id}")
    link_user_kb = InlineKeyboardMarkup(row_width=1)
    link_user_kb.add(button_link_user)
    
    if not db.is_registered(message.from_user.id):
        await message.answer('Я вас не узнаю. Вы зарегистрировались, прежде чем оплачивать?', reply_markup=mainmenu.main_kb(message.from_user.id))
        await bot.send_message(376131047, f'<b>НЕЗАРЕГИСТИРОВАННЫЙ</b> пользователь с id {message.from_user.id} ({message.from_user.username} / {message.from_user.first_name}) прислал фото', reply_markup=link_user_kb)
        await bot.send_photo(chat_id=376131047, photo=message.photo[-1].file_id)
    else:
        sc.delete_limit(db.get_rdn_id_from_user(message.from_user.id)[0], db.get_rdn_id_from_user(message.from_user.id)[1]) 
        db.update_flag_blocked(message.from_user.id, 'false')   
        await message.answer(f"Спасибо, документ отправлен на проверку.\n\nДоступ к сервису восстановлен.\n\nДата следующей оплаты: до {next_payment_date}\n\nНапомню в день оплаты.", reply_markup=mainmenu.main_kb(message.from_user.id))
        #await message.answer("✅ Добавлен 1 месяц доступа к сервису.")
        await bot.send_animation(message.from_user.id, animation='https://i.gifer.com/2Ts.gif')
        await bot.send_message(376131047, f'Пользователь с id {message.from_user.id} ({message.from_user.username} / {message.from_user.first_name}) прислал документ', reply_markup=link_user_kb)
        await bot.send_document(chat_id=376131047, document=message.document.file_id)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):

    button_link_user = InlineKeyboardButton(text="Ссылка на пользователя", url=f"tg://user?id={message.from_user.id}")
    link_user_kb = InlineKeyboardMarkup(row_width=1)
    link_user_kb.add(button_link_user)
    current_time = datetime.now().replace(microsecond=0)
    db.launched_bot(message.from_user.id, current_time)
    
    if db.is_registered(message.from_user.id):
        await message.answer("Мы рады, что вы вернулись! 😇\n\nВыберите нужный пункт меню, чтобы продолжить.", reply_markup=mainmenu.main_kb(message.from_user.id))
    else:
        await bot.send_message(376131047, 'Новый пользователь запустил бота!\n' # Отправляем сообщение админу о запуске бота
                                            f'User id: {message.from_user.id}\n'
                                            f'Имя: {message.from_user.first_name} {message.from_user.last_name}', reply_markup=link_user_kb)
        await message.answer(messages.welcome_message, reply_markup=mainmenu.main_kb(message.from_user.id))


@dp.message_handler(commands=['cmd'])
async def add_key(message: types.Message):
    if message.from_user.id in config.admins:
        await message.reply(f"Доступные команды:\n/start\n/get_user_id\n/get_info\n/get_free_keys\n/set_limit\n/delete_limit")
    else:
        await message.reply(f"Доступ запрещён.")


@dp.message_handler(commands=['ban'])
async def ban():
    users = db.ban()
    count = 0
    inactive_users = []
    amount_of_messages = 0
    for id in users:
        try:
            pay_menu = InlineKeyboardMarkup(row_width=1)
            button_url_qiwi = InlineKeyboardButton(text='Оплатить картой (временно недоступно, уже чиню', callback_data='pay_by_card')
            button_pay_by_phone = InlineKeyboardButton(text='Оплатить переводом', callback_data='pay_by_phone_number')
            pay_menu.insert(button_url_qiwi).insert(button_pay_by_phone)
            await bot.send_message(id, f'Нам очень жаль, но мы вынуждены заблокировать ваши ключи из-за отсутствия оплаты 😞\n\nВы можете восстановить доступ, оплатив {db.get_tariff(id)} рублей, выбрав один из вариантов оплаты ниже.', reply_markup=pay_menu)
            amount_of_messages += 1
            sc.set_limit(db.get_rdn_id_from_user(id)[0], db.get_rdn_id_from_user(id)[1])
            db.update_flag_blocked(id, 'true')
        except:
            count += 1
            inactive_users.append(id)
            sc.set_limit(db.get_rdn_id_from_user(id)[0], db.get_rdn_id_from_user(id)[1])
            db.update_flag_blocked(id, 'true')
    await bot.send_message(376131047, f"Неоплаченные пользователи заблокированы.\nКоличество заблокированных: {len(users)}.")
    

@dp.message_handler(commands=['set_limit'])
async def add_key(message: types.Message):
    sc.set_limit(db.get_rdn_id_from_user(message.from_user.id)[0], db.get_rdn_id_from_user(message.from_user.id)[1], db.get_rdn_id_from_user(message.from_user.id)[2])
    await message.reply("Проверяй блокировку")


@dp.message_handler(commands=['delete_limit'])
async def add_key(message: types.Message):
    sc.delete_limit(db.get_rdn_id_from_user(message.from_user.id)[0], db.get_rdn_id_from_user(message.from_user.id)[1], db.get_rdn_id_from_user(message.from_user.id)[2])
    await message.reply("Проверяй снятие блокировки")


@dp.message_handler(commands=['get_user_id'])
async def add_key(message: types.Message):
    await message.reply(f"Твой user id: {message.from_user.id}" ) 


@dp.message_handler(commands=['get_free_keys'])
async def add_key(message: types.Message):
    await message.reply(f"Количество свободных ключей: {db.get_free_keys()}" )   


@dp.message_handler(commands=['get_info'])
async def get_info(message: types.Message):
    await message.reply(message)


@dp.message_handler(commands=['send_a_reminder'])
async def send_a_reminder():
    users = db.get_ids_who_to_pay_soon() #Возвращает список id пользователей у кого оплата сегодня
    count = 0
    amount_of_messages = 0
    for id in users:
        try:
            pay_menu = InlineKeyboardMarkup(row_width=1)
            button_url_qiwi = InlineKeyboardButton(text='Оплатить картой (временно недоступно, уже чиню', callback_data='pay_by_card')
            button_pay_by_phone = InlineKeyboardButton(text='Оплатить переводом', callback_data='pay_by_phone_number')
            pay_menu.insert(button_url_qiwi).insert(button_pay_by_phone)
            
            if db.was_a_payment(id):
                await bot.send_message(id, f'Пожалуйста, не забудьте оплатить доступ <b>сегодня до 23:59 МСК</b> чтобы продолжить пользоваться VPN', reply_markup=pay_menu)
                amount_of_messages += 1
            else:
                await bot.send_message(id, f'Пробные три дня подходят к концу 😔\nВам понравилась скорость? Понравилось пользоваться нашим VPN?\n\nПожалуйста, не забудьте оплатить доступ <b>сегодня до 23:59 МСК</b> чтобы продолжить пользоваться VPN', reply_markup=pay_menu)
                amount_of_messages += 1
        except:
            count += 1
    await bot.send_message(376131047, f"Уведомления об оплате отправлены.\nКоличество отправленных сообщений: {amount_of_messages}.")


@dp.message_handler(text="Зарегистрироваться")
async def price(message: types.Message):
    if db.is_registered(message.from_user.id): # Проверяем зарегистрирован ли пользователь
        await message.answer(messages.arleady_registered, reply_markup=get_keys_kb) # Если да, возвращаем сообщение arleady_registered
    else:
        user_name = ''
        telegram_username = ''

        if message.from_user.first_name: # Проверяем, указано ли имя и добавляем его к user_name
            user_name += str(message.from_user.first_name)
            user_name += ' '

        if message.from_user.last_name: # Проверяем, указана ли фамилия и добавляем его к user_name
            user_name += str(message.from_user.last_name)

        if message.from_user.username: # Проверяем, указан ли никнейм и добавляем его к telegram_username
            telegram_username += str(message.from_user.username)

        current_time = datetime.now().replace(microsecond=0) # Получаем текущее время
        shutdown_date = current_time.replace(hour=23, minute=59, second=59, microsecond=0) + timedelta(days=3)
        tariff = 250
        db.register(message.from_user.id, db.get_first_free_id(), user_name, telegram_username, current_time, shutdown_date, tariff)
        button_link_user = InlineKeyboardButton(text="Ссылка на пользователя", url=f"tg://user?id={message.from_user.id}")
        link_user_kb = InlineKeyboardMarkup(row_width=1)
        link_user_kb.add(button_link_user)
        
        await bot.send_message(376131047, 'Пользователь зарегистрировался!\n' # Отправляем сообщение админу о регистрации пользователя
                                        f'User id: {message.from_user.id}\n'
                                        f'Имя: {message.from_user.first_name} {message.from_user.last_name}', reply_markup=link_user_kb)
        
        await message.answer(messages.registation_successfully, reply_markup=mainmenu.main_kb(message.from_user.id))
        await bot.send_animation(message.from_user.id, animation='https://i.gifer.com/Be.gif')


@dp.message_handler(text="Стоимость")
async def price(message: types.Message):
    await message.answer(messages.price)


@dp.message_handler(text="О сервисе")
async def about(message: types.Message):
    await message.answer(messages.about)


@dp.message_handler(text="Как оплатить")
async def how_to_pay(message: types.Message):
    await message.answer(messages.how_to_pay, reply_markup=mainmenu.main_kb(message.from_user.id))


@dp.message_handler(text="Оплатить")
async def pay(message: types.Message):
    if db.when_to_pay(message.from_user.id):
        if message.chat.type == 'private':
            pay_menu = InlineKeyboardMarkup(row_width=1)
            button_url_qiwi = InlineKeyboardButton(text='Оплатить картой', callback_data='pay_by_card')
            button_pay_by_phone = InlineKeyboardButton(text='Оплатить переводом', callback_data='pay_by_phone_number')
            pay_menu.insert(button_url_qiwi).insert(button_pay_by_phone)
            await message.answer(f'К оплате: {db.get_tariff(message.from_user.id)}р.\n\nВы можете оплатить двумя способами.\n\nКак вам будет удобнее?', reply_markup=pay_menu)
    else:
        await message.answer(f"Не переживайте, вам не надо платить за VPN!\n\nЭто так здорово! 😸", reply_markup=mainmenu.main_kb(message.from_user.id))


@dp.callback_query_handler(text="pay_by_card")
async def pay(callback: types.Message):
    async with QiwiP2PClient(secret_p2p=config.QIWI_TOKEN, shim_server_url="http://referrerproxy-env.eba-cxcmwwm7.us-east-1.elasticbeanstalk.com/proxy/p2p/") as p2p:
        comment = str(callback.from_user.id) + '_' + str(random.randint(1000, 9999))
        bill = await p2p.create_p2p_bill(amount=db.get_tariff(callback.from_user.id), pay_source_filter=["card"], comment=comment, theme_code="Nykyta-MKpy0OCKJW")
        shim_url = p2p.create_shim_url(bill)
        db.add_check(callback.from_user.id, bill.id)
        await bot.send_message(callback.from_user.id, messages.pay_by_card, reply_markup=buy_menu(url=shim_url, bill=bill.id))


@dp.callback_query_handler(text='pay_by_phone_number')
async def pay_by_phone_number(callback: types.CallbackQuery):
    await bot.send_message(callback.from_user.id, messages.pay_by_phone_number)


@dp.callback_query_handler(text_contains='check_')
async def check(callback: types.CallbackQuery):
    bill = str(callback.data[6:])
    info = db.get_check(bill)
    if info != False:
        try:
            if str(await qiwi_p2p_client.get_bill_status(bill)) == 'PAID':
                db.add_days(callback.from_user.id)
                next_payment_date = db.when_to_pay(callback.from_user.id)
                button_link_user = InlineKeyboardButton(text="Ссылка на пользователя", url=f"tg://user?id={callback.from_user.id}")
                link_user_kb = InlineKeyboardMarkup(row_width=1)
                link_user_kb.add(button_link_user)
                sc.delete_limit(db.get_rdn_id_from_user(callback.from_user.id)[0], db.get_rdn_id_from_user(callback.from_user.id)[1]) 
                db.update_flag_blocked(callback.from_user.id, 'false')  
                await callback.message.edit_reply_markup() 
                await bot.send_message(callback.from_user.id, f"Спасибо, оплата принята.\n\nДоступ к сервису уже восстановлен.\n\nДата следующей оплаты: до {next_payment_date}\n\nНапомню в день оплаты.", reply_markup=mainmenu.main_kb(callback.from_user.id))
                #await bot.send_animation(callback.from_user.id, animation='https://i.gifer.com/2Ts.gif')
                await bot.send_message(376131047, f'Пользователь с id {callback.from_user.id} ({callback.from_user.username} / {callback.from_user.first_name}) подтвердил оплату через QIWI', reply_markup=link_user_kb)
        except:
            await bot.send_message(376131047, f'У пользователя с id {callback.from_user.id} возникло исключение.\n\n{traceback.format_exc()}')
        else:
            await bot.send_message(callback.from_user.id, 'Мы не видим оплату от вас 🧐', reply_markup=buy_menu(False, bill=bill))
    else:
        await bot.send_message(callback.from_user.id, 'Счёт не найден')


@dp.message_handler(text="Получить ключ")
async def get_keys(message: types.Message):
    user_id = str(message.from_user.id)
    if db.is_registered(user_id):
        await message.answer("Выберите страну расположения сервера", reply_markup=servers_kb)
    else:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(button_register).add(button_cancel)
        await message.answer('Вы ещё не зарегистрировались. Пожалуйста, нажмите кнопку "Зарегистрироваться"', reply_markup=keyboard)


@dp.message_handler(text="Великобритания 🇬🇧")
async def get_keys(message: types.Message):
    await message.answer("Скопируй ключ из следующего сообщения и вставь его в приложение Outline")
    await message.answer(db.get_key(message.from_user.id, 'rdn1'), reply_markup=servers_kb)


@dp.message_handler(text="Нидерланды 🇳🇱")
async def get_keys(message: types.Message):
    await message.answer("Скопируй ключ из следующего сообщения и вставь его в приложение Outline")
    await message.answer(db.get_key(message.from_user.id, 'rdn2'), reply_markup=servers_kb)


@dp.message_handler(text="Скачать приложение")
async def get_keys(message: types.Message):
    # Проверяем, зарегистрирован ли пользователь и в зависимости от этого предлагаем или не предлагаем ему получить ключ
    if db.is_registered(message.from_user.id):
        buttons = [
            types.InlineKeyboardButton(text="Outline для IOS", url="https://apps.apple.com/ru/app/outline-app/id1356177741"),
            types.InlineKeyboardButton(text="Outline для Android", url="https://play.google.com/store/apps/details?id=org.outline.android.client&hl=ru&gl=US"),
            types.InlineKeyboardButton(text="Outline для Windows", url="https://raw.githubusercontent.com/Jigsaw-Code/outline-releases/master/client/stable/Outline-Client.exe")
        ]
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)
        await message.answer("Скачать приложение вы можете по ссылкам ниже:", reply_markup=keyboard)
        await message.answer('Скачали? Теперь жмите "Получить ключ" и выбирайте страну.')
    else: 
        buttons = [
            types.InlineKeyboardButton(text="Outline для IOS", url="https://apps.apple.com/ru/app/outline-app/id1356177741"),
            types.InlineKeyboardButton(text="Outline для Android", url="https://play.google.com/store/apps/details?id=org.outline.android.client&hl=ru&gl=US"),
            types.InlineKeyboardButton(text="Outline для Windows", url="https://raw.githubusercontent.com/Jigsaw-Code/outline-releases/master/client/stable/Outline-Client.exe")
        ]
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)
        await message.answer("Скачать приложение вы можете по ссылкам ниже:", reply_markup=keyboard)


@dp.message_handler(text="Дата оплаты")
async def when_to_pay(message: types.Message):
    if db.when_to_pay(message.from_user.id):
        await message.answer(f"Вам необходимо оплатить {db.get_tariff(message.from_user.id)} рублей до {db.when_to_pay(message.from_user.id)} МСК\n\nНе переживайте, я вам напомню в день оплаты.", reply_markup=mainmenu.main_kb(message.from_user.id))
    else:
        await message.answer(f"Не переживайте, вам не надо платить за VPN!\n\nЭто так здорово! 😸", reply_markup=mainmenu.main_kb(message.from_user.id))


@dp.message_handler(text="Главное меню")
async def get_main_menu(message: types.Message):
    await message.answer("Вы отменили текущее действие", reply_markup=mainmenu.main_kb(message.from_user.id))    


@dp.message_handler(text_contains='ss://') 
async def get_all_message(message: types.Message):
    buttons = [
            types.InlineKeyboardButton(text="Outline для IOS", url="https://apps.apple.com/ru/app/outline-app/id1356177741"),
            types.InlineKeyboardButton(text="Outline для Android", url="https://play.google.com/store/apps/details?id=org.outline.android.client&hl=ru&gl=US"),
            types.InlineKeyboardButton(text="Outline для Windows", url="https://raw.githubusercontent.com/Jigsaw-Code/outline-releases/master/client/stable/Outline-Client.exe")
        ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    await message.answer("Этот ключ нужно вставить в приложение Outline.\n\nНиже появились кнопки для скачивания приложения.", reply_markup=keyboard)


@dp.message_handler(text=["Помощь", "помощь", "Help", "help"])
async def cancel(message: types.Message):
    button_link_user = InlineKeyboardButton(text="Ссылка на пользователя", url=f"tg://user?id={message.from_user.id}")
    link_user_kb = InlineKeyboardMarkup(row_width=1)
    link_user_kb.add(button_link_user)
    await message.answer("Просьба о помощи отправлена администратору. Он напишет вам со своего аккаунта в течении 5 минут.", reply_markup=mainmenu.main_kb(message.from_user.id))
    await bot.send_message(376131047, f'Пользователь с id {message.from_user.id} ({message.from_user.username} / {message.from_user.first_name} {message.from_user.last_name}) нуждается в помощи', reply_markup=link_user_kb)  


@dp.message_handler(text=["Тариф 200", "тариф 200"])
async def cancel(message: types.Message):
    button_link_user = InlineKeyboardButton(text="Ссылка на пользователя", url=f"tg://user?id={message.from_user.id}")
    link_user_kb = InlineKeyboardMarkup(row_width=1)
    link_user_kb.add(button_link_user)
    db.set_tariff(message.from_user.id)
    await message.answer("Вам установлен тариф 200 рублей / мес.", reply_markup=mainmenu.main_kb(message.from_user.id))
    await bot.send_message(376131047, f'Пользователь с id {message.from_user.id} ({message.from_user.username} / {message.from_user.first_name} {message.from_user.last_name}) установил тариф 200 рублей', reply_markup=link_user_kb)  


@dp.message_handler(content_types='text') 
async def get_all_message(message: types.Message):
    await message.answer("К сожалению, я ещё не умею общаться как Siri или Алиса и не понимаю вас.\n\nЕсли у вас возникли трудности, напишите \"Помощь\" и мы поможем вам.", reply_markup=mainmenu.main_kb(message.from_user.id))


async def reminder():
    aioschedule.every().day.at("08:00").do(send_a_reminder)
    aioschedule.every().day.at("00:05").do(ban)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
    asyncio.create_task(reminder())


if __name__ == '__main__':  
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
    