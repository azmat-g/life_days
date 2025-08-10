from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery

from app.payment import create, check

import app.keyboards as kb
import database.requests as rq
import app.texts as txts

from datetime import datetime

import os
import logging

purchases_router = Router()

@purchases_router.callback_query(F.data.startswith('prolong_'))
async def process_callback_query(callback: CallbackQuery, bot: Bot):
    try:
        action = callback.data[8:]
        description = ''
        text = ''
        amount_for_kb = ''
        days_number = 0
        payment_url, payment_id, uuid = None, None, None
        if action == '1_month':
            description = 'Продление подписки на 30 дней'
            text = txts.prolong_subscription('30', '99')
            # text = 'Продление подписки на 30 дней, 99 RUB\n\nПосле оплаты нажмите "Проверить оплату 🔎"'
            payment_url, payment_id, uuid = create('99.00', callback.message.chat.id, description)
            amount_for_kb = '99'
            days_number = 30
        elif action == '2_month':
            description = 'Продление подписки на 60 дней'
            text = txts.prolong_subscription('60', '180')
            # text = 'Продление подписки на 60 дней, 180 RUB\n\nПосле оплаты нажмите "Проверить оплату 🔎"'
            payment_url, payment_id, uuid = create('180.00', callback.message.chat.id, description)
            amount_for_kb = '180'
            days_number = 60
        elif action == '3_month':
            description = 'Продление подписки на 90 дней'
            text = txts.prolong_subscription('90', '250')
            # text = 'Продление подписки на 90 дней, 250 RUB\n\nПосле оплаты нажмите "Проверить оплату 🔎"'
            payment_url, payment_id, uuid = create('250.00', callback.message.chat.id, description)
            amount_for_kb = '250'
            days_number = 90
        # elif action == 'monthly':
        #     description = 'Оформление ежемесячной подписки'
        #     text = 'Оформление ежемесячной подписки'
        #     payment_url, payment_id = create('80.00', callback.message.chat.id, description)
        
        await rq.add_payment(
            user_chat_id=callback.message.chat.id,
            uuid=uuid,
            amount=int(amount_for_kb),
            payment_id=payment_id,
            description=description,
            days_number=days_number
        )

        await bot.edit_message_text(
            text=text,
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            parse_mode='HTML',
            reply_markup=await kb.payment_kb(payment_url, payment_id, amount_for_kb)
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


@purchases_router.callback_query(F.data.startswith('check_payment_'))
async def check_handler(callback: CallbackQuery, bot: Bot):
    try:
        payment_id = callback.data[14:]
        result = check(payment_id)
        if result:
            text = await rq.payment_is_successed(callback.message.chat.id, payment_id)
            if text:
                await bot.edit_message_text(
                    text=text,
                    chat_id=callback.message.chat.id,
                    message_id=callback.message.message_id,
                    reply_markup=kb.delete_this_message
                )
            else:
                await callback.message.answer(
                    text='Что-то пошло не так, попробуйте оплатить еще раз.',
                    reply_markup=kb.delete_this_message
                )
            # await rq.prolong_subscription(callback.message.chat.id, payment_id)
        else:
            await callback.message.answer(
                text='Что-то пошло не так, попробуйте оплатить еще раз.',
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