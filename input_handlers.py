import datetime
import telegram
from peewee import DoesNotExist, fn
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import run_async, RegexHandler, MessageHandler, Filters, CallbackQueryHandler
import bot_states
import keyboards
import lang
import excel_generator
from models import User, TopUp, Withdrawal, UserTransfer, DepositTransfer
from eth_utils import is_address as is_eth_address
from ban import Ban
import tariffs

_partners_excel_query_time = {}
_transactions_excel_query_time = {}
_commands_spam_filter = {}
_bans = {}

_POSITIVE_FLOAT_REGEX = f'^(?![0.]+$)\d+(\.\d{1,2})|{keyboards.MAIN_BUTTONS["back"]}?$'


class UserFloodRestrictions:
    ALLOWED_COMMAND = 30
    ALLOWED_TIME = 20


def user_is_spamming(chat_id):
    now = datetime.datetime.now()
    if chat_id not in _commands_spam_filter:
        _commands_spam_filter[chat_id] = []
    _commands_spam_filter[chat_id].append(now)

    updated_filter = [
        query_time for query_time in _commands_spam_filter[chat_id]
        if (now - query_time).seconds < UserFloodRestrictions.ALLOWED_TIME
    ]

    _commands_spam_filter[chat_id] = updated_filter

    if len(updated_filter) > UserFloodRestrictions.ALLOWED_COMMAND:
        return True
    return False


@run_async
def notify_ban(bot, user_id, ban_hours):
    text = f'Поздравляем! Вы были забанены за флуд на кол-во часов: {ban_hours}.'
    bot.send_message(chat_id=user_id, text=text)


def _main_menu(bot, update, user_data):
    user_id = update.message.chat_id

    if not _bans.get(user_id, None):
        _bans[user_id] = Ban()

    ban = _bans.get(user_id)
    if ban.banned():
        return bot_states.MAIN

    if user_is_spamming(user_id):
        ban_hours = ban.set_banned()
        notify_ban(bot, user_id, ban_hours)
        return bot_states.MAIN

    try:
        user = User.get(chat_id=user_id)
        username = update.message.from_user.username
        if user.username != username:
            user.username = username
            user.save()
    except DoesNotExist as e:
        bot.send_message(user_id, lang.not_registered())
        return bot_states.MAIN

    text = update.message.text

    if text == keyboards.MAIN_BUTTONS['bank']:
        return MainMenu.bank(bot, user)
    elif text == keyboards.MAIN_BUTTONS['top_up']:
        return MainMenu.top_up(bot, user)
    elif text == keyboards.MAIN_BUTTONS['withdraw']:
        return MainMenu.withdraw(bot, user)
    elif text == keyboards.MAIN_BUTTONS['partners']:
        return MainMenu.partners(bot, user)
    elif text == keyboards.MAIN_BUTTONS['transactions']:
        return MainMenu.transactions(bot, user)
    elif text == keyboards.MAIN_BUTTONS['help']:
        return MainMenu.help(bot, user)


def user_request_excel_too_often(user_id, query_time):
    if user_id in query_time:
        last_query = query_time[user_id]
        now = datetime.datetime.now()
        seconds_passed = (now - last_query).seconds
        if seconds_passed < 60:
            return True
    query_time[user_id] = datetime.datetime.now()
    return False


def _callback(bot, update):
    query = update.callback_query
    user_id = query.message.chat_id
    user = User.get(chat_id=user_id)

    if query.data == 'partners_excel':
        if user_request_excel_too_often(user_id, _partners_excel_query_time):
            text = 'Нельзя запрашивать excel партнёров чаще, чем раз в минуту.'
            bot.send_message(chat_id=user_id, text=text)
            return
        excel_generator.partners_excel(bot, user)
    elif query.data == 'transactions_excel':
        if user_request_excel_too_often(user_id, _transactions_excel_query_time):
            text = 'Нельзя запрашивать excel транзакций чаще, чем раз в минуту.'
            bot.send_message(chat_id=user_id, text=text)
            return
        excel_generator.transactions_excel(bot, user)


