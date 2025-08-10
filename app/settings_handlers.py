from aiogram import Bot, Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.texts as txts
import app.time_calc as tc
import database.requests as rq
import os
import logging

from datetime import datetime

settings_router = Router()

class Settings(StatesGroup):
    user_name = State()
    editing_message_id = State()
    user_cur_date = State()
    user_cur_time = State()
    is_datetime_correct = State()
    user_birthday = State()
    notification_hours = State()
    notification_mins = State()

@settings_router.message(Command('profile'))
async def cmd_settings(message: Message, bot: Bot, state: FSMContext):
    try:
        user_info_list = await rq.get_user_profile_info(message.chat.id)
        bot_message = await bot.send_message(
            chat_id=message.chat.id,
            text=txts.get_profile_info(user_info_list),
            reply_markup=kb.choose_setting,
            parse_mode='HTML'
        )
        await state.update_data(editing_message_id=bot_message.message_id)
        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.message_id
        )
    except Exception as e:
        await bot.send_message(
            chat_id=message.chat.id,
            text='⚠️ Произошла ошибка. Попробуйте позже.\n\nАдминистратор уведомлен.',
            reply_markup=kb.delete_this_message
        )
        await bot.send_message(
            chat_id=os.getenv('ADMIN_CHAT_ID'),
            text=f'Ошибка у пользователя chat_id: {message.chat.id}, username: {message.from_user.username}, время: {datetime.now().strftime('%d.%m.%Y, %H:%M:%S')}:\n\n{e}.',
            disable_notification=True
        )
        logging.exception(e)

@settings_router.callback_query(F.data.startswith('set_'))
async def set_settings(callback: CallbackQuery, bot: Bot, state: FSMContext):
    try:
        text = ''
        keyboard = None
        if callback.data[4:] == 'name':
            text='Как вас зовут? Отправьте имя ответным сообщением.'
            keyboard=kb.delete_name
            await state.set_state(Settings.user_name)
        elif callback.data[4:] == 'timezone':
            text='Выберите Вашу текущую дату:'
            keyboard=await kb.date_choise()
            await state.set_state(Settings.user_cur_date)
        elif callback.data[4:] == 'birthday':
            text=txts.send_birthday
            await state.set_state(Settings.user_birthday)
        elif callback.data[4:] == 'notifs_time':
            is_user_timezone = await rq.is_user_timezone(callback.message.chat.id)
            if is_user_timezone:
                text=txts.choose_notifications_hours
                keyboard=await kb.notifications_hours()
                await state.set_state(Settings.notification_hours)
            else:
                text = txts.timezone_is_unknown
                keyboard=await kb.date_choise()
                await state.set_state(Settings.user_cur_date)
        await bot.edit_message_text(
            text=text,
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            parse_mode='HTML',
            reply_markup=keyboard
        )
    except Exception as e:
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text='⚠️ Произошла ошибка. Попробуйте позже.\n\nАдминистратор уведомлен.',
            reply_markup=kb.delete_this_message
        )
        await bot.send_message(
            chat_id=os.getenv('ADMIN_CHAT_ID'),
            text=f'Ошибка у пользователя chat_id: {callback.message.chat.id}, username: {callback.message.from_user.username}, время: {datetime.now().strftime('%d.%m.%Y, %H:%M:%S')}:\n\n{e}.',
            disable_notification=True
        )
        logging.exception(e)

@settings_router.message(Settings.user_name)
async def set_name(message: Message, state: FSMContext, bot: Bot):
    try:
        data = await state.get_data()
        edit_mess_id = data['editing_message_id']
        if message.text and (len(message.text) <= 30):
            await rq.set_user_name(chat_tg_id=message.chat.id, new_user_name=message.text)
            await bot.edit_message_text(
                text=txts.name_updated(message.text),
                chat_id=message.chat.id,
                message_id=edit_mess_id,
                parse_mode='HTML',
                reply_markup=kb.delete_this_message
            )
            await bot.delete_message(
                chat_id=message.chat.id,
                message_id=message.message_id
            )
            await state.clear()
        else:
            await state.set_state(Settings.user_name)
            await bot.edit_message_text(
                text=txts.send_correct_name,
                chat_id=message.chat.id,
                message_id=edit_mess_id,
                parse_mode='HTML',
                reply_markup=kb.delete_name
            )
            await bot.delete_message(
                chat_id=message.chat.id,
                message_id=message.message_id
            )
    except Exception as e:
        await bot.send_message(
            chat_id=message.chat.id,
            text='⚠️ Произошла ошибка. Попробуйте позже.\n\nАдминистратор уведомлен.',
            reply_markup=kb.delete_this_message
        )
        await bot.send_message(
            chat_id=os.getenv('ADMIN_CHAT_ID'),
            text=f'Ошибка у пользователя chat_id: {message.chat.id}, username: {message.from_user.username}, время: {datetime.now().strftime('%d.%m.%Y, %H:%M:%S')}:\n\n{e}.',
            disable_notification=True
        )
        logging.exception(e)

