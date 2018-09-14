from peewee import DoesNotExist
from telegram.ext import CommandHandler, run_async
import bot_states
import keyboards
import lang
from models import User


@run_async
def _start_command(bot, update, args):
    chat_id = update.message.chat_id
    first_name = update.message.chat.first_name
    username = update.message.from_user.username

    if not username:
        text = f'{first_name}, вы не установили имя пользователя telegram.' \
               f' Пожалуйста установите поле в настройках и введите команду /start ещё раз.'
        bot.send_message(chat_id=chat_id, text=text)
        return bot_states.MAIN

    try:
        user = User.get(chat_id=chat_id)
        text = f'{first_name}, вы уже зарегистрированны в системе. Добро пожаловать домой!'
    except DoesNotExist:
        referral = None
        try:
            if len(args) > 0:
                referred_by = args[0]
                referral = User.get(chat_id=referred_by)
        except DoesNotExist:
            pass

        user = User.create(
            chat_id=chat_id,
            username=username,
            first_name=update.message.from_user.first_name,
            last_name=update.message.from_user.last_name,
            referral=referral
        )

        text = f'{first_name}, вы были успешно зарегистрированны в системе!'

    bot.send_message(chat_id=user.chat_id, text=text, reply_markup=keyboards.main_keyboard())
    return bot_states.MAIN


@run_async
def _transfer_balance_to_deposit_command(bot, update):
    chat_id = update.message.chat_id
    try:
        user = User.get(chat_id=chat_id)
    except DoesNotExist:
        bot.send_message(chat_id, lang.not_registered())
        return bot_states.MAIN
    bot.send_message(
        chat_id=chat_id,
        text=lang.transfer_balance_to_deposit(user.balance),
        reply_markup=keyboards.back_keyboard()
    )
    return bot_states.TRANSFER_BALANCE_TO_DEPOSIT


@run_async
def _wallet_change_command(bot, update):
    chat_id = update.message.chat_id
    try:
        user = User.get(chat_id=chat_id)
    except DoesNotExist:
        bot.send_message(
            chat_id=chat_id,
            text=lang.not_registered()
        )
        return bot_states.MAIN

    bot.send_message(
        chat_id=chat_id,
        text=lang.enter_new_wallet(),
        reply_markup=keyboards.back_keyboard()
    )
    return bot_states.WALLET_CHANGE


@run_async
def _transfer_balance_to_user(bot, update):
    chat_id = update.message.chat_id
    try:
        user = User.get(chat_id=chat_id)
    except DoesNotExist:
        bot.send_message(chat_id, lang.not_registered())
        return bot_states.MAIN

    bot.send_message(
        chat_id=chat_id,
        text=lang.transfer_balance_to_user(user.balance),
        reply_markup=keyboards.back_keyboard()
    )
    return bot_states.TRANSFER_BALANCE_TO_USER


@run_async
def _withdrawal_command(bot, update):
    chat_id = update.message.chat_id
    try:
        user = User.get(chat_id=chat_id)
    except DoesNotExist:
        bot.send_message(chat_id, lang.not_registered())
        return bot_states.MAIN
    bot.send_message(
        chat_id=chat_id,
        text=lang.create_withdrawal(user.balance),
        reply_markup=keyboards.back_keyboard()
    )
    return bot_states.CREATE_WITHDRAWAL


def transfer_balance_to_deposit():
    handler = CommandHandler('transfer_deposit', _transfer_balance_to_deposit_command)
    return handler


def change_wallet_initiation_handler():
    handler = CommandHandler('wallet', _wallet_change_command)
    return handler


def start_command_handler():
    handler = CommandHandler('start', _start_command, pass_args=True)
    return handler


def transfer_balance_to_user():
    handler = CommandHandler('transfer_user', _transfer_balance_to_user)
    return handler


def withdraw_command_handler():
    handler = CommandHandler('withdraw', _withdrawal_command)
    return handler
