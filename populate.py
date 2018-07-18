import config
from models import User, Partnership

test_user = User.get(chat_id=config.get_test_user_id())

user1 = User.create(chat_id=1, username='some_dude1', first_name='Педик')
user2 = User.create(chat_id=2, username='some_dude2', first_name='Педик')
user3 = User.create(chat_id=3, username='some_dude3', first_name='Педик')

partnership1 = Partnership.create(referral=test_user, invited=user1)
partnership2 = Partnership.create(referral=test_user, invited=user2)
partnership3 = Partnership.create(referral=test_user, invited=user3)

user11 = User.create(chat_id=11, username='some_dude11', first_name='Педик')
user12 = User.create(chat_id=12, username='some_dude12', first_name='Педик')
user13 = User.create(chat_id=13, username='some_dude13', first_name='Педик')

partnership11 = Partnership.create(referral=user1, invited=user11)
partnership12 = Partnership.create(referral=user1, invited=user12)
partnership13 = Partnership.create(referral=user1, invited=user13)


user121 = User.create(chat_id=121, username='some_dude121', first_name='Педик')
user122 = User.create(chat_id=122, username='some_dude122', first_name='Педик')

partnership121 = Partnership.create(referral=user12, invited=user121)
partnership122 = Partnership.create(referral=user12, invited=user122)
