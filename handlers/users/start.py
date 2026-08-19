from collections import Counter
import logging
import os

from aiogram import types
from aiogram.types import ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.handler import SkipHandler
from loader import dp, bot
from keyboards.inline.menu_button import *
import pandas as pd
from utils.db_api.database import *
from data import config
from filters.admin_filter import IsAdmin

logger = logging.getLogger(__name__)


def _organization_column_labels(organizations: list) -> list:
    bases = [(o.name or "").strip() or o.start_code for o in organizations]
    cnt = Counter(bases)
    labels = []
    for org, base in zip(organizations, bases):
        if cnt[base] > 1:
            labels.append(f"{base} ({org.id})")
        else:
            labels.append(base)
    return labels


def build_employee_org_coupon_df(emps, cupons, organizations: list, period_label):
    labels = _organization_column_labels(organizations)
    rows = []
    for emp in emps:
        row = {"Sana": period_label, "Xodim": emp.name or ""}
        for org, label in zip(organizations, labels):
            n = sum(
                1
                for c in cupons
                if c.user_id == emp.user_id and c.organization_id == org.id
            )
            row[label] = n
        rows.append(row)
    return pd.DataFrame(rows)

LEGACY_CHANNEL_ID = config.CHANNEL_ID
LEGACY_UZOMAN_CHANNEL_ID = config.UZOMAN_CHANNEL_ID


def parse_telegram_user_id_input(text: str):
    """Возвращает (user_id, error_message | None)."""
    s = (text or "").strip()
    if not s:
        return None, "❌ User ID kiriting."
    if not s.isdigit():
        return None, "❌ User ID faqat raqam bo‘lishi kerak."
    uid = int(s)
    if uid <= 0:
        return None, "❌ User ID musbat bo‘lishi kerak."
    return uid, None


@dp.message_handler(commands=["start"])
async def handler(message: types.Message):
    args = (message.get_args() or "").strip()

    if args == "":
        await message.answer('⚠️ Iltimos botdan qr kod orqali foydalaning 📲')
        return

    # Payload convention:
    # - `<org_start_code>` => normal channel
    # - `<org_start_code>:uzoman` => uzoman channel
    # Legacy:
    # - `uzoman` => uzoman channel for the (default) organization
    role = "default"
    org_code = args
    if args == "uzoman":
        role = "uzoman"
        org_code = None
    elif ":" in args:
        maybe_code, maybe_role = args.split(":", 1)
        org_code = maybe_code
        if maybe_role == "uzoman":
            role = "uzoman"

    org = None
    if org_code:
        org = await get_organization_by_start_code(org_code)
    if org is None:
        org = await get_default_organization()

    organization_id = org.id if org is not None else None

    user_id = message.from_user.id
    user = await get_employee(user_id, organization_id=organization_id)
    if user is None:
        await message.answer('❌ Ushbu foydalanuvchi id bilan hodim topilmadi')
        return

    # Запоминаем "текущую" организацию пользователя (для меню без payload)
    await set_employee_active_organization(user_id=user_id, organization_id=organization_id)

    cupon = await add_coupon(user_id=user_id, organization_id=organization_id)
    soni = await check_count(cupon, organization_id=organization_id)

    if cupon is not None:
        await message.answer('Siz kupondan foydalandizngiz!')

        if org is not None:
            target_chat_id = org.uzoman_channel_id if role == "uzoman" and org.uzoman_channel_id is not None else org.channel_id
        else:
            target_chat_id = LEGACY_UZOMAN_CHANNEL_ID if role == "uzoman" else LEGACY_CHANNEL_ID

        await bot.send_message(
            chat_id=target_chat_id,
            text=f"{user.name} - talondan foydalandi.",
        )
    else:
        await message.answer('Siz kupondan bugun 2-marta ✌️ foydalanmoqchisiz. Afsuski buning iloji yo\'q')

    if soni == 100 and cupon is not None:
        cupons = await not_checked(cupon, organization_id=organization_id)
        emps = await get_employees(organization_id=organization_id)

        if not cupons:
            return

        names = []
        counts = []
        for emp in emps:
            count = 0
            for cps in cupons:
                if emp.user_id == cps.user_id:
                    count += 1
            names.append(emp.name)
            counts.append(count)

        year = cupons[0].date.year
        month = cupons[0].date.month
        df = pd.DataFrame(
            {
                "Sana": f"{year}/{month}",
                "Xodim": names,
                "Soni": counts,
            }
        )

        xlsx_name = f'./xisobot_{organization_id or "legacy"}.xlsx'
        df.to_excel(xlsx_name)
        doc = open(xlsx_name, 'rb')

        if org is not None:
            report_chat_id = org.channel_id
        else:
            report_chat_id = LEGACY_CHANNEL_ID

        await bot.send_document(
            document=doc,
            chat_id=report_chat_id,
            caption=f"Bu {soni} - talon",
        )
        await mark_cupons_checked([i.id for i in cupons])


