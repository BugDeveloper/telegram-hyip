from flask import Flask, request


app = Flask(__name__)

_SUCCESS_RESPONSE = '{status: ok}'
_ETH_WEI = 1000000000000000000
_SUBSCRIPTION_KEY = b'7d11e3af35e60dc9d3635c63a93f6f75f619a11c147c413c426534ebe2a22e23'


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

@app.route('/')
def main():
    return 'Welcome'


if __name__ == "__main__":
    app.run()
