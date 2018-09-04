
_MINIMAL_ETH_DEPOSIT = 0.0025
_MINIMAL_ETH_WITHDRAW = 0.0125


_TARIFF_REWARDS = {
    0: 0,
    1: 0.006,
    2: 0.008,
    3: 0.01
}

_PRECISION = '.0001'

_TARIFF_DEPOSIT = {
    0: 0,
    1: 0.0025,
    2: 1,
    3: 3,
}

_REFERRAL_LEVELS_INCOME = [0.1, 0.05, 0.01]

GOLD_TARIFF_INDEX = 3
SILVER_TARIFF_INDEX = 2
BRONZE_TARIFF_INDEX = 1
NO_TARIFF_INDEX = 0


def tariff_reward(tariff_id):
    return _TARIFF_REWARDS[tariff_id]


def tariff_deposit(tariff_id):
    return _TARIFF_DEPOSIT[tariff_id]


def get_referral_levels_percentage():
    return _REFERRAL_LEVELS_INCOME


def eth_minimal_deposit():
    return _MINIMAL_ETH_DEPOSIT


def minimal_eth_withdraw():
    return _MINIMAL_ETH_WITHDRAW