@dp.message_handler(IsAdmin(), commands=["admin"], state='*')
async def handler(message: types.Message):
    markup = await menu_buutin()
    await message.answer('Kerakli buyruqni tanlang', reply_markup=markup)


# Быстрый вход в админ-меню по короткому коду «11».
# Кому доступно — решает фильтр IsAdmin: при ADMIN_OPEN_TO_ALL=true (в .env)
# меню открывается любому, кто напишет «11»; при false — только ADMINS.
@dp.message_handler(IsAdmin(), lambda message: (message.text or "").strip() == '11', state='*')
async def handler(message: types.Message, state: FSMContext):
    await state.finish()
    logger.info(
        "[AdminMenu] kod=11 user_id=%s username=%s open_to_all=%s",
        message.from_user.id,
        message.from_user.username,
        config.ADMIN_OPEN_TO_ALL,
    )
    markup = await menu_buutin()
    await message.answer('Kerakli buyruqni tanlang', reply_markup=markup)


@dp.message_handler(IsAdmin(), lambda message: message.text in ['🔙 Bekor qilish'], state='*')
async def handler(message: types.Message, state: FSMContext):
    await state.finish()
    markup = await menu_buutin()
    await message.answer('Kerakli buyruqni tanlang', reply_markup=markup)


@dp.message_handler(IsAdmin(), lambda message: message.text in ['Add user'], state='*')
async def handler(message: types.Message, state: FSMContext):
    markup = await cancel()
    logger.info(
        "[AddUser:entry] pid=%s from_user_id=%s chat_id=%s",
        os.getpid(),
        message.from_user.id,
        message.chat.id,
    )
    # Если предыдущий сценарий завис на каком-то state (например get_name),
    # начинаем добавление сотрудника с чистого состояния.
    await state.finish()
    await message.answer("Xodim user_id sini jo'nating", reply_markup=markup)
    await state.set_state('get_id')
    try:
        logger.info("[AddUser:entry] pid=%s state_after_set=%s", os.getpid(), await state.get_state())
    except Exception:
        logger.exception("[AddUser:entry] failed to read state")


@dp.message_handler(content_types=types.ContentType.ANY, state='*')
async def handler(message: types.Message, state: FSMContext):
    markup = await cancel()
    try:
        current_state = await state.get_state()
    except Exception:
        current_state = None
        logger.exception("[AddUser:get_id] pid=%s failed to read state", os.getpid())
    if current_state != "get_id":
        raise SkipHandler()
    logger.info(
        "[AddUser:get_id] pid=%s incoming %s",
        os.getpid(),
        {
            "from_user_id": message.from_user.id,
            "chat_id": message.chat.id,
            "content_type": message.content_type,
            "text": message.text,
        },
    )
    uid, err = parse_telegram_user_id_input(message.text)
    logger.info("[AddUser:get_id] pid=%s parsed %s", os.getpid(), {"uid": uid, "err": err})
    if err:
        await message.answer(err, reply_markup=markup)
        return
    admin = await get_employee(message.from_user.id)
    organization_id = admin.active_organization_id if admin is not None else None
    if organization_id is None:
        await message.answer('❌ Avval o\'z tashkilotingiz QR-kodi bilan kirib oling.')
        return
    emp = await ensure_employee_stub(user_id=uid, organization_id=organization_id)
    logger.info(
        "[AddUser:get_id] pid=%s ensure_employee_stub %s",
        os.getpid(),
        {"emp_id": getattr(emp, "id", None), "emp_user_id": getattr(emp, "user_id", None)},
    )
    if emp is None:
        await message.answer('❌ Bazada saqlab bo\'lmadi. Keyinroq qayta urinib ko\'ring.', reply_markup=markup)
        return
    await state.update_data(user_id=uid)
    await message.answer('Xodim to\'liq ismini kiriting', reply_markup=markup)
    await state.set_state('get_name')


