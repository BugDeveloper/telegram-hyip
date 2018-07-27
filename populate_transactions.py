from random import uniform
import config
from models import User, TopUp, Withdrawal

test_user = User.get(chat_id=config.get_test_user_id())

for i in range(10):
    top_up = TopUp.create(
        user=test_user,
        amount=uniform(0, 1.0)
    )

for i in range(10):
    withdrawal = Withdrawal.create(
        user=test_user,
        amount=uniform(0, 1.0)
    )
