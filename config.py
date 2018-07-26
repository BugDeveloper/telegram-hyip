_DAILY_INCOME = 0.02
_MINIMAL_ETH_DEPOSIT = 0.0025
_MINIMAL_ETH_WITHDRAW = 0.0125
_ETH_ADDRESS = 'WALLET'
_TOKEN = '599262955:AAH-B7vZ4udSVDJlUVjOCNKyMFy5oKc3xpo'
_BOT_USERNAME = 'the_ascension_bot'
_TEST_USER_ID = 114616282
_REFERRAL_LEVELS_INCOME = [0.1, 0.05, 0.01]
_DEBUG = True


def is_debug_mode():
    return _DEBUG


def get_referral_levels_percentage():
    return _REFERRAL_LEVELS_INCOME


def get_test_user_id():
    return _TEST_USER_ID


def get_eth_minimal_deposit():
    return _MINIMAL_ETH_DEPOSIT


def get_bot_username():
    return _BOT_USERNAME


def get_token():
    return _TOKEN


def get_daily_reward():
    return _DAILY_INCOME


def get_project_eth_address():
    return _ETH_ADDRESS
