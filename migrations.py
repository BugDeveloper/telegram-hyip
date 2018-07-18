import os

from peewee import SqliteDatabase
from models import User, Partnership, TopUp, Withdrawal

_DB_NAME = 'ascension.db'

print('Delete current database? (Y/n)')
delete_db = input()

if delete_db == 'y' or delete_db == 'Y' or delete_db == '':
    os.remove(_DB_NAME)
elif delete_db == 'n' or delete_db == 'N':
    pass
else:
    print('Incorrect input, script stopped')
    exit(1)

db = SqliteDatabase(_DB_NAME)
db.create_tables([User, Partnership, TopUp, Withdrawal])
