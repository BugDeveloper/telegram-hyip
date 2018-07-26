import datetime
import peewee
from peewee import *


db = SqliteDatabase('ascension.db')


class AscensionModel(peewee.Model):
    class Meta:
        database = db


class User(AscensionModel):
    chat_id = peewee.IntegerField(primary_key=True)
    referral = peewee.ForeignKeyField('self', backref='partners', null=True, on_delete='SET NULL')
    deposit = peewee.DecimalField(default=0)
    balance = peewee.DecimalField(default=0)
    first_level_partners_deposit = peewee.DecimalField(default=0)
    second_level_partners_deposit = peewee.DecimalField(default=0)
    third_level_partners_deposit = peewee.DecimalField(default=0)
    wallet = peewee.CharField(max_length=40, null=True, unique=True)
    username = peewee.CharField(max_length=40)
    first_name = peewee.CharField(max_length=40)
    last_name = peewee.CharField(max_length=40, null=True)
    created_at = DateTimeField(default=datetime.datetime.now)

    @property
    def partners_per_levels(self):

        partners_list = []
        first_level_query = User.select().where(User.referral == self)

        first_level_partners = first_level_query.execute()
        partners_list.append(first_level_partners)

        first_level_ids = []
        for partner in first_level_partners:
            first_level_ids.append(partner.chat_id)

        second_level_query = (
            User.select()
                .where(User.referral << first_level_ids)
        )
        second_level_partners = second_level_query.execute()
        partners_list.append(second_level_partners)

        second_level_ids = []
        for partner in second_level_partners:
            second_level_ids.append(partner.chat_id)

        third_level_query = (
            User.select()
                .where(User.referral << second_level_ids)
        )
        third_level_partners = third_level_query.execute()
        partners_list.append(third_level_partners)

        return partners_list


class TopUp(AscensionModel):
    user = ForeignKeyField(User, on_delete='CASCADE', related_name='top_ups')
    amount = peewee.DecimalField(decimal_places=5)
    created_at = DateTimeField(default=datetime.datetime.now)


class Withdrawal(AscensionModel):
    user = ForeignKeyField(User, on_delete='CASCADE', related_name='withdrawals')
    amount = peewee.DecimalField(decimal_places=5)
    created_at = DateTimeField(default=datetime.datetime.now)
