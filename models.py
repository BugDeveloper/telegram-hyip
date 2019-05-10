import datetime
import peewee
import playhouse
from peewee import *
from playhouse.hybrid import hybrid_property
from playhouse.signals import post_save, pre_save
from telegram.ext import Dispatcher
import lang
import tariffs

db = SqliteDatabase('ascension.db')


class Payments:
    @staticmethod
    def update_levels_deposit(user, amount):
        first_level_upper = user.referral
        if not first_level_upper:
            return
        first_level_upper.first_level_partners_deposit += amount
        first_level_upper.save()

        second_level_upper = first_level_upper.referral
        if not second_level_upper:
            return
        second_level_upper.second_level_partners_deposit += amount
        second_level_upper.save()

        third_level_upper = second_level_upper.referral
        if not third_level_upper:
            return
        third_level_upper.third_level_partners_deposit += amount
        third_level_upper.save()


class AscensionModel(playhouse.signals.Model):
    class Meta:
        database = db


class User(AscensionModel):
    chat_id = peewee.IntegerField(primary_key=True)
    referral = peewee.ForeignKeyField('self', backref='partners', null=True, on_delete='SET NULL')
    deposit = peewee.FloatField(default=0)
    balance = peewee.FloatField(default=0)
    sum_deposit_reward = peewee.FloatField(default=0)
    first_level_partners_deposit = peewee.FloatField(default=0)
    second_level_partners_deposit = peewee.FloatField(default=0)
    third_level_partners_deposit = peewee.FloatField(default=0)
    wallet = peewee.CharField(max_length=40, null=True, unique=True)
    username = peewee.CharField(max_length=40, null=True)
    first_name = peewee.CharField(max_length=40)
    last_name = peewee.CharField(max_length=40, null=True)
    created_at = DateTimeField(default=datetime.datetime.now())

    def __str__(self):
        text = f'{self.first_name}'
        if self.last_name:
            text = f'{text} {self.last_name}'
        if self.username:
            text = f'@{self.username}'
        return text

    @hybrid_property
    def deposit_reward(self):
        gold_tariff_comp = self.deposit >= tariffs.tariff_deposit(tariffs.GOLD_TARIFF_INDEX)
        silver_tariff_comp = self.deposit >= tariffs.tariff_deposit(tariffs.SILVER_TARIFF_INDEX)
        bronze_tariff_comp = self.deposit >= tariffs.tariff_deposit(tariffs.BRONZE_TARIFF_INDEX)

        if gold_tariff_comp:
            return tariffs.tariff_reward(tariffs.GOLD_TARIFF_INDEX)
        elif silver_tariff_comp:
            return tariffs.tariff_reward(tariffs.SILVER_TARIFF_INDEX)
        elif bronze_tariff_comp:
            return tariffs.tariff_reward(tariffs.BRONZE_TARIFF_INDEX)
        else:
            return tariffs.tariff_reward(tariffs.NO_TARIFF_INDEX)

    @hybrid_property
    def first_level_deposit(self):
        return 0

    @first_level_deposit.expression
    def first_level_deposit(cls):
        return User.select(fn.SUM(User.deposit)).where(User.referral == cls)

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


@post_save(sender=User)
def on_save_handler(model_class, instance, created):
    if created:
        if instance.referral:
            Dispatcher.get_instance().bot.send_message(
                chat_id=instance.referral.chat_id,
                text=f'По вашей ссылке зарегистрировался новый партнёр: {instance}'
            )


class DepositTransfer(AscensionModel):
    user = ForeignKeyField(User, on_delete='CASCADE', related_name='deposit_transfers', null=True)
    amount = peewee.FloatField()
    created_at = DateTimeField(default=datetime.datetime.now())


@pre_save(sender=DepositTransfer)
def on_save_handler(model_class, instance, created):
    user = instance.user
    amount = instance.amount

    if user.balance < amount:
        raise PermissionError()


@post_save(sender=DepositTransfer)
def on_save_handler(model_class, instance, created):
    user = instance.user
    amount = instance.amount
    user.balance -= amount
    user.deposit += amount
    user.save()
    Payments.update_levels_deposit(user, instance.amount)


class UserTransfer(AscensionModel):
    from_user = ForeignKeyField(User, on_delete='CASCADE', related_name='transfers_from', null=True)
    to_user = ForeignKeyField(User, on_delete='CASCADE', related_name='transfers_to', null=True)
    amount = peewee.FloatField()
    created_at = DateTimeField(default=datetime.datetime.now())


@pre_save(sender=UserTransfer)
def on_save_handler(model_class, instance, created):
    amount = instance.amount
    from_user = instance.from_user

    if from_user.balance < amount:
        raise PermissionError()


@post_save(sender=UserTransfer)
def on_save_handler(model_class, instance, created):
    from_user = instance.from_user
    to_user = instance.to_user
    amount = instance.amount

    from_user.balance -= amount
    from_user.save()
    to_user.balance += amount
    to_user.save()

    Dispatcher.get_instance().bot.send_message(
        chat_id=to_user.chat_id,
        text=lang.balance_transferred_from_user(amount, from_user),
    )


class TopUp(AscensionModel):
    user = ForeignKeyField(User, on_delete='CASCADE', related_name='top_ups', null=True)
    amount = peewee.FloatField()
    from_wallet = peewee.CharField(max_length=40, null=True)
    received = peewee.BooleanField(default=True)
    created_at = DateTimeField(default=datetime.datetime.now())


@post_save(sender=TopUp)
def on_save_handler(model_class, instance, created):
    if instance.user:
        user = instance.user
        user.deposit += instance.amount
        user.save()
        Payments.update_levels_deposit(user, instance.amount)

        Dispatcher.get_instance().bot.send_message(
            chat_id=user.chat_id,
            text=f'Ваш депозит был увеличен на {instance.amount} ETH.'
        )


class Withdrawal(AscensionModel):
    user = ForeignKeyField(User, on_delete='CASCADE', related_name='withdrawals')
    approved = BooleanField(default=False)
    amount = peewee.FloatField()
    created_at = DateTimeField(default=datetime.datetime.now())


@pre_save(sender=Withdrawal)
def on_save_handler(model_class, instance, created):
    if created:
        user = instance.user
        if len(user.withdrawals.where(Withdrawal.approved == False)) or user.balance < instance.amount:
            raise PermissionError()


@post_save(sender=Withdrawal)
def on_save_handler(model_class, instance, created):
    user = instance.user

    if created:
        user.balance -= instance.amount
        user.save()
    elif instance.approved:
        Dispatcher.get_instance().bot.send_message(
            chat_id=user.chat_id,
            text=f'Ваш перевод на сумму {instance.amount} ETH был подтвержден. '
                 f'Средства будут переведены в кратчайшие сроки.'
        )
