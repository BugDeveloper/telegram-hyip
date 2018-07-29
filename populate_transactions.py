import datetime
from random import uniform
import config
from models import User, TopUp, Withdrawal

test_user = User.get(chat_id=config.test_user_id())
now = datetime.datetime.now()
two_weeks_ago = now - datetime.timedelta(days=15)
week_ago = now - datetime.timedelta(days=7)

for i in range(5):
    top_up = TopUp.create(
        user=test_user,
        amount=uniform(0, 1.0),
        created_at=two_weeks_ago,
    )

for i in range(5):
    top_up = TopUp.create(
        user=test_user,
        amount=uniform(0, 1.0),
        created_at=week_ago
    )

for i in range(10):
    withdrawal = Withdrawal.create(
        user=test_user,
        amount=uniform(0, 1.0),
        created_at=week_ago,
        approved=False
    )

for i in range(10):
    withdrawal = Withdrawal.create(
        user=test_user,
        amount=uniform(0, 1.0),
        created_at=two_weeks_ago,
        approved=False
    )
