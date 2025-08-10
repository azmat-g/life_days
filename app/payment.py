import os
from dotenv import find_dotenv, load_dotenv

import yookassa
from yookassa import Payment
import uuid

load_dotenv(find_dotenv())

yookassa.Configuration.account_id = os.getenv('YOOKASSA_ACCOUNT_ID')
yookassa.Configuration.secret_key = os.getenv('YOKASSA_SECRET_KEY')

def create(amount: str, chat_id: int, payment_description: str):
    id_key = str(uuid.uuid4())
    print('id_key', id_key)
    payment = Payment.create({
        'amount': {
            'value': amount,
            'currency': "RUB"
        },
        'payment_method_data': {
            'type': 'bank_card'
        },
        'confirmation': {
            'type': 'redirect',
            'return_url': 'https://t.me/azmatmerion_bot'
        },
        'capture': True,
        'metadata': {
            'chat_id': chat_id
        },
        'description': payment_description
    }, id_key)

    print('payment_id', payment.id)
    return payment.confirmation.confirmation_url, payment.id, id_key

def check(payment_id):
    payment = yookassa.Payment.find_one(payment_id)
    if payment.status == 'succeeded':
        return payment.metadata
    else:
        return False