class MainMenu:

    @staticmethod
    @run_async
    def transactions(bot, user):
        count_of_last_trx = 3
        top_ups = user.top_ups.order_by(TopUp.id.desc()).limit(count_of_last_trx)
        withdrawals = user.withdrawals.order_by(Withdrawal.id.desc()).limit(count_of_last_trx)
        keyboard = [
            [
                InlineKeyboardButton("Скачать excel таблицу транзакций", callback_data='transactions_excel'),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=user.chat_id, text=lang.top_ups(top_ups))
        bot.send_message(
            chat_id=user.chat_id,
            text=lang.withdrawals(withdrawals),
            reply_markup=reply_markup
        )
        return bot_states.MAIN

    @staticmethod
    @run_async
    def partners(bot, user):
        keyboard = [
            [
                InlineKeyboardButton("Скачать excel таблицу партнёров", callback_data='partners_excel'),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = lang.partners(user, bot.username, user.referral)
        bot.send_message(
            chat_id=user.chat_id,
            text=text,
            reply_markup=reply_markup
        )
        return bot_states.MAIN

    @staticmethod
    @run_async
    def withdraw(bot, user):
        if user.wallet:
            text = lang.withdraw(user.wallet)
            bot.send_message(chat_id=user.chat_id, text=text)
            return bot_states.MAIN
        else:
            text = f'{lang.wallet_not_set()}\n{lang.enter_new_wallet()}'

            bot.send_message(
                chat_id=user.chat_id,
                text=text,
                reply_markup=keyboards.back_keyboard()
            )
            return bot_states.WALLET_CHANGE

    @staticmethod
    @run_async
    def top_up(bot, user):
        if user.wallet:
            text = lang.top_up(user.wallet)
            bot.send_message(
                chat_id=user.chat_id,
                text=text,
            )
            bot.send_message(
                chat_id=user.chat_id,
                text=lang.top_up_invest_wallet(),
                parse_mode=telegram.ParseMode.MARKDOWN
            )
            return bot_states.MAIN
        else:
            text = lang.wallet_not_set() + '\n' + lang.enter_new_wallet()
            bot.send_message(
                chat_id=user.chat_id,
                text=text,
                reply_markup=keyboards.back_keyboard(),
            )
            return bot_states.WALLET_CHANGE

    @staticmethod
    @run_async
    def bank(bot, user):
        text = lang.deposit(user.deposit, user.balance, user.deposit_reward, user.sum_deposit_reward)
        bot.send_message(
            chat_id=user.chat_id,
            text=text
        )
        return bot_states.MAIN

    @staticmethod
    @run_async
    def help(bot, user):
        bot.send_message(
            chat_id=user.chat_id,
            text=lang.help()
        )
        # TODO Erase
        return bot_states.MAIN


class LessThanMinimalWithdraw(Exception):
    pass


class NotEnoughBalance(Exception):
    pass


def _validate_transaction(user, text):
    amount = float(text)
    if amount < tariffs.minimal_eth_withdraw():
        raise LessThanMinimalWithdraw()
    if amount > user.balance:
        raise NotEnoughBalance

    return amount


def _transfer_balance_to_user(bot, update):
    text = update.message.text
    chat_id = update.message.chat_id

    if text == keyboards.MAIN_BUTTONS['back']:
        bot.send_message(
            chat_id=chat_id,
            text=lang.back_to_main_menu(),
            reply_markup=keyboards.main_keyboard()
        )
        return bot_states.MAIN

    transfer_data = text.split(' ')

    if len(transfer_data) != 2:
        bot.send_message(chat_id=chat_id, text=lang.invalid_input())
        return bot_states.TRANSFER_BALANCE_TO_USER

    username = transfer_data[0].lower()

    user = User.get(chat_id=chat_id)

    try:
        user_to_transfer = User.get(fn.Lower(User.username) == username)
        amount = _validate_transaction(user, transfer_data[1])
    except ValueError:
        bot.send_message(chat_id=chat_id, text=lang.invalid_input())
        return bot_states.TRANSFER_BALANCE_TO_USER
    except LessThanMinimalWithdraw:
        bot.send_message(chat_id=chat_id, text=lang.minimal_withdraw_amount())
        return bot_states.TRANSFER_BALANCE_TO_USER
    except NotEnoughBalance:
        bot.send_message(chat_id=chat_id, text=lang.not_enough_eth())
        return bot_states.TRANSFER_BALANCE_TO_USER
    except DoesNotExist:
        bot.send_message(chat_id=chat_id, text=lang.user_not_registered())
        return bot_states.TRANSFER_BALANCE_TO_USER

    UserTransfer.create(
        from_user=user,
        to_user=user_to_transfer,
        amount=amount,
    )

    bot.send_message(
        chat_id=user.chat_id,
        text=lang.balance_transferred_to_user(amount, user_to_transfer.username),
        reply_markup=keyboards.main_keyboard()
    )

    return bot_states.MAIN


def _transfer_balance_to_deposit(bot, update):
    text = update.message.text
    chat_id = update.message.chat_id

    if text == keyboards.MAIN_BUTTONS['back']:
        bot.send_message(
            chat_id=chat_id,
            text=lang.back_to_main_menu(),
            reply_markup=keyboards.main_keyboard()
        )
        return bot_states.MAIN

    user = User.get(chat_id=chat_id)

    try:
        amount = _validate_transaction(user, text)
    except ValueError:
        bot.send_message(chat_id=chat_id, text=lang.invalid_input())
        return bot_states.TRANSFER_BALANCE_TO_DEPOSIT
    except LessThanMinimalWithdraw:
        bot.send_message(chat_id=chat_id, text=lang.minimal_withdraw_amount())
        return bot_states.TRANSFER_BALANCE_TO_DEPOSIT
    except NotEnoughBalance:
        bot.send_message(chat_id=chat_id, text=lang.not_enough_eth())
        return bot_states.TRANSFER_BALANCE_TO_DEPOSIT

    DepositTransfer.create(
        user=user,
        amount=amount
    )

    bot.send_message(
        chat_id=chat_id,
        text=lang.balance_transferred_to_deposit(amount),
        reply_markup=keyboards.main_keyboard()
    )
    return bot_states.MAIN


def _create_withdrawal(bot, update):
    text = update.message.text
    chat_id = update.message.chat_id

    if text == keyboards.MAIN_BUTTONS['back']:
        bot.send_message(
            chat_id=chat_id,
            text=lang.back_to_main_menu(),
            reply_markup=keyboards.main_keyboard()
        )
        return bot_states.MAIN

    user = User.get(chat_id=chat_id)

    try:
        amount = _validate_transaction(user, text)
    except ValueError:
        bot.send_message(chat_id=chat_id, text=lang.invalid_input())
        return bot_states.CREATE_WITHDRAWAL
    except LessThanMinimalWithdraw:
        bot.send_message(chat_id=chat_id, text=lang.minimal_withdraw_amount())
        return bot_states.CREATE_WITHDRAWAL
    except NotEnoughBalance:
        bot.send_message(chat_id=chat_id, text=lang.not_enough_eth())
        return bot_states.CREATE_WITHDRAWAL

    try:
        not_approved_withdrawal = Withdrawal.get(approved=False)
        bot.send_message(
            chat_id=chat_id,
            text=lang.not_approved_previous(not_approved_withdrawal.amount),
            reply_markup=keyboards.main_keyboard()
        )
        return bot_states.MAIN
    except DoesNotExist:
        pass

    Withdrawal.create(
        user=user,
        amount=amount
    )

    bot.send_message(
        chat_id=user.chat_id,
        text=lang.withdrawal_created(user.wallet),
        reply_markup=keyboards.main_keyboard()
    )

    return bot_states.MAIN


@run_async
def _change_wallet(bot, update):
    chat_id = update.message.chat_id
    if update.message.text == keyboards.MAIN_BUTTONS['back']:
        bot.send_message(
            chat_id=chat_id,
            text=lang.back_to_main_menu(),
            reply_markup=keyboards.main_keyboard()
        )
        return bot_states.MAIN

    wallet = update.message.text.lower()

    if not is_eth_address(wallet):
        bot.send_message(chat_id=chat_id, text=lang.invalid_input())
        return bot_states.WALLET_CHANGE
    try:
        User.get(wallet=wallet)
        bot.send_message(chat_id=chat_id, text=lang.eth_address_taken())
        return bot_states.WALLET_CHANGE
    except DoesNotExist:
        pass

    user_id = update.message.chat_id
    user = User.get(chat_id=user_id)
    user.wallet = wallet.lower()
    user.save()
    bot.send_message(
        chat_id=chat_id,
        text=lang.wallet_successfully_set(wallet),
        reply_markup=keyboards.main_keyboard())
    return bot_states.MAIN


def callback_query_handler():
    callback_handler = CallbackQueryHandler(_callback)
    return callback_handler


def main_menu_input_handler():
    regex = f'^({keyboards.MAIN_BUTTONS["bank"]}|' \
            f'{keyboards.MAIN_BUTTONS["transactions"]}|' \
            f'{keyboards.MAIN_BUTTONS["top_up"]}|' \
            f'{keyboards.MAIN_BUTTONS["withdraw"]}|' \
            f'{keyboards.MAIN_BUTTONS["partners"]}|' \
            f'{keyboards.MAIN_BUTTONS["help"]}' \
            f')$'
    main_handler = RegexHandler(
        regex,
        _main_menu,
        pass_user_data=True
    )
    return main_handler


def withdrawal_input_handler():
    handler = MessageHandler(
        Filters.text,
        _create_withdrawal
    )
    return handler


def transfer_balance_to_deposit_input_handler():
    handler = MessageHandler(
        Filters.text,
        _transfer_balance_to_deposit
    )
    return handler


def transfer_balance_to_user_input_handler():
    handler = MessageHandler(
        Filters.text,
        _transfer_balance_to_user
    )
    return handler


def change_wallet_input_handler():
    wallet_handler = MessageHandler(
        Filters.text,
        _change_wallet
    )

    return wallet_handler
