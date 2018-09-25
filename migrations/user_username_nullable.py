from playhouse.migrate import *

DB_NAME = 'ascension.db'
db = SqliteDatabase(DB_NAME)
migrator = SqliteMigrator(db)

migrate(
    migrator.drop_not_null('user', 'username')
)
