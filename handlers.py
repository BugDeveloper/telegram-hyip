import datetime

from peewee import DoesNotExist
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import Unauthorized, BadRequest, TimedOut, NetworkError, ChatMigrated, TelegramError
from telegram.ext import run_async, RegexHandler, MessageHandler, Filters, CommandHandler, CallbackQueryHandler
import lang
from models import User, Partnership
from eth_utils import is_address as is_eth_address
import xlsxwriter
from ban import Ban

MAIN, WALLET_CHANGE = range(2)

_partners_excel_query_spam_filter = {}
_commands_spam_filter = {}
_bans = {}


class UserFloodRestrictions:
    ALLOWED_COMMAND = 30
    ALLOWED_TIME = 20


_MAIN_BUTTONS = {
    'bank': '💰 Мой счет',
    'top_up': '💼 Вложить',
    'withdraw': '🤑 Вывести',
    'transactions': '⏳ История',
    'partners': '👥 Партнеры',
    'help': '❓ Помощь',
    'back': '⬅️ Назад'
}

_MAIN_KEYBOARD = [
    [
        _MAIN_BUTTONS['bank'],
        _MAIN_BUTTONS['transactions'],
    ],
    [
        _MAIN_BUTTONS['top_up'],
        _MAIN_BUTTONS['withdraw']
    ],
    [
        _MAIN_BUTTONS['partners'],
        _MAIN_BUTTONS['help'],
    ]
]

_BACK_KEYBOARD = [
    [
        _MAIN_BUTTONS['back']
    ]
]


def error_callback(bot, update, error):
    try:
        raise error
    except Unauthorized:
        user = User.get(chat_id=update.message.chat_id)
        user.delete()
    except BadRequest:
        # handle malformed requests - read more below!
        pass
    except TimedOut:
        bot.send_message()
        pass
    except NetworkError:
        # handle other connection problems
        pass
    except ChatMigrated as e:
        # the chat_id of a group has changed, use e.new_chat_id instead
        pass
    except TelegramError:
        # handle all other telegram related error
        pass


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
    text = 'Поздравляем! Вы были забанены за флуд на кол-во часов: ' + str(ban_hours) + '.'
    bot.send_message(chat_id=user_id, text=text)


def _menu(bot, update, user_data):
    user_id = update.message.chat_id

    if not _bans.get('user_id', None):
        _bans['user_id'] = Ban()

    ban = _bans.get('user_id')

    if ban.banned():
        return MAIN

    if user_is_spamming(user_id):
        ban_hours = ban.set_banned()
        notify_ban(bot, user_id, ban_hours)
        return MAIN

    try:
        user = User.get(chat_id=user_id)
    except DoesNotExist as e:
        bot.send_message(user_id, lang.not_registered())
        return MAIN

    text = update.message.text

    if text == _MAIN_BUTTONS['bank']:
        return MainMenu.deposit(bot, user)
    elif text == _MAIN_BUTTONS['top_up']:
        return MainMenu.top_up(bot, user)
    elif text == _MAIN_BUTTONS['withdraw']:
        return MainMenu.withdraw(bot, user)
    elif text == _MAIN_BUTTONS['partners']:
        return MainMenu.partners(bot, user)
    elif text == _MAIN_BUTTONS['transactions']:
        return MainMenu.transactions(bot, user)
    elif text == _MAIN_BUTTONS['help']:
        return MainMenu.help(bot, user)
    else:
        return MAIN


def _callback(bot, update):
    query = update.callback_query
    user_id = query.message.chat_id
    user = User.get(chat_id=user_id)

    if query.data == 'partners_excel':
        if user_id in _partners_excel_query_spam_filter:
            last_query = _partners_excel_query_spam_filter[user_id]
            now = datetime.datetime.now()
            seconds_passed = (now - last_query).seconds
            if seconds_passed < 60:
                text = 'Нельзя запрашивать excel чаще, чем раз в минуту. Осталось секунд: ' + str(
                    60 - seconds_passed) + '.'
                bot.send_message(chat_id=user_id, text=text)
                return
        PartnersMenu.partners_excel(bot, user)


class PartnersMenu:
    @staticmethod
    @run_async
    def partners_excel(bot, user):
        _partners_excel_query_spam_filter[user.chat_id] = datetime.datetime.now()
        cols = {
            'Телеграм username': 'username',
            'Имя': 'first_name',
            'Фамилия': 'last_name',
            'Прибыль': 'balance',
            'Дата регистрации': 'created_date'
        }

        partners_list = user.partners
        filename = 'partners/' + user.username + '.xlsx'

        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': True})
        row = 0
        level_number = 0

        for level in partners_list:
            level_number += 1
            if not row == 0:
                row += 2
            worksheet.write(row, 0, str(level_number) + ' реферальный уровень', bold)
            row += 1
            col = 0
            for field in cols.keys():
                worksheet.write(row, col, field, bold)
                col += 1
            row += 1
            col = 0
            for partner in level:
                for prop_name in cols.values():
                    if prop_name == 'created_date':
                        created_date = getattr(partner, prop_name)
                        worksheet.write(row, col, created_date.strftime("%Y-%m-%d"))
                    else:
                        worksheet.write(row, col, getattr(partner, prop_name))
                    col += 1
                col = 0
                row += 1

        workbook.close()
        bot.send_document(chat_id=user.chat_id, document=open(filename, 'rb'))


