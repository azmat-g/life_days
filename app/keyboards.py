from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import app.time_calc as tc

skip_name = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Пропустить ввод имени ⏩', callback_data='skip_name')]
])

delete_name = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Удалить имя ❌', callback_data='delete_name')]
])

async def date_choise():
    keyboard = InlineKeyboardBuilder()
    dates = tc.get_date_options()
    for date in dates:
        keyboard.add(InlineKeyboardButton(text=date, callback_data=date))
    return keyboard.adjust(1).as_markup()

async def time_choise(time: str):
    keyboard = InlineKeyboardBuilder()
    for i in range(24):
        if i < 10:
            keyboard.add(InlineKeyboardButton(text=f'0{i}:{time}', callback_data=f'0{i}:{time}'))
        else:
            keyboard.add(InlineKeyboardButton(text=f'{i}:{time}', callback_data=f'{i}:{time}'))
    return keyboard.adjust(4).as_markup()

is_datetime_correct = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Все верно✅', callback_data='dt_is_correct')],
    [InlineKeyboardButton(text='Нет, указать заново❌', callback_data='dt_is_incorrect')]
])

async def notifications_hours():
    keyboard = InlineKeyboardBuilder()
    for i in range(24):
        if i < 10:
            keyboard.add(InlineKeyboardButton(text=f'0{i}:00', callback_data=f'0{i}:00'))
        else:
            keyboard.add(InlineKeyboardButton(text=f'{i}:00', callback_data=f'{i}:00'))
    return keyboard.adjust(4).as_markup()

async def notifications_mins(hours: str):
    keyboard = InlineKeyboardBuilder()
    for i in range(0, 56, 5):
        if i < 10:
            keyboard.add(InlineKeyboardButton(text=f'{hours}:0{i}', callback_data=f'{hours}:0{i}'))
        else:
            keyboard.add(InlineKeyboardButton(text=f'{hours}:{i}', callback_data=f'{hours}:{i}'))
    return keyboard.adjust(4).as_markup()

choose_setting = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Имя 👤', callback_data='set_name')],
    [InlineKeyboardButton(text='Часовой пояс 🌏', callback_data='set_timezone')],
    [InlineKeyboardButton(text='Дату рождения 👶🏻', callback_data='set_birthday')],
    [InlineKeyboardButton(text='Время уведомлений ✉️', callback_data='set_notifs_time')],
    [InlineKeyboardButton(text='Продлить подписку 💳', callback_data='subscription')],
    [InlineKeyboardButton(text='Закрыть ❌', callback_data='close_profile')]
])

prolong_subscr_btns = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Продлить на 30 дней, 99 RUB', callback_data='prolong_1_month')],
    [InlineKeyboardButton(text='Продлить на 60 дней, 180 RUB', callback_data='prolong_2_month')],
    [InlineKeyboardButton(text='Продлить на 90 дней, 250 RUB', callback_data='prolong_3_month')],
    [InlineKeyboardButton(text='Подробнее о подписке', callback_data='about_subscription')],
    # [InlineKeyboardButton(text='Оформить подписку, 80 RUB/месяц', callback_data='prolong_monthly')]
    [InlineKeyboardButton(text='Удалить это сообщение ❌', callback_data='delete_this_message')]
])

async def payment_kb(payment_url, payment_id, amount):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f'Оплатить {amount} RUB 💳', url=payment_url)],
        [InlineKeyboardButton(text='Проверить оплату 🔎', callback_data=f'check_payment_{payment_id}')]
    ])
    return keyboard

delete_this_message = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Удалить это сообщение ❌', callback_data='delete_this_message')]
])

subscription_expires = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Продлить 💳', callback_data='subscription')],
    [InlineKeyboardButton(text='Удалить это сообщение ❌', callback_data='delete_this_message')]
])

disable_bot = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да, отключить ❌', callback_data='disable_bot')],
    [InlineKeyboardButton(text='Нет, оставить активным ✅', callback_data='keep_bot_active')]
])

is_meiling_text_correct = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отправить рассылку', callback_data='correct_mailing')],
    [InlineKeyboardButton(text='Заполнить заново', callback_data='incorrect_mailing')],
    [InlineKeyboardButton(text='Отменить', callback_data='cancel_mailing')]
])