@settings_router.callback_query(Settings.user_name)
async def delete_name(callback: CallbackQuery, state: FSMContext, bot: Bot):
    try:
        await rq.set_user_name(chat_tg_id=callback.message.chat.id, new_user_name=None)
        await bot.edit_message_text(
            text='Имя удалено.',
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=kb.delete_this_message
        )
        await state.clear()
    except Exception as e:
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text='⚠️ Произошла ошибка. Попробуйте позже.\n\nАдминистратор уведомлен.',
            reply_markup=kb.delete_this_message
        )
        await bot.send_message(
            chat_id=os.getenv('ADMIN_CHAT_ID'),
            text=f'Ошибка у пользователя chat_id: {callback.message.chat.id}, username: {callback.message.from_user.username}, время: {datetime.now().strftime('%d.%m.%Y, %H:%M:%S')}:\n\n{e}.',
            disable_notification=True
        )
        logging.exception(e)

@settings_router.callback_query(Settings.user_cur_date)
async def set_date(callback: CallbackQuery, state: FSMContext, bot: Bot):
    try:
        await state.update_data(user_cur_date=callback.data)
        await state.set_state(Settings.user_cur_time)
        data = await state.get_data()
        edit_mess_id = data['editing_message_id']
        await bot.edit_message_text(
            text=txts.choose_time,
            chat_id=callback.message.chat.id,
            message_id=edit_mess_id,
            reply_markup=await kb.time_choise(time=tc.get_cur_time()))
    except Exception as e:
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text='⚠️ Произошла ошибка. Попробуйте позже.\n\nАдминистратор уведомлен.',
            reply_markup=kb.delete_this_message
        )
        await bot.send_message(
            chat_id=os.getenv('ADMIN_CHAT_ID'),
            text=f'Ошибка у пользователя chat_id: {callback.message.chat.id}, username: {callback.message.from_user.username}, время: {datetime.now().strftime('%d.%m.%Y, %H:%M:%S')}:\n\n{e}.',
            disable_notification=True
        )
        logging.exception(e)

@settings_router.callback_query(Settings.user_cur_time)
async def confirm_datetime(callback: CallbackQuery, state: FSMContext, bot: Bot):
    try:
        await state.update_data(user_cur_time=callback.data)
        await state.set_state(Settings.is_datetime_correct)
        data = await state.get_data()
        edit_mess_id = data['editing_message_id']
        cur_datetime = data['user_cur_date'] + ' ' + data['user_cur_time']
        await bot.edit_message_text(
            text=txts.is_datetime_correct(cur_datetime),
            parse_mode='HTML',
            chat_id=callback.message.chat.id,
            message_id=edit_mess_id,
            reply_markup=kb.is_datetime_correct
        )
    except Exception as e:
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text='⚠️ Произошла ошибка. Попробуйте позже.\n\nАдминистратор уведомлен.',
            reply_markup=kb.delete_this_message
        )
        await bot.send_message(
            chat_id=os.getenv('ADMIN_CHAT_ID'),
            text=f'Ошибка у пользователя chat_id: {callback.message.chat.id}, username: {callback.message.from_user.username}, время: {datetime.now().strftime('%d.%m.%Y, %H:%M:%S')}:\n\n{e}.',
            disable_notification=True
        )
        logging.exception(e)

