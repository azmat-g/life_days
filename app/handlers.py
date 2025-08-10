from aiogram import Bot, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from datetime import datetime

import app.keyboards as kb
import app.time_calc as tc
import database.requests as rq
import app.texts as txts

import os
import logging

router = Router()

class Reg(StatesGroup):
    editing_message_id = State()
    user_name = State()
    user_cur_date = State()
    user_cur_time = State()
    is_datetime_correct = State()
    user_birthday = State()
    # user_life_years = State()
    notification_hours = State()
    notification_mins = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, bot: Bot):
    try:
        is_user = await rq.set_user(message.chat.id, message.from_user.username)
        if not is_user:
            bot_message = await message.answer(
                text=txts.send_name,
                parse_mode='HTML',
                reply_markup=kb.skip_name)
            await rq.set_user(message.chat.id, message.from_user.username)
            await state.update_data(editing_message_id=bot_message.message_id)
            await state.set_state(Reg.user_name)
        else:
            await rq.activate_bot(message.chat.id)
            is_user_full = await rq.is_user_full(message.chat.id)
            if is_user_full:
                text = txts.bot_is_active_full_user
            else:
                text = txts.bot_is_active__not_full_user
            await message.answer(
                text=text,
                reply_markup=kb.delete_this_message
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
            text=f'Ошибка у пользователя chat_id: {message.chat.id}, username: @{message.from_user.username}, время: {datetime.now().strftime('%d.%m.%Y, %H:%M:%S')}:\n\n{e}.',
            disable_notification=True
        )
        logging.exception(e)

