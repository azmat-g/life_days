from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import os
from dotenv import find_dotenv, load_dotenv

import database.requests as rq
import app.keyboards as kb

from datetime import datetime

admin_router = Router()

class mailing_message(StatesGroup):
    message_text = State()
    message_properties = State()

@admin_router.message(Command('send_mailing'))
async def send_mailing(message: Message, bot: Bot, state: FSMContext):
    admin_chat_id = int(os.getenv('MY_OWN_ID'))
    if message.chat.id == admin_chat_id:
        await bot.send_message(
            chat_id=os.getenv('MY_OWN_ID'),
            text='Отправь текст уведомления:'
        )
        await state.set_state(mailing_message.message_text)
        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.message_id
        )

@admin_router.message(mailing_message.message_text)
async def is_mailing_message_correct(message: Message, bot: Bot, state: FSMContext):
    await bot.send_message(
        chat_id=message.chat.id,
        text=message.text,
        entities=message.entities,
        reply_markup=kb.is_meiling_text_correct
    )
    await bot.delete_message(
        chat_id=message.chat.id,
        message_id=message.message_id
    )

@admin_router.callback_query(F.data == 'correct_mailing')
async def send_mailing(callback: CallbackQuery, bot: Bot, state: FSMContext):
    users = await rq.get_users_for_mailing()
    for user in users:
        try:
            await bot.send_message(
                chat_id=user[0],
                text=callback.message.text,
                entities=callback.message.entities,
                reply_markup=kb.delete_this_message
            )
        except Exception as e:
            await bot.send_message(
            chat_id=os.getenv('ADMIN_CHAT_ID'),
            text=f'Ошибка у пользователя chat_id: {user[0]}, время: {datetime.now().strftime('%d.%m.%Y, %H:%M:%S')}:\n\n{e}.',
            disable_notification=True
        )
    await bot.edit_message_text(
        text='Рассылка отправлена!',
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=kb.delete_this_message
    )
    await state.clear()

@admin_router.callback_query(F.data == 'incorrect_mailing')
async def incorrect_mailing(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(
        chat_id=os.getenv('MY_OWN_ID'),
        text='Отправь текст уведомления:'
    )
    await state.set_state(mailing_message.message_text)
    await bot.delete_message(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id
    )

@admin_router.callback_query(F.data == 'cancel_mailing')
async def incorrect_mailing(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await bot.delete_message(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id
    )
    await state.clear()