@settings_router.callback_query(Settings.is_datetime_correct)
async def is_datetime_correct(callback: CallbackQuery, state: FSMContext, bot: Bot):
    try:
        data = await state.get_data()
        edit_mess_id = data['editing_message_id']
        cur_user_datetime = data['user_cur_date'] + ' ' + data['user_cur_time']
        if callback.data == 'dt_is_incorrect':
            await state.set_state(Settings.user_cur_date)
            await bot.edit_message_text(
                text=txts.choose_date,
                chat_id=callback.message.chat.id,
                message_id=edit_mess_id,
                parse_mode='HTML',
                reply_markup=await kb.date_choise())
        elif callback.data == 'dt_is_correct':
            new_user_timezome = tc.get_user_timezone(cur_user_datetime)
            await rq.update_user_timezone(
                user_chat_id=callback.message.chat.id,
                new_user_timezone=new_user_timezome
            )
            await bot.edit_message_text(
                text=txts.timezone_updated,
                chat_id=callback.message.chat.id,
                message_id=edit_mess_id,
                parse_mode='HTML',
                reply_markup=kb.delete_this_message
            )
            await state.clear()
    except Exception as e:
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text='⚠️ Произошла ошибка. Попробуйте позже.\n\nАдминистратор уведомлен.',
            reply_markup=kb.delete_this_message
        )
        await bot.send_message(
            chat_id=os.getenv('ADMIN_CHAT_ID'),
            text=f'Ошибка у пользователя chat_id: {callback.message.chat.id}, username: {callback.message.from_user.username}, время: {datetime.now().strftime('%d.%m.%Y, %H:%M:%S')}:\n\n{e}.',
            disable_notification=True
        )
        logging.exception(e)
        

@settings_router.message(Settings.user_birthday)
async def set_user_birthday(message: Message, state: FSMContext, bot: Bot):
    try:
        is_birthday_correct = tc.is_birthday_correct(message.text)
        data = await state.get_data()
        edit_mess_id = data['editing_message_id']
        if is_birthday_correct:
            user_birthday = tc.birthday_str_to_dt(message.text)
            await rq.update_user_birthday(message.chat.id, user_birthday)
            await bot.edit_message_text(
                text=txts.birthday_updated(message.text),
                chat_id=message.chat.id,
                message_id=edit_mess_id,
                parse_mode='HTML',
                reply_markup=kb.delete_this_message
            )
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            await state.clear()
        else:
            if not message.text:
                await state.set_state(Settings.user_birthday)
                await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                await bot.edit_message_text(
                    text=txts.send_date_in_text,
                    chat_id=message.chat.id,
                    message_id=edit_mess_id,
                    parse_mode='HTML'
                )
            else:
                await state.set_state(Settings.user_birthday)
                await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                await bot.edit_message_text(
                    text=txts.date_is_incorrect(message.text),
                    chat_id=message.chat.id,
                    message_id=edit_mess_id,
                    parse_mode='HTML'
                )
    except Exception as e:
        await bot.send_message(
            chat_id=message.chat.id,
            text='⚠️ Произошла ошибка. Попробуйте позже.\n\nАдминистратор уведомлен.',
            reply_markup=kb.delete_this_message
        )
        await bot.send_message(
            chat_id=os.getenv('ADMIN_CHAT_ID'),
            text=f'Ошибка у пользователя chat_id: {message.chat.id}, username: {message.from_user.username}, время: {datetime.now().strftime('%d.%m.%Y, %H:%M:%S')}:\n\n{e}.',
            disable_notification=True
        )
        logging.exception(e)
    
@settings_router.callback_query(Settings.notification_hours)
async def set_notifications_hours(callback: CallbackQuery, state: FSMContext, bot: Bot):
    try:
        data = await state.get_data()
        edit_mess_id = data['editing_message_id']
        await state.set_state(Settings.notification_mins)
        await bot.edit_message_text(
            text=txts.choose_notifications_mins,
            chat_id=callback.message.chat.id,
            message_id=edit_mess_id,
            reply_markup=await kb.notifications_mins(callback.data[:2])
        )
    except Exception as e:
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text='⚠️ Произошла ошибка. Попробуйте позже.\n\nАдминистратор уведомлен.',
            reply_markup=kb.delete_this_message
        )
        await bot.send_message(
            chat_id=os.getenv('ADMIN_CHAT_ID'),
            text=f'Ошибка у пользователя chat_id: {callback.message.chat.id}, username: {callback.message.from_user.username}, время: {datetime.now().strftime('%d.%m.%Y, %H:%M:%S')}:\n\n{e}.',
            disable_notification=True
        )
        logging.exception(e)

@settings_router.callback_query(Settings.notification_mins)
async def set_notifications_time(callback: CallbackQuery, state: FSMContext, bot: Bot):
    try:
        data = await state.get_data()
        edit_mess_id = data['editing_message_id']
        notification_time = callback.data
        await rq.update_notification_time(callback.message.chat.id, notification_time)
        await bot.edit_message_text(
            text=txts.notifs_time_updated(notification_time),
            chat_id=callback.message.chat.id,
            message_id=edit_mess_id,
            parse_mode='HTML',
            reply_markup=kb.delete_this_message
        )
        await state.clear()
    except Exception as e:
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text='⚠️ Произошла ошибка. Попробуйте позже.\n\nАдминистратор уведомлен.',
            reply_markup=kb.delete_this_message
        )
        await bot.send_message(
            chat_id=os.getenv('ADMIN_CHAT_ID'),
            text=f'Ошибка у пользователя chat_id: {callback.message.chat.id}, username: {callback.message.from_user.username}, время: {datetime.now().strftime('%d.%m.%Y, %H:%M:%S')}:\n\n{e}.',
            disable_notification=True
        )
        logging.exception(e)