class MainMenu:

    @staticmethod
    def transactions(bot, user):
        top_ups = user.top_ups
        withdrawals = user.withdrawals
        text = lang.withdrawals(withdrawals) + '\n' + lang.top_ups(top_ups)
        bot.send_message(chat_id=user.chat_id, text=text)
        return MAIN

    @staticmethod
    @run_async
    def partners(bot, user):

        keyboard = [
            [
                InlineKeyboardButton("Скачать excel таблицу партнёров", callback_data='partners_excel'),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = lang.partners(user.chat_id, user.referral)
        bot.send_message(
            chat_id=user.chat_id,
            text=text,
            reply_markup=reply_markup
        )
        return MAIN

    @staticmethod
    @run_async
    def withdraw(bot, user):
        if user.wallet:
            text = lang.withdraw(user.wallet)
            bot.send_message(chat_id=user.chat_id, text=text)
            return MAIN
        else:
            text = lang.wallet_not_set() + '\n' + lang.enter_new_wallet()

            bot.send_message(
                chat_id=user.chat_id,
                text=text,
                reply_markup=ReplyKeyboardMarkup(_BACK_KEYBOARD)
            )
            return WALLET_CHANGE

    @staticmethod
    @run_async
    def top_up(bot, user):
        if user.wallet:
            text = lang.top_up()
            bot.send_message(chat_id=user.chat_id, text=text)
            return MAIN
        else:
            text = lang.wallet_not_set() + '\n' + lang.enter_new_wallet()
            bot.send_message(
                chat_id=user.chat_id,
                text=text,
                reply_markup=ReplyKeyboardMarkup(_BACK_KEYBOARD)
            )
            return WALLET_CHANGE

    @staticmethod
    @run_async
    def deposit(bot, user):
        text = lang.deposit(user.deposit, user.balance)
        bot.send_message(
            chat_id=user.chat_id,
            text=text
        )
        return MAIN

    @staticmethod
    @run_async
    def help(bot, user):
        text = 'Раздел помощи'
        bot.send_message(
            chat_id=user.chat_id,
            text=text
        )
        return MAIN


@run_async
def _start(bot, update, args):
    chat_id = update.message.chat_id
    try:
        user = User.get(chat_id=chat_id)
        text = update.message.chat.first_name + ', вы уже зарегистрированны в системе. Добро пожаловать домой!'
    except DoesNotExist:
        user = User.create(
            chat_id=chat_id,
            username=update.message.from_user.username,
            first_name=update.message.from_user.first_name,
            last_name=update.message.from_user.last_name
        )

        if len(args) > 0:
            referred_by = args[0]
            try:
                referral = User.get(chat_id=referred_by)
                partnership = Partnership.create(referral=referral, invited=user)
            except DoesNotExist:
                pass

        text = update.message.chat.first_name + ', вы были успешно зарегистрированны в системе!'

    bot.send_message(chat_id=user.chat_id, text=text, reply_markup=ReplyKeyboardMarkup(_MAIN_KEYBOARD))
    return MAIN


def _wallet_change_command(bot, update):
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text=lang.enter_new_wallet(), reply_markup=ReplyKeyboardMarkup(_BACK_KEYBOARD))
    return WALLET_CHANGE


def _wallet_change(bot, update):
    wallet = update.message.text
    chat_id = update.message.chat_id
    if wallet == _MAIN_BUTTONS['back']:
        bot.send_message(chat_id=chat_id, text=lang.back_to_main_menu(),
                         reply_markup=ReplyKeyboardMarkup(_MAIN_KEYBOARD))
        return MAIN

    if not is_eth_address(wallet):
        bot.send_message(chat_id=chat_id, text=lang.invalid_input())
        return WALLET_CHANGE

    try:
        user = User.get(wallet=wallet)
        bot.send_message(chat_id=chat_id, text=lang.eth_address_taken())
        return WALLET_CHANGE
    except DoesNotExist:
        pass

    user_id = update.message.chat_id
    user = User.get(chat_id=user_id)
    user.wallet = wallet.lower()
    user.save()
    bot.send_message(
        chat_id=chat_id,
        text=lang.wallet_successfully_set(wallet),
        reply_markup=ReplyKeyboardMarkup(_MAIN_KEYBOARD))
    return MAIN


def get_callback_query_handler():
    callback_handler = CallbackQueryHandler(_callback)
    return callback_handler


def get_change_wallet_handler():
    wallet_handler = MessageHandler(
        Filters.text,
        _wallet_change
    )
    return wallet_handler


def get_main_menu_handler():
    main_handler = RegexHandler('^('
                                + _MAIN_BUTTONS['bank'] + '|'
                                + _MAIN_BUTTONS['transactions'] + '|'
                                + _MAIN_BUTTONS['top_up'] + '|'
                                + _MAIN_BUTTONS['withdraw'] + '|'
                                + _MAIN_BUTTONS['partners'] + '|'
                                + _MAIN_BUTTONS['help']
                                + ')$',
                                _menu,
                                pass_user_data=True
                                )
    return main_handler


def get_change_wallet_command_handler():
    change_wallet_handler = CommandHandler('wallet', _wallet_change_command)
    return change_wallet_handler


def get_start_command_handler():
    start_handler = CommandHandler('start', _start, pass_args=True)
    return start_handler
