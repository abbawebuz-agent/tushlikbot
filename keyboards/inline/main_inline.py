from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.callback_data import CallbackData
from backend.models import *
from utils.db_api.database import *


async def admin_menu():
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Yangi keshbeklar ro'yxatini kiritish", callback_data="add_kash_list")],
            [InlineKeyboardButton(text="👨‍⚕️Alohida doktor uchun hisobotlar", callback_data="kash_by_doctor")],
            [InlineKeyboardButton(text="📈 Umimiy keshbeklar", callback_data="all_kash")],
            [InlineKeyboardButton(text="🗂 Sohalar bo'yicha keshbeklar", callback_data="kash_by_category")],
            [InlineKeyboardButton(text="📅 Bugungi keshbekni ko'rish", callback_data="kash_this_day")],
            [InlineKeyboardButton(text="📅 Tanlangan kun uchun keshbekni ko'rish", callback_data="kash_in_day")],
            [InlineKeyboardButton(text="📅 Shu oy uchun keshbekni ko'rish", callback_data="kash_this_month")],
            [InlineKeyboardButton(text="📅 Tanlangan oy uchun keshbekni ko'rish", callback_data="kash_in_month")],
            [InlineKeyboardButton(text="💊️Alohida preparat bo'yicha keshbeklar", callback_data="kash_by_product")],
        ]
    )
    return markup


async def back_admin_menu():
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"back_admin"),
            ],
        ]
    )
    return markup


async def doctor_in_admin():
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗓 Bugungi kungi keshbekni ko'rish", callback_data="kash_today")],
            [InlineKeyboardButton(text="📅 Alohida kun uchun keshbekni ko'rish", callback_data="kash_day")],
            [InlineKeyboardButton(text="📆 Shu oy uchun keshbekni ko'rish", callback_data="kash_this_month")],
            [InlineKeyboardButton(text="🗒 Alohida oy uchun keshbekni ko'rish", callback_data="kash_month")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"back_admin")],
        ]
    )
    return markup


async def category_keyboard():
    categories = await get_categories()
    inline_keyboard = []
    for i in categories:
        inline_keyboard.append([InlineKeyboardButton(text=i.category_name, callback_data=i.id)])
    inline_keyboard.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"back_menu")])
    markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return markup


async def logout_keyboard():
    keyboard = ReplyKeyboardMarkup()
    key1 = KeyboardButton(text="⬅️Chiqish")
    keyboard.add(key1)
    keyboard.resize_keyboard = True
    return keyboard
