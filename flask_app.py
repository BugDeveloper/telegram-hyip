import datetime
import hmac
import json

from flask import Flask, request, render_template, Response
from peewee import DoesNotExist
import config
from models import User, TopUp, Withdrawal
from flask_basicauth import BasicAuth

app = Flask(__name__)
basic_auth = BasicAuth(app)

app.config['BASIC_AUTH_USERNAME'] = 'worst'
app.config['BASIC_AUTH_PASSWORD'] = 'scumever'

_SUCCESS_RESPONSE = {'status': 'ok'}
_FAIL_RESPONSE = {'status': 'fail'}
_ETH_WEI = 1000000000000000000
_SUBSCRIPTION_KEY = b'7d11e3af35e60dc9d3635c63a93f6f75f619a11c147c413c426534ebe2a22e23'


def is_signature_valid(signature, message, subscription_key):
    enc_message = hmac.new(key=subscription_key, digestmod='sha512')
    enc_message.update(message)
    enc_message = enc_message.hexdigest()
    return str(enc_message) == signature


@app.route('/confirmed_transaction', methods=['POST'])
def top_up_balance():
    data = request.get_json()

    message = request.get_data()
    signatures = request.headers.get('X-Ethercast-Signature')
    signature512 = signatures.split('; ')[1][7:]

    if not is_signature_valid(
            signature=signature512,
            message=message,
            subscription_key=_SUBSCRIPTION_KEY
    ):
        return Response(
            response='Nice try motherfucker',
            status=400,
            mimetype='application/json'
        )

    if data['to'] != config.project_eth_address():
        print('Something is really wrong with ethercast')
        return Response(
            response='Success',
            status=200,
            mimetype='application/json'
        )

    amount = int(data['value'], 0) / _ETH_WEI
    wallet = data['from'].lower()

    try:
        user = User.get(wallet=wallet)
        top_up = TopUp.create(
            user=user,
            amount=amount,
            from_wallet=wallet
        )
    except DoesNotExist:
        top_up = TopUp.create(
            amount=amount,
            received=False,
            from_wallet=wallet
        )

    return Response(
        response='Success',
        status=200,
        mimetype='application/json'
    )

# curl -d '{"value":"0x16337cf446e5fc80", "from":"0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE"}' -H "Content-Type: application/json" -X POST http://167.99.218.143/confirmed_transaction
# curl -d '{"to":"WALLET","value":"0x16337cf446e5fc80", "from":"0xd2ee776d5acf82f8b1799ec3d8e2fb1d74738b59"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:5000/confirmed_transaction

class ValidationError(Exception):
    pass


@app.route('/user_deposit')
@basic_auth.required
def user_deposit():
    return render_template(
        'user_deposit.html'
    )


@app.route('/increase_user_deposit', methods=['POST'])
@basic_auth.required
def increase_user_deposit():
    json = request.get_json(silent=True)
    username = json['username'].lower()
    amount = json['amount']

    try:
        user = User.get(username=username)
    except DoesNotExist as e:
        return Response(
            response='Нет такого юзера',
            status=400,
            mimetype='application/json'
        )

    try:
        amount = float(amount)
    except ValueError:
        return Response(
            response='Не похоже на дробное число',
            status=400,
            mimetype='application/json'
        )

    TopUp.create(
        amount=amount,
        user=user
    )
    return Response(
        response='Успешно',
        status=200,
        mimetype='application/json'
    )


@app.route('/approve_withdrawal', methods=['POST'])
@basic_auth.required
def approve_withdrawal():
    id = request.get_json(silent=True)['id']
    withdrawal = Withdrawal.get(id=id)
    if withdrawal.approved:
        return Response(
            response='Вывод уже был подтвержден',
            status=400,
            mimetype='application/json'
        )
    withdrawal.approved = True
    withdrawal.save()
    return Response(
        response='Успешно',
        status=200,
        mimetype='application/json'
    )


@app.route('/withdrawals')
@basic_auth.required
def withdrawals():
    withdrawals = Withdrawal.select(Withdrawal, User).where(Withdrawal.approved == False) \
        .where(Withdrawal.created_at < datetime.date.today()).order_by(Withdrawal.created_at).join(User)

    return render_template(
        'withdrawals.html',
        withdrawals=withdrawals
    )


@app.route('/lost_top_ups')
@basic_auth.required
def lost_top_ups():
    lost_top_ups = TopUp.select().where(TopUp.received == False)

    return render_template(
        'lost_top_ups.html',
        lost_top_ups=lost_top_ups
    )


@app.route('/received_top_up', methods=['POST'])
@basic_auth.required
def top_up_received():
    json_request = request.get_json(silent=True)
    id = json_request['id']
    username = json_request['username'].lower()
    top_up = TopUp.get(id=id)
    if top_up.received:
        return Response(
            response='Пополнение уже зачислено',
            status=400,
            mimetype='application/json'
        )
    try:
        user = User.get(username=username)
    except DoesNotExist as e:
        return Response(
            response='Нет такого пользователя',
            status=400,
            mimetype='application/json'
        )

    top_up.user = user
    top_up.received = True
    top_up.save()

    return Response(
        response='Успешно',
        status=200,
        mimetype='application/json'
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
