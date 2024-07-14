from aiogram import types
from aiogram.types import ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from loader import dp, bot
from keyboards.inline.menu_button import *
import pandas as pd
from utils.db_api.database import *
from data import config

channel_id = config.CHANNEL_ID
uzoman_channel_id = config.UZOMAN_CHANNEL_ID


@dp.message_handler(commands=["start"])
async def handler(message: types.Message):
    print(message.get_args())
    args = message.get_args()
    if args != '':
        user_id = message.from_user.id
        user = await get_employee(user_id)
        if user is None:
            await message.answer('❌ Ushbu foydalanuvchi id bilan hodim topilmadi')
        else:
            cupon = await add_coupon(user_id=message.from_user.id)
            soni = await check_count(cupon)
            if cupon is not None:
                await message.answer('Siz kupondan foydalandizngiz!')
                await bot.send_message(
                    chat_id=channel_id if args != "uzoman" else uzoman_channel_id,
                    text=f"{user.name} - talondan foydalandi.")
            else:
                await message.answer('Siz kupondan bugun 2-marta ✌️ foydalanmoqchisiz. Afsuski buning iloji yo\'q')
            if soni == 100:
                cupons = await not_checked(cupon)
                emps = await get_employees()
                names = []
                counts = []
                for emp in emps:
                    count = 0
                    for cps in cupons:
                        if emp.user_id == cps.user_id:
                            count += 1
                    names.append(emp.name)
                    counts.append(count)
                df = pd.DataFrame({'Sana': f"{cupons[0].date.year}/{cupons[0].date.month}",
                                   'Xodim': names,
                                   'Soni': counts})
                df.to_excel('./xisobot.xlsx')
                doc = open('./xisobot.xlsx', 'rb')
                await bot.send_document(document=doc, chat_id=channel_id, caption=f"Bu {soni} - talon")
                for i in cupons:
                    i.checked = True
                    i.save()
    else:
        await message.answer(f'⚠️ Iltimos botdan qr kod orqali foydalaning 📲')


@dp.message_handler(lambda message: message.text in ['11'], state='*')
async def handler(message: types.Message):
    markup = await menu_buutin()
    await message.answer('Kerakli buyruqni tanlang', reply_markup=markup)


@dp.message_handler(lambda message: message.text in ['🔙 Bekor qilish'], state='*')
async def handler(message: types.Message, state: FSMContext):
    await state.finish()
    markup = await menu_buutin()
    await message.answer('Kerakli buyruqni tanlang', reply_markup=markup)


@dp.message_handler(lambda message: message.text in ['Xodim qo\'shish'], state='*')
async def handler(message: types.Message, state: FSMContext):
    markup = await cancel()
    await message.answer('Xodim user_id sini jo\'nating', reply_markup=markup)
    await state.set_state('get_id')


@dp.message_handler(content_types=types.ContentType.TEXT, state='get_id')
async def handler(message: types.Message, state: FSMContext):
    data = message.text
    markup = await cancel()
    await state.update_data(user_id=data)
    await message.answer('Xodim to\'liq ismini kiriting', reply_markup=markup)
    await state.set_state('get_name')


@dp.message_handler(content_types=types.ContentType.TEXT, state='get_name')
async def handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['user_id']
    await add_employee(user_id=user_id, full_name=message.text)
    await state.finish()
    markup = await menu_buutin()
    await message.answer('Kerakli buyruqni tanlang', reply_markup=markup)


@dp.message_handler(lambda message: message.text in ["Bugungi ro'yxat"], state='*')
async def handler(message: types.Message, state: FSMContext):
    cupons = await list_today()
    emps = await get_employees()
    names = []
    counts = []
    for emp in emps:
        count = 0
        for cps in cupons:
            if emp.user_id == cps.user_id:
                count += 1
        names.append(emp.name)
        counts.append(count)
    df = pd.DataFrame({'Sana': date.today(),
                       'Xodim': names,
                       'Soni': counts})
    df.to_excel('./xisobot.xlsx')

    doc = open('./xisobot.xlsx', 'rb')
    await message.answer_document(document=doc, caption=f"Bugun {len(cupons)}")