@router.message(Reg.user_name)
async def set_name(message: Message, state: FSMContext, bot: Bot):
    try:
        data = await state.get_data()
        edit_mess_id = data['editing_message_id']
        if message.text and (len(message.text) <= 30):
            await rq.set_user_name(chat_tg_id=message.chat.id, new_user_name=message.text)
            await state.set_state(Reg.user_cur_date)
            await bot.edit_message_text(
                text=txts.choose_date_with_name(message.text),
                chat_id=message.chat.id,
                message_id=edit_mess_id,
                parse_mode='HTML',
                reply_markup=await kb.date_choise()
            )
            await bot.delete_message(
                chat_id=message.chat.id,
                message_id=message.message_id
            )
        else:
            await state.set_state(Reg.user_name)
            await bot.edit_message_text(
                text=txts.send_correct_name,
                chat_id=message.chat.id,
                message_id=edit_mess_id,
                parse_mode='HTML',
                reply_markup=kb.skip_name
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

@router.callback_query(Reg.user_name)
async def skip_name(callback: CallbackQuery, state: FSMContext, bot: Bot):
    try:
        data = await state.get_data()
        edit_mess_id = data['editing_message_id']
        await state.set_state(Reg.user_cur_date)
        await bot.edit_message_text(
            text=txts.name_skipped,
            chat_id=callback.message.chat.id,
            message_id=edit_mess_id,
            reply_markup=await kb.date_choise()
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

@router.callback_query(Reg.user_cur_date)
async def set_date(callback: CallbackQuery, state: FSMContext, bot: Bot):
    try:
        await state.update_data(user_cur_date=callback.data)
        await state.set_state(Reg.user_cur_time)
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
    
@router.callback_query(Reg.user_cur_time)
async def confirm_datetime(callback: CallbackQuery, state: FSMContext, bot: Bot):
    try:
        await state.update_data(user_cur_time=callback.data)
        await state.set_state(Reg.is_datetime_correct)
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

@router.callback_query(Reg.is_datetime_correct)
async def is_datetime_correct(callback: CallbackQuery, state: FSMContext, bot: Bot):
    try:
        data = await state.get_data()
        edit_mess_id = data['editing_message_id']
        cur_user_datetime = data['user_cur_date'] + ' ' + data['user_cur_time']
        if callback.data == 'dt_is_incorrect':
            await state.set_state(Reg.user_cur_date)
            await bot.edit_message_text(
                text=txts.choose_date,
                chat_id=callback.message.chat.id,
                message_id=edit_mess_id,
                parse_mode='HTML',
                reply_markup=await kb.date_choise())
        elif callback.data == 'dt_is_correct':
            new_user_timezome = tc.get_user_timezone(cur_user_datetime)
            await rq.set_user_timezone(callback.message.chat.id, new_user_timezome)
            await state.set_state(Reg.user_birthday)
            await bot.edit_message_text(
                text=txts.send_birthday,
                chat_id=callback.message.chat.id,
                message_id=edit_mess_id,
                parse_mode='HTML',
                reply_markup=None
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

@router.message(Reg.user_birthday)
async def set_user_birthday(message: Message, state: FSMContext, bot: Bot):
    try:
        is_birthday_correct = tc.is_birthday_correct(message.text)
        data = await state.get_data()
        edit_mess_id = data['editing_message_id']
        if is_birthday_correct:
            await state.set_state(Reg.notification_hours)
            user_birthday = tc.birthday_str_to_dt(message.text)
            await rq.set_user_birthday(message.chat.id, user_birthday)
            user_birthday, user_timezone = await rq.get_user_dates(message.chat.id)
            cur_day, past_weeks, past_days_after_weeks = tc.get_user_days_weeks(user_birthday, user_timezone)
            await bot.edit_message_text(
                text=txts.days_weeks_left_reg(cur_day, past_weeks, past_days_after_weeks),
                chat_id=message.chat.id,
                message_id=edit_mess_id,
                parse_mode='HTML',
            )
            bot_message = await bot.send_message(
                text=txts.choose_notifications_hours,
                chat_id=message.chat.id,
                reply_markup=await kb.notifications_hours()
            )
            await state.update_data(editing_message_id=bot_message.message_id)
            await bot.delete_message(
                chat_id=message.chat.id,
                message_id=message.message_id
            )
        else:
            if not message.text:
                await state.set_state(Reg.user_birthday)
                await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                await bot.edit_message_text(
                    text=txts.send_date_in_text,
                    chat_id=message.chat.id,
                    message_id=edit_mess_id,
                    parse_mode='HTML'
                )
            else:
                await state.set_state(Reg.user_birthday)
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

@router.callback_query(Reg.notification_hours)
async def set_notifications_hours(callback: CallbackQuery, state: FSMContext, bot: Bot):
    try:
        data = await state.get_data()
        edit_mess_id = data['editing_message_id']
        await state.set_state(Reg.notification_mins)
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

@router.callback_query(Reg.notification_mins)
async def set_notifications_time(callback: CallbackQuery, state: FSMContext, bot: Bot):
    try:
        data = await state.get_data()
        edit_mess_id = data['editing_message_id']
        notification_time = callback.data
        await rq.set_notification_time(callback.message.chat.id, notification_time)
        await bot.edit_message_text(
            text=txts.notification_time_set(notification_time),
            chat_id=callback.message.chat.id,
            message_id=edit_mess_id,
            parse_mode='HTML',
            reply_markup=None
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

@router.callback_query(F.data == 'delete_this_message')
async def delete_this_message(callback: CallbackQuery, bot: Bot):
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

@router.message(Command('disable_bot'))
async def disable_bot(message: Message, bot: Bot):
    try:
        await bot.send_message(
            chat_id=message.chat.id,
            text=txts.disable_bot,
            reply_markup=kb.disable_bot
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

@router.callback_query(F.data == 'disable_bot')
async def yes_disable_bot(callback: CallbackQuery, bot: Bot):
    try:
        await rq.disable_bot(callback.message.chat.id)
        await bot.edit_message_text(
            text=txts.bot_is_disabled,
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=None
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

@router.callback_query(F.data == 'keep_bot_active')
async def yes_disable_bot(callback: CallbackQuery, bot: Bot):
    try:
        await bot.edit_message_text(
            text=txts.bot_stays_active,
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
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