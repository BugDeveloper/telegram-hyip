_ETH_ADDRESS = '0xbe8C1eA54CFe0b8b0c227396C9e562507c024481'
_TEST_USER_ID = 114616282
_DB_NAME = 'ascension.db'
# _TOKEN = '692532736:AAEf8Deb5jNvozF12sDlL5DOts3T6HrUGF0'
_TEST_TOKEN = '599262955:AAH-B7vZ4udSVDJlUVjOCNKyMFy5oKc3xpo'


def db_name():
    return _DB_NAME


def test_user_id():
    return _TEST_USER_ID


def test_token():
    return _TEST_TOKEN


def project_eth_address():
    return _ETH_ADDRESS.lower()
