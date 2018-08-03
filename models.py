import datetime
from decimal import Decimal, ROUND_HALF_EVEN

import peewee
import playhouse
from peewee import *
from playhouse.hybrid import hybrid_property
from playhouse.signals import post_save

import tariffs

db = SqliteDatabase('ascension.db')


class AscensionModel(playhouse.signals.Model):
    class Meta:
        database = db


class User(AscensionModel):
    chat_id = peewee.IntegerField(primary_key=True)
    referral = peewee.ForeignKeyField('self', backref='partners', null=True, on_delete='SET NULL')
    deposit = peewee.DecimalField(default=0, decimal_places=7, auto_round=True)
    balance = peewee.DecimalField(default=0, decimal_places=7, auto_round=True)
    sum_deposit_reward = peewee.DecimalField(default=0, decimal_places=7, auto_round=True)
    first_level_partners_deposit = peewee.DecimalField(default=0, decimal_places=7, auto_round=True)
    second_level_partners_deposit = peewee.DecimalField(default=0, decimal_places=7, auto_round=True)
    third_level_partners_deposit = peewee.DecimalField(default=0, decimal_places=7, auto_round=True)
    wallet = peewee.CharField(max_length=40, null=True, unique=True)
    username = peewee.CharField(max_length=40)
    first_name = peewee.CharField(max_length=40)
    last_name = peewee.CharField(max_length=40, null=True)
    created_at = DateTimeField(default=datetime.datetime.now())

    @hybrid_property
    def deposit_reward(self):

        gold_tariff_comp = self.deposit.compare(tariffs.tariff_deposit(tariffs.GOLD_TARIFF_INDEX))
        silver_tariff_comp = self.deposit.compare(tariffs.tariff_deposit(tariffs.SILVER_TARIFF_INDEX))
        bronze_tariff_comp = self.deposit.compare(tariffs.tariff_deposit(tariffs.BRONZE_TARIFF_INDEX))

        if gold_tariff_comp >= 0:
            return tariffs.tariff_reward(tariffs.GOLD_TARIFF_INDEX)
        elif silver_tariff_comp >= 0:
            return tariffs.tariff_reward(tariffs.SILVER_TARIFF_INDEX)
        elif bronze_tariff_comp >= 0:
            return tariffs.tariff_reward(tariffs.BRONZE_TARIFF_INDEX)
        else:
            return tariffs.tariff_reward(tariffs.NO_TARIFF_INDEX)

    @deposit_reward.expression
    def deposit_reward(cls):
        return Case(
            None,
            expression_tuples=[
                (
                    cls.deposit.__ge__(
                        tariffs.tariff_deposit(tariffs.GOLD_TARIFF_INDEX)
                    ),
                    tariffs.tariff_reward(tariffs.GOLD_TARIFF_INDEX)
                ),
                (
                    cls.deposit.between(
                        tariffs.tariff_deposit(tariffs.SILVER_TARIFF_INDEX),
                        tariffs.tariff_deposit(tariffs.GOLD_TARIFF_INDEX)
                    ),
                    tariffs.tariff_reward(tariffs.SILVER_TARIFF_INDEX)
                ),
                (
                    cls.deposit.between(
                        tariffs.tariff_deposit(tariffs.BRONZE_TARIFF_INDEX),
                        tariffs.tariff_deposit(tariffs.SILVER_TARIFF_INDEX)
                    ),
                    tariffs.tariff_reward(tariffs.BRONZE_TARIFF_INDEX)
                ),
            ],
            default=tariffs.tariff_reward(tariffs.NO_TARIFF_INDEX)
        )

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


class DepositTransfer(AscensionModel):
    user = ForeignKeyField(User, on_delete='CASCADE', related_name='top_ups', null=True)
    amount = peewee.DecimalField(decimal_places=7, auto_round=True)
    created_at = DateTimeField(default=datetime.datetime.now())


@post_save(sender=DepositTransfer)
def on_save_handler(model_class, instance, created):
    user = instance.user
    amount = instance.amount
    user.balance -= amount
    user.deposit += amount
    user.save()


class UserTransfer(AscensionModel):
    from_user = ForeignKeyField(User, on_delete='CASCADE', related_name='top_ups', null=True)
    to_user = ForeignKeyField(User, on_delete='CASCADE', related_name='top_ups', null=True)
    amount = peewee.DecimalField(decimal_places=7, auto_round=True)
    created_at = DateTimeField(default=datetime.datetime.now())


@post_save(sender=UserTransfer)
def on_save_handler(model_class, instance, created):
    from_user = instance.from_user
    to_user = instance.to_user
    amount = instance.amount

    if from_user.balance > amount:
        from_user.balance -= amount
        from_user.save()
        to_user.balance += amount
        to_user.save()


class TopUp(AscensionModel):
    user = ForeignKeyField(User, on_delete='CASCADE', related_name='top_ups', null=True)
    amount = peewee.DecimalField(decimal_places=7, auto_round=True)
    from_wallet = peewee.CharField(max_length=40, null=True)
    received = peewee.BooleanField(default=True)
    created_at = DateTimeField(default=datetime.datetime.now())


@post_save(sender=TopUp)
def on_save_handler(model_class, instance, created):
    user = instance.user
    user.balance += instance.amount
    user.save()


class Withdrawal(AscensionModel):
    user = ForeignKeyField(User, on_delete='CASCADE', related_name='withdrawals')
    approved = BooleanField(default=False)
    amount = peewee.DecimalField(decimal_places=7, auto_round=True)
    created_at = DateTimeField(default=datetime.datetime.now())


@post_save(sender=Withdrawal)
def on_save_handler(model_class, instance, created):
    user = instance.user

    if user.balance > instance.amount:
        user = instance.user
        user.balance -= instance.amount
        user.save()
