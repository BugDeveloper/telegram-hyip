import datetime

from peewee import DoesNotExist

import config
import mq_bot
from models import User

mq_bot.init()

now = datetime.datetime.now()
two_weeks_ago = now - datetime.timedelta(days=15)
week_ago = now - datetime.timedelta(days=7)

core_referral1 = User.create(
    chat_id=10,
    username='core_referral1',
    first_name='Педик',
    created_at=two_weeks_ago
)

core_referral11 = User.create(
    chat_id=20,
    username='core_referral11',
    first_name='Педик',
    referral=core_referral1,
    created_at=two_weeks_ago
)

core_referral111 = User.create(
    chat_id=30,
    username='core_referral111',
    first_name='Педик',
    referral=core_referral11,
    created_at=two_weeks_ago
)

try:
    test_user = User.get(chat_id=config.test_user_id())
    test_user.referral = core_referral111
    test_user.balance = 1
    test_user.deposit = 1
    test_user.save()
except DoesNotExist:
    test_user = User.create(
        chat_id=config.test_user_id(),
        username='bug_developer',
        first_name='Senya',
        last_name=None,
        referral=core_referral111
    )


user1 = User.create(
    chat_id=1,
    username='some_dude1',
    first_name='Педик',
    referral=test_user,
    created_at=week_ago
)

user2 = User.create(
    chat_id=2,
    username='some_dude2',
    first_name='Педик',
    referral=test_user,
    created_at=week_ago
)

user3 = User.create(
    chat_id=3,
    username='some_dude3',
    first_name='Педик',
    referral=test_user,
    created_at=week_ago
)

user11 = User.create(
    chat_id=11,
    username='some_dude11',
    first_name='Педик',
    referral=user1,
    created_at=week_ago
)

user12 = User.create(
    chat_id=12,
    username='some_dude12',
    first_name='Педик',
    referral=user1,
    created_at=week_ago
)

user13 = User.create(
    chat_id=13,
    username='some_dude13',
    first_name='Педик',
    referral=user1,
    created_at=week_ago
)

user121 = User.create(
    chat_id=121,
    username='some_dude121',
    first_name='Педик',
    referral=user12,
    created_at=week_ago
)

user122 = User.create(
    chat_id=122,
    username='some_dude122',
    first_name='Педик',
    referral=user12,
    created_at=week_ago
)