@dp.message_handler(content_types=types.ContentType.ANY, state='*')
async def handler(message: types.Message, state: FSMContext):
    try:
        current_state = await state.get_state()
    except Exception:
        current_state = None
        logger.exception("[AddUser:get_name] pid=%s failed to read state", os.getpid())
    if current_state != "get_name":
        raise SkipHandler()

    data = await state.get_data()
    user_id = data.get('user_id')
    admin = await get_employee(message.from_user.id)
    organization_id = admin.active_organization_id if admin is not None else None
    logger.info(
        "[AddUser:get_name] pid=%s incoming %s",
        os.getpid(),
        {
            "from_user_id": message.from_user.id,
            "chat_id": message.chat.id,
            "name_text": message.text,
            "target_user_id": user_id,
            "admin_employee_id": getattr(admin, "id", None),
            "organization_id": organization_id,
        },
    )
    if organization_id is None:
        await message.answer('❌ Avval o\'z tashkilotingiz QR-kodi bilan kirib oling.')
        return
    if user_id is None:
        await message.answer('❌ Qayta urinib ko\'ring: avval user_id yuboring.', reply_markup=await cancel())
        await state.finish()
        return
    emp = await set_employee_name(user_id=user_id, full_name=message.text)
    logger.info(
        "[AddUser:get_name] pid=%s set_employee_name result %s",
        os.getpid(),
        {"emp_id": getattr(emp, "id", None), "emp_user_id": getattr(emp, "user_id", None)},
    )
    if emp is None:
        await message.answer('❌ Ismni saqlab bo\'lmadi.', reply_markup=await cancel())
        return
    await state.finish()
    markup = await menu_buutin()
    await message.answer('Kerakli buyruqni tanlang', reply_markup=markup)



@dp.message_handler(IsAdmin(), lambda message: message.text in ["Current list"], state='*')
async def handler(message: types.Message, state: FSMContext):
    admin = await get_employee(message.from_user.id)
    organization_id = admin.active_organization_id if admin is not None else None
    if organization_id is None:
        await message.answer('❌ Avval o\'z tashkilotingiz QR-kodi bilan kirib oling.')
        return
    cupons = await list_today(organization_id=None)
    emps = await get_employees(organization_id=organization_id)
    orgs = await get_all_organizations()
    df = build_employee_org_coupon_df(emps, cupons, orgs, date.today())
    df.to_excel('./xisobot.xlsx')

    doc = open('./xisobot.xlsx', 'rb')
    await message.answer_document(document=doc, caption=f"Bugun {len(cupons)}")


@dp.message_handler(IsAdmin(), lambda message: message.text in ["Monthly list"], state='*')
async def handler(message: types.Message, state: FSMContext):
    admin = await get_employee(message.from_user.id)
    organization_id = admin.active_organization_id if admin is not None else None
    if organization_id is None:
        await message.answer('❌ Avval o\'z tashkilotingiz QR-kodi bilan kirib oling.')
        return
    cupons = await list_this_month(organization_id=None)
    emps = await get_employees(organization_id=organization_id)
    orgs = await get_all_organizations()
    df = build_employee_org_coupon_df(
        emps,
        cupons,
        orgs,
        f"{date.today().year}/{date.today().month}",
    )
    df.to_excel('./xisobot.xlsx')

    doc = open('./xisobot.xlsx', 'rb')
    await message.answer_document(document=doc, caption=f"Ushbu oy {len(cupons)} ta")


