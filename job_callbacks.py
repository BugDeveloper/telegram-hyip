from decimal import Decimal
import config
from models import User


def reward_users(bot, job):
    levels_percentage = config.get_referral_levels_percentage()
    query = User.update(balance=(
            User.balance + User.deposit * config.get_daily_reward()
            + User.first_level_partners_deposit * levels_percentage[0]
            + User.second_level_partners_deposit * levels_percentage[1]
            + User.third_level_partners_deposit * levels_percentage[2]
    )
    ).where(User.deposit >= config.get_eth_minimal_deposit())
    query.execute()

    users = User.select().where(User.deposit >= config.get_eth_minimal_deposit())

    for user in users:
        reward = user.deposit * Decimal(config.get_daily_reward())\
                 + user.first_level_partners_deposit * Decimal(levels_percentage[0])\
                 + user.second_level_partners_deposit * Decimal(levels_percentage[1])\
                 + user.third_level_partners_deposit * Decimal(levels_percentage[2])
        bot.send_message(
            chat_id=user.chat_id,
            text='Вы получили начислений на сумму ' + str(reward) + ' ETH'
        )
