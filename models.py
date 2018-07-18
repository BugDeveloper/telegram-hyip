import datetime
import peewee
from peewee import *

db = SqliteDatabase('ascension.db')


class AscensionModel(peewee.Model):
    class Meta:
        database = db


class User(AscensionModel):
    chat_id = peewee.IntegerField(primary_key=True)
    deposit = peewee.DecimalField(default=0, decimal_places=6)
    balance = peewee.DecimalField(default=0, decimal_places=6)
    wallet = peewee.CharField(max_length=40, null=True, unique=True)
    username = peewee.CharField(max_length=40)
    first_name = peewee.CharField(max_length=40)
    last_name = peewee.CharField(max_length=40, null=True)
    created_date = DateTimeField(default=datetime.datetime.now)

    @property
    def referral(self):
        query = (
            User.select()
                .join(Partnership, JOIN.INNER, on=Partnership.referral)
                .where(Partnership.invited == self.chat_id)
                .first()
        )
        return query

    @property
    def partners(self):
        partners_list = []
        first_level_query = (
            User.select(User, Partnership)
                .join(Partnership, JOIN.INNER, on=Partnership.invited)
                .where(Partnership.referral == self.chat_id)
        )
        first_level_partners = first_level_query.execute()
        partners_list.append(first_level_partners)

        first_level_ids = []
        for partner in first_level_partners:
            first_level_ids.append(partner.chat_id)

        second_level_query = (
            User.select(User, Partnership)
                .join(Partnership, JOIN.INNER, on=Partnership.invited)
                .where(Partnership.referral << first_level_ids)
        )
        second_level_partners = second_level_query.execute()
        partners_list.append(second_level_partners)

        second_level_ids = []
        for partner in second_level_partners:
            second_level_ids.append(partner.chat_id)

        third_level_query = (
            User.select(User, Partnership)
                .join(Partnership, JOIN.INNER, on=Partnership.invited)
                .where(Partnership.referral << second_level_ids)
        )
        third_level_partners = third_level_query.execute()
        partners_list.append(third_level_partners)

        return partners_list


class Partnership(AscensionModel):
    referral = peewee.ForeignKeyField(User, index=True, on_delete='CASCADE')
    invited = peewee.ForeignKeyField(User, index=True)


class TopUp(AscensionModel):
    user = ForeignKeyField(User, on_delete='CASCADE', related_name='top_ups')
    amount = peewee.DecimalField(decimal_places=5)


class Withdrawal(AscensionModel):
    user = ForeignKeyField(User, on_delete='CASCADE', related_name='withdrawals')
    amount = peewee.DecimalField(decimal_places=5)