@dp.message_handler(lambda message: message.text in ["Oylik ro'yxat"], state='*')
async def handler(message: types.Message, state: FSMContext):
    cupons = await list_this_month()
    emps = await get_employees()
    names = []
    counts = []
    for emp in emps:
        count = 0
        for cps in cupons:
            if emp.user_id == cps.user_id:
                count += 1
        names.append(emp.name)
        counts.append(count)
    df = pd.DataFrame({'Sana': f"{date.today().year}/{date.today().month}",
                       'Xodim': names,
                       'Soni': counts})
    df.to_excel('./xisobot.xlsx')

    doc = open('./xisobot.xlsx', 'rb')
    await message.answer_document(document=doc, caption=f"Ushbu oy {len(cupons)} ta")


@dp.message_handler(lambda message: message.text in ["Ma'lum oy uchun xisobot"], state='*')
async def handler(message: types.Message, state: FSMContext):
    years = []
    orders = await get_cupons()
    for order in orders:
        years.append(order.date.year)
    years = list(dict.fromkeys(years))
    markup = await year_keyboard(years)
    await message.answer(text='Kerakli yilni tanlang 👇', reply_markup=markup)
    await state.set_state('get_year_')


@dp.callback_query_handler(state="get_year_")
async def get_year(call: types.CallbackQuery, state: FSMContext):
    data = call.data
    if data != 'back_menu':
        date = []
        state_data = await state.get_data()
        orders = await get_cupons()
        for order in orders:
            if order.date.year == int(data):
                date.append(order.date.month)
        date = list(dict.fromkeys(date))
        markup = await month_keyboard(date)
        await call.message.edit_text(text='Kerakli oyni tanlang 👇', reply_markup=markup)
        await state.update_data(year=data)
        await state.set_state('get_month_')
    else:
        await call.message.delete()
        await bot.send_message(chat_id=call.from_user.id, text=f".", reply_markup=ReplyKeyboardRemove())
        markup = await menu_buutin()
        await state.finish()
        await bot.send_message(chat_id=call.from_user.id, text='Kerakli buyruqni tanlang 👇', reply_markup=markup)


@dp.callback_query_handler(state="get_month_")
async def get_year(call: types.CallbackQuery, state: FSMContext):
    data = call.data
    if data != 'back_menu':
        cupons = []
        state_data = await state.get_data()
        orders = await get_cupons()
        for order in orders:
            if order.date.year == int(state_data['year']) and order.date.month == int(data):
                cupons.append(order)
        emps = await get_employees()
        names = []
        counts = []
        for emp in emps:
            count = 0
            for cps in cupons:
                if emp.user_id == cps.user_id:
                    count += 1
            names.append(emp.name)
            counts.append(count)
        df = pd.DataFrame({'Sana': f"{cupons[0].date.today().year}/{cupons[0].date.today().month}",
                           'Xodim': names,
                           'Soni': counts})
        df.to_excel('./xisobot.xlsx')
        doc = open('./xisobot.xlsx', 'rb')
        await call.message.delete()
        await bot.send_document(chat_id=call.from_user.id, document=doc, caption=f"Ushbu oyda {len(cupons)} ta",
                                reply_markup=ReplyKeyboardRemove())
        markup = await menu_buutin()
        await bot.send_message(chat_id=call.from_user.id, text='Kerakli buyruqni tanlang 👇', reply_markup=markup)
        await state.finish()
    else:
        date = []
        state_data = await state.get_data()
        orders = await get_cupons()
        for order in orders:
            if order.date.year == int(state_data['year']):
                date.append(order.date.year)
        date = list(dict.fromkeys(date))
        markup = await year_keyboard(date)
        await call.message.edit_text(text='Kerakli yilni tanlang 👇', reply_markup=markup)
        await state.update_data(year=data)
        await state.set_state('get_year_')
