import datetime
from random import uniform
from peewee import DoesNotExist
import config
import mq_bot
from models import User, TopUp, Withdrawal, UserTransfer

test_user = User.get(chat_id=config.test_user_id())
try:
    second_user = User.get(chat_id=1)
except DoesNotExist:
    second_user = User.create(
                chat_id=228,
                username='some_name',
                first_name='Patrick',
                last_name='Jhonson',
                balance=1
            )
now = datetime.datetime.now()
two_weeks_ago = now - datetime.timedelta(days=15)
week_ago = now - datetime.timedelta(days=7)
mq_bot.init()

for i in range(5):
    top_up = TopUp.create(
        user=test_user,
        amount=uniform(0, 1.0),
        created_at=two_weeks_ago,
    )

for i in range(5):
    top_up = TopUp.create(
        amount=uniform(0, 1.0),
        received=False
    )

for i in range(5):
    top_up = TopUp.create(
        user=test_user,
        amount=uniform(0, 1.0),
        created_at=week_ago
    )

transfer_to_user = UserTransfer.create(
    from_user=test_user,
    to_user=second_user,
    amount=0.2
)


transfer_from_user = UserTransfer.create(
    from_user=second_user,
    to_user=test_user,
    amount=0.1
)

withdrawal = Withdrawal.create(
    user=test_user,
    amount=uniform(0, 1.0),
    created_at=week_ago,
    approved=False
)


withdrawal = Withdrawal.create(
    user=second_user,
    amount=uniform(0, 1.0),
    approved=False
)