@settings_router.callback_query(F.data == 'close_profile')
async def close_profile_infp(callback: CallbackQuery, bot: Bot):
    try:
        await bot.delete_message(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id
        )
    except Exception as e:
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text='⚠️ Произошла ошибка. Попробуйте позже.\n\nАдминистратор уведомлен.',
            reply_markup=kb.delete_this_message
        )
        await bot.send_message(
            chat_id=os.getenv('ADMIN_CHAT_ID'),
            text=f'Ошибка у пользователя chat_id: {callback.message.chat.id}, username: {callback.message.from_user.username}, время: {datetime.now().strftime('%d.%m.%Y, %H:%M:%S')}:\n\n{e}.',
            disable_notification=True
        )
        logging.exception(e)

@settings_router.callback_query(F.data == 'subscription')
async def subscription(callback: CallbackQuery, bot: Bot, state: FSMContext):
    try:
        subscription_end = await rq.get_subscr_end(callback.message.chat.id)
        text, keyboard = None, None
        if subscription_end:
            text = txts.get_subscr_end(subscription_end)
            keyboard = kb.prolong_subscr_btns
        else:
            text = txts.timezone_is_unknown
            keyboard = await kb.date_choise()
            await state.update_data(editing_message_id=callback.message.message_id)
            await state.set_state(Settings.user_cur_date)
        await bot.edit_message_text(
                text=text,
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                parse_mode='HTML',
                reply_markup=keyboard
            )

    except Exception as e:
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text='⚠️ Произошла ошибка. Попробуйте позже.\n\nАдминистратор уведомлен.',
            reply_markup=kb.delete_this_message
        )
        await bot.send_message(
            chat_id=os.getenv('ADMIN_CHAT_ID'),
            text=f'Ошибка у пользователя chat_id: {callback.message.chat.id}, username: {callback.message.from_user.username}, время: {datetime.now().strftime('%d.%m.%Y, %H:%M:%S')}:\n\n{e}.',
            disable_notification=True
        )
        logging.exception(e)

@settings_router.message(Command('subscription'))
async def subscription(message: Message, bot: Bot, state: FSMContext):
    try:
        subscription_end = await rq.get_subscr_end(message.chat.id)
        text, keyboard = None, None
        if subscription_end:
            text = txts.get_subscr_end(subscription_end)
            keyboard = kb.prolong_subscr_btns
        else:
            text = txts.timezone_is_unknown
            keyboard = await kb.date_choise()
            await state.set_state(Settings.user_cur_date)
        bot_message = await bot.send_message(
            chat_id=message.chat.id,
            text=text,
            parse_mode='HTML',
            reply_markup=keyboard
        )
        if not subscription_end:
            await state.update_data(editing_message_id=bot_message.message_id)
        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.message_id
        )
    except Exception as e:
        await bot.send_message(
            chat_id=message.chat.id,
            text='⚠️ Произошла ошибка. Попробуйте позже.\n\nАдминистратор уведомлен.',
            reply_markup=kb.delete_this_message
        )
        await bot.send_message(
            chat_id=os.getenv('ADMIN_CHAT_ID'),
            text=f'Ошибка у пользователя chat_id: {message.chat.id}, username: {message.from_user.username}, время: {datetime.now().strftime('%d.%m.%Y, %H:%M:%S')}:\n\n{e}.',
            disable_notification=True
        )
        logging.exception(e)

@settings_router.callback_query(F.data == 'about_subscription')
async def about_subscription(callback: CallbackQuery, bot: Bot):
    try:
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text=txts.about_subscription,
            parse_mode='HTML',
            reply_markup=kb.delete_this_message
        )
    except Exception as e:
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text='⚠️ Произошла ошибка. Попробуйте позже.\n\nАдминистратор уведомлен.',
            reply_markup=kb.delete_this_message
        )
        await bot.send_message(
            chat_id=os.getenv('ADMIN_CHAT_ID'),
            text=f'Ошибка у пользователя chat_id: {callback.message.chat.id}, username: {callback.message.from_user.username}, время: {datetime.now().strftime('%d.%m.%Y, %H:%M:%S')}:\n\n{e}.',
            disable_notification=True
        )
        logging.exception(e)