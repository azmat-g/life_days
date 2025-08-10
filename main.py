import asyncio
from datetime import datetime, timedelta
import logging
import os

from aiogram import Bot, Dispatcher

from logging.handlers import RotatingFileHandler

from database.engine import create_db, drop_db, session_maker
from middlewares.db import DataBaseSession

from app.handlers import router
from app.settings_handlers import settings_router
from app.purchases_handlers import purchases_router
from app.admin_handlers import admin_router
import app.keyboards as kb

from aiogram.fsm.storage.redis import RedisStorage

import database.requests as rq
import app.texts as txts
import app.time_calc as tc

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

storage = RedisStorage.from_url('redis://localhost:6379/0')
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(storage=storage)

def setup_logging():
    os.makedirs('logs', exist_ok=True)
    
    log_format = '%(asctime)s %(levelname)s %(name)s %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    logging.basicConfig(
        level=logging.WARNING,
        format=log_format,
        datefmt=date_format,
        handlers=[
            RotatingFileHandler(
                'logs/bot.log',
                maxBytes=10*1024*1024,
                backupCount=10,
                encoding='utf-8'
            ),
            logging.StreamHandler()
        ]
    )
    
    sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
    sqlalchemy_logger.setLevel(logging.ERROR)
    sqlalchemy_logger.propagate = False

async def send_daily_notifications():
    while True:
        start_time = datetime.now()
        users = await rq.get_users_to_notify()
        # print('users:', users)
        for user in users:
            try:
                cur_day, past_weeks, past_days_after_weeks = tc.get_user_days_weeks(user[1], user[2])
                name = user[4]
                await bot.send_message(
                    chat_id=user[0],
                    text=txts.everyday_notification(cur_day, past_weeks, past_days_after_weeks, name),
                    parse_mode='HTML'
                )
                if user[5] < 3:
                    await bot.send_message(
                        chat_id=user[0],
                        text=txts.subscription_expires(user[3], user[2]),
                        parse_mode='HTML',
                        reply_markup=kb.subscription_expires
                    )
            except Exception as e:
                print(f"Error sending to user {user[0]}: {e}")
                logging.info(f"Error sending to user {user[0]}: {e}")
                await bot.send_message(
                    chat_id=os.getenv('ADMIN_CHAT_ID'),
                    text=f'Ошибка у пользователя chat_id: {user[0]}, name: {user[4]}, время: {datetime.now().strftime('%d.%m.%Y, %H:%M:%S')}:\n\n{e}.',
                    disable_notification=True
                )
                logging.exception(e)

        duration = datetime.now() - start_time
        sleep_time = max(60 - duration.total_seconds(), 0)
        await asyncio.sleep(sleep_time)

async def on_startup(bot):
    print('bot is running')
    logging.info('bot is running')
    run_param = False
    if run_param:
        await drop_db()

    await create_db()

    asyncio.create_task(send_daily_notifications())

async def on_shutdown(bot):
    print('bot stopped')

async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    dp.include_routers(router, settings_router, purchases_router, admin_router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    setup_logging()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')