from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


button_price = KeyboardButton('Стоимость')
button_about = KeyboardButton('О сервисе')
button_how_to_pay = KeyboardButton('Как оплатить')
button_pay = KeyboardButton('Оплатить')
button_register = KeyboardButton('Зарегистрироваться')
button_get_key = KeyboardButton('Получить ключ')
button_london = KeyboardButton('Великобритания 🇬🇧')
button_amsterdam = KeyboardButton('Нидерланды 🇳🇱')
button_frankfurt = KeyboardButton('Германия 🇩🇪 | Рекомендуем!')
button_download_app = KeyboardButton('Скачать приложение')
button_when_to_pay = KeyboardButton('Дата оплаты')
button_cancel = KeyboardButton('Главное меню')
button_manual_control = KeyboardButton('Ручное управление')

def buy_menu(isUrl=True, url='', bill=''):
    qiwiMenu = InlineKeyboardMarkup(row_width=1)

    if isUrl:
        button_url_qiwi = InlineKeyboardButton(text='Оплатить', url=url)
        qiwiMenu.insert(button_url_qiwi)
        
    button_check_qiwi = InlineKeyboardButton(text='Подтвердить оплату', callback_data='check_'+bill)
    qiwiMenu.insert(button_check_qiwi)
    return qiwiMenu
