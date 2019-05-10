_ETH_ADDRESS = '0xbe8C1eA54CFe0b8b0c227396C9e562507c024481'
_DB_NAME = 'ascension.db'
_SUPPORT_ACCOUNT = '@ico_day_support'
DEBUG = True


def get_support_account():
    return _SUPPORT_ACCOUNT


def db_name():
    return _DB_NAME


def project_eth_address():
    return _ETH_ADDRESS.lower()
