from datetime import datetime, timedelta
from math import ceil
from sqlalchemy import select, update, func, and_, cast, Integer
from database.engine import session_maker

import app.time_calc as tc

from database.models import User, Payment

async def set_user(chat_tg_id: int, new_user_username: str):
    async with session_maker() as session:
        user = await session.scalar(select(User).where(User.user_tg_chat_id == chat_tg_id))
        if not user:
            session.add(User(
                user_tg_chat_id=chat_tg_id,
                username=new_user_username
            ))
            await session.commit()
            return None
        return True

async def set_user_name(chat_tg_id: int, new_user_name: str):
    async with session_maker() as session:
        user = await session.scalar(select(User).where(User.user_tg_chat_id == chat_tg_id))
        user.name = new_user_name
        await session.commit()

async def set_user_timezone(user_chat_id: int, user_timezone: int):
    async with session_maker() as session:
        stmt = update(User).where(User.user_tg_chat_id == user_chat_id).values(user_timezone=user_timezone)
        await session.execute(stmt)
        await session.commit()

async def set_user_birthday(user_chat_id: int, user_birthday: datetime):
    async with session_maker() as session:
        stmt = update(User).where(User.user_tg_chat_id == user_chat_id).values(user_birthday=user_birthday)
        await session.execute(stmt)
        await session.commit()

async def get_user_dates(user_chat_id: int):
    async with session_maker() as session:
        user = await session.scalar(select(User).where(User.user_tg_chat_id == user_chat_id))
        return (user.user_birthday, user.user_timezone)
    
async def set_notification_time(user_chat_id: int, notification_time: str):
    async with session_maker() as session:
        user = await session.scalar(select(User).where(User.user_tg_chat_id == user_chat_id))
        user.notification_time_user_tz = notification_time
        user.notification_time_server_tz = tc.get_notification_time_server_tz(notification_time, user.user_timezone)
        user.user_status = 'active'
        await session.commit()

async def update_notification_time(user_chat_id: int, notification_time: str):
    async with session_maker() as session:
        user = await session.scalar(select(User).where(User.user_tg_chat_id == user_chat_id))
        user.notification_time_user_tz = notification_time
        user.notification_time_server_tz = tc.get_notification_time_server_tz(notification_time, user.user_timezone)
        await session.commit()

async def get_users_to_notify():
    async with session_maker() as session:
        current_time = datetime.now()
        cur_time_hh_mm = current_time.strftime("%H:%M")
        stmt = (
            select(
                User.user_tg_chat_id,
                User.user_birthday,
                User.user_timezone,
                User.subscription_end,
                User.name,
                cast(
                    func.date_part('day', User.subscription_end - func.now()),
                    Integer
                ).label('days_remaining')
            )
            .where(
                and_(
                    User.user_status == 'active',
                    User.subscription_end > current_time,
                    User.notification_time_server_tz == cur_time_hh_mm
                )
            )
        )

        result = await session.execute(stmt)
        return result.all()
    
async def update_user_timezone(user_chat_id: int, new_user_timezone: int):
    async with session_maker() as session:
        user = await session.scalar(select(User).where(User.user_tg_chat_id == user_chat_id))
        if user.user_timezone and user.notification_time_server_tz:
            new_notifs_time_server_tz = tc.update_user_tz(
                old_user_tz=user.user_timezone,
                new_user_tz=new_user_timezone,
                old_notifs_time_server_tz=user.notification_time_server_tz)
            user.notification_time_server_tz = new_notifs_time_server_tz
        user.user_timezone = new_user_timezone
        await session.commit()

async def get_user_profile_info(user_chat_id: int):
    async with session_maker() as session:
        user = await session.scalar(select(User).where(User.user_tg_chat_id == user_chat_id))
        cur_user_time = None
        if user.user_timezone or user.user_timezone == 0:
            cur_user_time = (datetime.now() + timedelta(hours=user.user_timezone)).strftime("%d.%m.%Y %H:%M")
        birthday = None
        if user.user_birthday:
            birthday = user.user_birthday.strftime("%d.%m.%Y")
        notifs_time = user.notification_time_user_tz
        subscription_end = 'Укажите часовой пояс'
        if user.user_timezone or user.user_timezone == 0:
            subscription_end = (user.subscription_end + timedelta(hours=user.user_timezone)).strftime("%d.%m.%Y %H:%M")
        is_subscription_active = True
        if user.subscription_end < datetime.now():
            subscription_end = subscription_end + ' (истекла)'
            is_subscription_active = False
        return {'cur_user_time_str' : cur_user_time,
                'birthday_str': birthday,
                'notifs_time_str': notifs_time,
                'subscription_end_str': subscription_end,
                'user_birthday_dt': user.user_birthday,
                'user_timezone_int': user.user_timezone,
                'user_name': user.name,
                'is_subscription_active': is_subscription_active,
                'is_user_timezone': bool(user.user_timezone or user.user_timezone == 0),
                'user_status': user.user_status
                }
    