@dp.message_handler(IsAdmin(), lambda message: message.text in ["Choose date"], state='*')
async def handler(message: types.Message, state: FSMContext):
    years = []
    admin = await get_employee(message.from_user.id)
    organization_id = admin.active_organization_id if admin is not None else None
    if organization_id is None:
        await message.answer('❌ Avval o\'z tashkilotingiz QR-kodi bilan kirib oling.')
        return
    orders = await get_cupons(organization_id=None)
    for order in orders:
        years.append(order.date.year)
    years = list(dict.fromkeys(years))
    markup = await year_keyboard(years)
    await message.answer(text='Kerakli yilni tanlang 👇', reply_markup=markup)
    await state.set_state('get_year_')


@dp.callback_query_handler(IsAdmin(), state="get_year_")
async def get_year(call: types.CallbackQuery, state: FSMContext):
    data = call.data
    if data != 'back_menu':
        date = []
        state_data = await state.get_data()
        admin = await get_employee(call.from_user.id)
        organization_id = admin.active_organization_id if admin is not None else None
        if organization_id is None:
            return
        orders = await get_cupons(organization_id=None)
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


@dp.callback_query_handler(IsAdmin(), state="get_month_")
async def get_year(call: types.CallbackQuery, state: FSMContext):
    data = call.data
    if data != 'back_menu':
        cupons = []
        state_data = await state.get_data()
        admin = await get_employee(call.from_user.id)
        organization_id = admin.active_organization_id if admin is not None else None
        if organization_id is None:
            return
        orders = await get_cupons(organization_id=None)
        for order in orders:
            if order.date.year == int(state_data['year']) and order.date.month == int(data):
                cupons.append(order)
        emps = await get_employees(organization_id=organization_id)
        if not cupons:
            return

        orgs = await get_all_organizations()
        df = build_employee_org_coupon_df(
            emps,
            cupons,
            orgs,
            f"{cupons[0].date.year}/{cupons[0].date.month}",
        )

        xlsx_name = f'./xisobot_{organization_id or "legacy"}_{state_data["year"]}_{data}.xlsx'
        df.to_excel(xlsx_name)
        doc = open(xlsx_name, 'rb')
        await call.message.delete()
        await bot.send_document(chat_id=call.from_user.id, document=doc, caption=f"Ushbu oyda {len(cupons)} ta",
                                reply_markup=ReplyKeyboardRemove())
        markup = await menu_buutin()
        await bot.send_message(chat_id=call.from_user.id, text='Kerakli buyruqni tanlang 👇', reply_markup=markup)
        await state.finish()
    else:
        admin = await get_employee(call.from_user.id)
        organization_id = admin.active_organization_id if admin is not None else None
        if organization_id is None:
            return
        orders = await get_cupons(organization_id=None)

        # Вернуться к выбору года (barcha tashkilotlar bo'yicha)
        years = list(dict.fromkeys([order.date.year for order in orders if order.date is not None]))
        markup = await year_keyboard(years)
        await call.message.edit_text(text='Kerakli yilni tanlang 👇', reply_markup=markup)
        await state.set_state('get_year_')



@dp.message_handler(content_types=types.ContentType.ANY, state="*")
async def _debug_any_message(message: types.Message, state: FSMContext):
    """
    Debug helper: logs any incoming message and current FSM state.
    Always passes update to next handlers.
    """
    try:
        cur = await state.get_state()
    except Exception:
        cur = None
    logger.info(
        "[Debug:any_message] pid=%s chat_id=%s user_id=%s content_type=%s text=%r fsm_state=%s",
        os.getpid(),
        message.chat.id,
        getattr(message.from_user, "id", None),
        message.content_type,
        message.text,
        cur,
    )
    raise SkipHandler()