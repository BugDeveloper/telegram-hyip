_DAILY_INCOME = 0.02
_MINIMAL_ETH_DEPOSIT = 0.0025
_MINIMAL_ETH_WITHDRAW = 0.0125
_ETH_ADDRESS = 'WALLET'
_TOKEN = '599262955:AAH-B7vZ4udSVDJlUVjOCNKyMFy5oKc3xpo'
_BOT_USERNAME = 'the_ascension_bot'
_TEST_USER_ID = 114616282
_REFERRAL_LEVELS_INCOME = [0.1, 0.05, 0.01]
_DEBUG = True


def minimal_eth_withdraw():
    return _MINIMAL_ETH_WITHDRAW


def is_debug_mode():
    return _DEBUG


def get_referral_levels_percentage():
    return _REFERRAL_LEVELS_INCOME


def test_user_id():
    return _TEST_USER_ID


def eth_minimal_deposit():
    return _MINIMAL_ETH_DEPOSIT


def bot_username():
    return _BOT_USERNAME


def token():
    return _TOKEN


def daily_reward():
    return _DAILY_INCOME


def project_eth_address():
    return _ETH_ADDRESS
