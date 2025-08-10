from datetime import datetime
from sqlalchemy import Integer, String, DateTime, func, text, Boolean, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_tg_chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    username: Mapped[str] = mapped_column(String(70), nullable=True)
    name: Mapped[str] = mapped_column(String(30), nullable=True)
    registration_date: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now())
    subscription_end: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("(now() + interval '14 days')"))
    user_status: Mapped[str] = mapped_column(String(10), server_default='reg')
    notification_time_server_tz: Mapped[str] = mapped_column(String(10), nullable=True)
    notification_time_user_tz: Mapped[str] = mapped_column(String(10), nullable=True)
    user_birthday: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    user_timezone: Mapped[int] = mapped_column(Integer, nullable=True)

class Payment(Base):
    __tablename__ = 'payments'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_tg_chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    uuid: Mapped[str] = mapped_column(String(40), nullable=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=True)
    payment_id: Mapped[str] = mapped_column(String(40), nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=True, server_default='pending')
    description: Mapped[str] = mapped_column(String(40), nullable=True)
    days_number: Mapped[int] = mapped_column(Integer, nullable=True)
    is_subscr_prolonged: Mapped[bool] = mapped_column(Boolean, nullable=True, server_default='false')