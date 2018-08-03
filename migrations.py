import os
import sqlite3
from peewee import SqliteDatabase
from models import User, TopUp, Withdrawal, DepositTransfer, UserTransfer

_DB_NAME = 'ascension.db'

print('Delete current database? (Y/n)')
delete_db = input().lower()

if delete_db == 'y' or delete_db == '':
    if os.path.isfile(_DB_NAME):
        os.remove(_DB_NAME)
elif delete_db == 'n':
    pass
else:
    print('Incorrect input, script stopped')
    exit(1)

db = SqliteDatabase(_DB_NAME)
db.create_tables([User, TopUp, Withdrawal, DepositTransfer, UserTransfer])
sqlite = sqlite3.connect(_DB_NAME)
sqlite.close()
