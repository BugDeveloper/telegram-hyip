_ETH_ADDRESS = '(тут адрес эфира)'
_DB_NAME = 'ascension.db'
_SUPPORT_ACCOUNT = '@ico_day_support'
DEBUG = True


def get_support_account():
    return _SUPPORT_ACCOUNT


def db_name():
    return _DB_NAME


def project_eth_address():
    return _ETH_ADDRESS.lower()