async def update_user_birthday(user_chat_id: int, new_user_birthday: datetime):
    async with session_maker() as session:
        user = await session.scalar(select(User).where(User.user_tg_chat_id == user_chat_id))
        user.user_birthday = new_user_birthday
        await session.commit()

async def get_subscr_end(user_chat_id: int):
    async with session_maker() as session:
        user = await session.scalar(select(User).where(User.user_tg_chat_id == user_chat_id))
        subscription_end = None
        if user.user_timezone or user.user_timezone == 0:
            subscription_end = (user.subscription_end + timedelta(hours=user.user_timezone)).strftime("%d.%m.%Y %H:%M")
            if user.subscription_end < datetime.now():
                subscription_end = subscription_end + ' (истекла)'
        return subscription_end
    
async def add_payment(user_chat_id: int, uuid: str, amount: int, payment_id: str, description: str, days_number: str):
    async with session_maker() as session:
        session.add(Payment(
            user_tg_chat_id=user_chat_id,
            uuid=uuid,
            amount=amount,
            payment_id=payment_id,
            description=description,
            days_number=days_number
        ))
        await session.commit()

async def payment_is_successed(user_chat_id: int, payment_id: str):
    async with session_maker() as session:
        payment = await session.scalar(select(Payment).where(
            and_(
                Payment.user_tg_chat_id == user_chat_id,
                Payment.payment_id == payment_id
            )
        ))
        user = await session.scalar(select(User).where(User.user_tg_chat_id == user_chat_id))
        if payment and user:
            payment.status = 'succeeded'
            if not payment.is_subscr_prolonged:
                new_subscr_end = None
                if user.subscription_end > datetime.now():
                    new_subscr_end = user.subscription_end + timedelta(days=payment.days_number)
                else:
                    new_subscr_end = datetime.now() + timedelta(days=payment.days_number)
                user.subscription_end = new_subscr_end
                payment.is_subscr_prolonged = True
                new_subscr_end_user_tz = (new_subscr_end + timedelta(hours=user.user_timezone)).strftime("%d.%m.%Y %H:%M")
                await session.commit()
                return f'Подписка успешно продлена до {new_subscr_end_user_tz} ✅\n\nПерейти в профиль - /profile'
        return False

async def prolong_subscription(user_chat_id: int, payment_id: str):
    async with session_maker() as session:
        user = await session.scalar(select(User).where(User.user_tg_chat_id == user_chat_id))
        payment = await session.scalar(select(Payment).where(
            and_(
                Payment.user_tg_chat_id == user_chat_id,
                Payment.payment_id == payment_id
            )
        ))
        if user and payment:
            if payment.status == 'succeeded' and payment.is_subscr_prolonged == False:
                new_subscr_end = user.subscription_end + timedelta(days=payment.days_number)
                user.subscription_end = new_subscr_end
                payment.is_subscr_prolonged = True
                await session.commit()
                return True
            else:
                return False
        else:
            return False
        
async def disable_bot(user_chat_id: int):
    async with session_maker() as session:
        user = await session.scalar(select(User).where(User.user_tg_chat_id == user_chat_id))
        user.user_status = 'disabled'
        await session.commit()

async def activate_bot(user_chat_id: int):
    async with session_maker() as session:
        user = await session.scalar(select(User).where(User.user_tg_chat_id == user_chat_id))
        user.user_status = 'active'
        await session.commit()

async def is_user_full(user_chat_id: int):
    async with session_maker() as session:
        user = await session.scalar(select(User).where(User.user_tg_chat_id == user_chat_id))
        if not user.notification_time_server_tz:
            return False
        if not user.notification_time_user_tz:
            return False
        if not user.user_birthday:
            return False
        if not (user.user_timezone or user.user_timezone == 0):
            return False
        return True

async def is_user_timezone(user_chat_id: int):
    async with session_maker() as session:
        user = await session.scalar(select(User).where(User.user_tg_chat_id == user_chat_id))
        if user.user_timezone or user.user_timezone == 0:
            return True
        else:
            return False
        
async def get_users_for_mailing():
    async with session_maker() as session:
        stmt = (
            select(
                User.user_tg_chat_id,
            )
            .where(
                    User.user_status == 'active',
            )
        )
        result = await session.execute(stmt)
        return result.all()