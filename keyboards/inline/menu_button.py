from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.callback_data import CallbackData
from backend.models import *


async def get_my_money():
    keyboard = ReplyKeyboardMarkup()
    key1 = KeyboardButton(text="Barcha keshbeklar")
    keyboard.add(key1)
    keyboard.resize_keyboard = True
    return keyboard


async def get_admin():
    keyboard = ReplyKeyboardMarkup()
    key1 = KeyboardButton(text="📊 Barcha keshbeklar ro'yxati")
    key2 = KeyboardButton(text="🗂 Yangi ro'yxat yuklash")
    keyboard.add(key1, key2)
    keyboard.resize_keyboard = True
    return keyboard


async def get_or_back():
    keyboard = ReplyKeyboardMarkup()
    key2 = KeyboardButton(text="🔙 Ortga qaytish")
    key3 = KeyboardButton(text="📑 Hisobotni yuklab olish")
    keyboard.add(key2, key3)
    keyboard.resize_keyboard = True
    return keyboard


async def confirm():
    keyboard = ReplyKeyboardMarkup()
    key1 = KeyboardButton(text="✅🧹 Tasdiqlash")
    key2 = KeyboardButton(text="❌ Bekor qilish")
    keyboard.add(key1, key2)
    keyboard.resize_keyboard = True
    return keyboard


async def file_back():
    keyboard = ReplyKeyboardMarkup()
    key1 = KeyboardButton(text="🔙 Ortga qaytish")
    keyboard.add(key1)
    keyboard.resize_keyboard = True
    return keyboard

async def menu_buutin():
    keyboard = ReplyKeyboardMarkup(one_time_keyboard=True)
    key1 = KeyboardButton(text=" Xodim qo'shish")
    key2 = KeyboardButton(text="Bugungi ro'yxat")
    key3 = KeyboardButton(text="Oylik ro'yxat")
    key4 = KeyboardButton(text="Ma'lum oy uchun xisobot")
    keyboard.add(key1, key2)
    keyboard.add(key3, key4)
    keyboard.resize_keyboard = True
    return keyboard

async def cancel():
    keyboard = ReplyKeyboardMarkup()
    key1 = KeyboardButton(text="🔙 Bekor qilish")
    keyboard.add(key1)
    keyboard.resize_keyboard = True
    return keyboard

async def year_keyboard(years):
    inline_keyboard = []
    for i in years:
        inline_keyboard.append([InlineKeyboardButton(text=f"{i}", callback_data=i)])
    inline_keyboard.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"back_menu")])
    markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return markup


Moths = {1: 'Yanvar', 2: 'Fevral', 3: 'Mart', 4: 'Aprel', 5: 'May', 6: 'Iyun', 7: 'Iyul', 8: 'Avgust', 9: 'Sentabr',
         10: 'Oktyabr', 11: 'Noyabr', 12: 'Dekabr', }


async def month_keyboard(date):
    inline_keyboard = []
    for i in date:
        inline_keyboard.append([InlineKeyboardButton(text=f"{Moths[i]}", callback_data=i)])
    inline_keyboard.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"back_menu")])
    markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return markup