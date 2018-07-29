import datetime
import decimal
import hmac
from mq_bot import MQBot as Bot
from flask import Flask, request, render_template
from peewee import DoesNotExist
import config
from models import User, TopUp, Withdrawal
from flask_basicauth import BasicAuth

app = Flask(__name__)
basic_auth = BasicAuth(app)

app.config['BASIC_AUTH_USERNAME'] = 'worst'
app.config['BASIC_AUTH_PASSWORD'] = 'scumever'

_SUCCESS_RESPONSE = '{status: ok}'
_ETH_WEI = 1000000000000000000
_SUBSCRIPTION_KEY = b'7d11e3af35e60dc9d3635c63a93f6f75f619a11c147c413c426534ebe2a22e23'


@app.route('/confirmed_transaction', methods=['POST'])
def top_up_balance():
    data = request.get_json()

    message = request.get_data()
    signatures = request.headers.get('X-Ethercast-Signature')
    signature512 = signatures.split('; ')[1][7:]

    if not Payments.is_signature_valid(
            signature=signature512,
            message=message,
            subscription_key=_SUBSCRIPTION_KEY
    ):
        return 'Nice try, motherfucker'

    if data['to'] != config.project_eth_address():
        print('Something is really wrong with ethercast')
        return _SUCCESS_RESPONSE

    try:
        user = User.get(wallet=data['from'].lower())
    except DoesNotExist:
        return _SUCCESS_RESPONSE

    amount = int(data['value'], 0) / _ETH_WEI

    Payments.update_levels_deposit(user, amount)

    user.deposit += decimal.Decimal(amount)
    user.save()
    top_up = TopUp.create(
        user=user,
        amount=amount
    )
    bot = Bot(token=config.token())
    bot.send_message(chat_id=user.chat_id, text=f'Ваш депозит был увеличен на {amount} ETH.')

    return _SUCCESS_RESPONSE


@app.route('/approve_withdrawal', methods=['POST'])
@basic_auth.required
def approve_withdrawal():
    id = request.get_json(silent=True)['id']
    withdrawal = Withdrawal.get(id=id)
    withdrawal.approved = True
    withdrawal.save()
    return 'success'


@app.route('/withdrawals')
@basic_auth.required
def withdrawals():
    withdrawals = Withdrawal.select(Withdrawal, User).where(Withdrawal.approved == False).order_by(
        Withdrawal.created_at).join(User)

    return render_template(
        'withdrawals.html',
        withdrawals=withdrawals
    )


@app.route('/')
@basic_auth.required
def statistics():
    def get_chart_data_for_transactions(transactions, columns):
        statistics_data = {}
        for transaction in transactions:
            date = transaction.created_at.strftime("%d %B")
            if date not in statistics_data:
                statistics_data[date] = 0
            statistics_data[date] += float(transaction.amount)

        chart_data = [columns]
        for day in statistics_data.keys():
            chart_data.append([day, statistics_data[day]])

        return chart_data

    now = datetime.datetime.now()
    month_ago = now - datetime.timedelta(days=30)
    withdrawals = Withdrawal.select() \
        .where(Withdrawal.created_at < now) \
        .where(Withdrawal.created_at > month_ago).order_by(Withdrawal.created_at)

    top_ups = TopUp.select() \
        .where(TopUp.created_at < now) \
        .where(TopUp.created_at > month_ago).order_by(TopUp.created_at)

    withdrawal_data = get_chart_data_for_transactions(
        withdrawals,
        [
            'Day',
            'Withdrawals'
        ]
    )

    top_up_data = get_chart_data_for_transactions(
        top_ups,
        [
            'Day',
            'TopUps'
        ]
    )

    registrations = User.select().where(User.created_at < now) \
        .where(User.created_at > month_ago).order_by(User.created_at)

    registration_temp = {}
    for registration in registrations:
        date = registration.created_at.strftime("%d %B")
        if date not in registration_temp:
            registration_temp[date] = 0
        registration_temp[date] += 1

    registration_data = [
        [
            'Day',
            'Registrations'
        ]
    ]

    for day in registration_temp.keys():
        registration_data.append([day, registration_temp[day]])

    return render_template(
        'statistics.html',
        withdrawal_data=withdrawal_data,
        top_up_data=top_up_data,
        registration_data=registration_data
    )


if __name__ == "__main__":
    app.run()


class Payments:
    @staticmethod
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

    @staticmethod
    def is_signature_valid(signature, message, subscription_key):
        enc_message = hmac.new(key=subscription_key, digestmod='sha512')
        enc_message.update(message)
        enc_message = enc_message.hexdigest()
        return str(enc_message) == signature
