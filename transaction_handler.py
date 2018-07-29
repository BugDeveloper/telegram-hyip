import decimal
import hmac
from flask import Flask, request
from peewee import DoesNotExist
from telegram import Bot
import config
from models import User, TopUp

app = Flask(__name__)

_SUCCESS_RESPONSE = '{status: ok}'
_ETH_WEI = 1000000000000000000
_SUBSCRIPTION_KEY = b'7d11e3af35e60dc9d3635c63a93f6f75f619a11c147c413c426534ebe2a22e23'


def update_levels_deposit(user, amount):
    first_level_upper = user.referral
    if not first_level_upper:
        return
    first_level_upper.first_level_partners_deposit += decimal.Decimal(amount)
    first_level_upper.save()

    second_level_upper = first_level_upper.referral
    if not second_level_upper:
        return
    second_level_upper.second_level_partners_deposit += decimal.Decimal(amount)
    second_level_upper.save()

    third_level_upper = second_level_upper.referral
    if not third_level_upper:
        return
    third_level_upper.third_level_partners_deposit += decimal.Decimal(amount)
    third_level_upper.save()


@app.route('/confirmed_transaction', methods=['POST'])
def top_up_balance():
    data = request.get_json()

    message = request.get_data()
    signatures = request.headers.get('X-Ethercast-Signature')
    signature512 = signatures.split('; ')[1][7:]

    if not _is_signature_valid(signature=signature512, message=message):
        return 'Nice try, motherfucker'

    if data['to'] != config.get_project_eth_address():
        print('Something is really wrong with ethercast')
        return _SUCCESS_RESPONSE

    try:
        user = User.get(wallet=data['from'].lower())
    except DoesNotExist:
        return _SUCCESS_RESPONSE

    amount = int(data['value'], 0) / _ETH_WEI

    update_levels_deposit(user, amount)

    user.deposit += decimal.Decimal(amount)
    user.save()
    top_up = TopUp.create(
        user=user,
        amount=amount
    )
    bot = Bot(token=config.token())
    bot.send_message(chat_id=user.chat_id, text=f'Ваш депозит был увеличен на {amount} ETH.')

    return _SUCCESS_RESPONSE


def _is_signature_valid(signature, message):
    enc_message = hmac.new(key=_SUBSCRIPTION_KEY, digestmod='sha512')
    enc_message.update(message)
    enc_message = enc_message.hexdigest()
    return str(enc_message) == signature
