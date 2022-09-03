from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from buttons import *
import db


def main_kb(userid):
    if db.is_registered(userid):
        main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
        main_kb.add(button_get_key).add(button_download_app).row(button_price, button_pay, button_when_to_pay, button_about)
        return main_kb
    else:
        main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
        main_kb.add(button_register).row(button_price, button_about)
        return main_kb
    