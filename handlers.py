from time import sleep

from peewee import DoesNotExist
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import Unauthorized, BadRequest, TimedOut, NetworkError, ChatMigrated, TelegramError, RetryAfter
from telegram.ext import run_async, RegexHandler, MessageHandler, Filters, CommandHandler, CallbackQueryHandler
import config
import lang
from models import User, Partnership
from eth_utils import is_address as is_eth_address
import xlsxwriter

MAIN, WALLET_CHANGE = range(2)

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
    message = update.message
    chat_id = message.chat_id

    try:
        raise error
    except BadRequest as e:
        bot.sendMessage(chat_id=chat_id, text='Кажется, вы что-то делаете неправильно.')
    except RetryAfter as e:
        pass
        # TODO
    except TimedOut as e:
        # TODO
        bot.sendMessage(chat_id=chat_id, text=message)
    except Unauthorized as e:
        pass
        # TODO
    except NetworkError as e:
        # TODO
        bot.sendMessage(chat_id=chat_id, text=message)
    except Exception as e:
        # TODO
        bot.sendMessage(chat_id=chat_id, text=message)


def _reply(update, text, keyboard=None):
    update.message.reply_text(text, reply_markup=keyboard)


def _menu(bot, update, user_data):
    text = update.message.text
    user_id = update.message.chat_id
    try:
        user = User.get(chat_id=user_id)
    except DoesNotExist as e:
        _reply(update, lang.not_registered())
        return MAIN

    if text == _MAIN_BUTTONS['bank']:
        return MainMenu.deposit(update, user)
    elif text == _MAIN_BUTTONS['top_up']:
        return MainMenu.top_up(update, user)
    elif text == _MAIN_BUTTONS['withdraw']:
        return MainMenu.withdraw(update, user)
    elif text == _MAIN_BUTTONS['partners']:
        return MainMenu.partners(bot, update, user)
    elif text == _MAIN_BUTTONS['transactions']:
        return MainMenu.transactions(update, user)


def _callback(bot, update):
    query = update.callback_query
    user_id = query.message.chat_id
    user = User.get(chat_id=user_id)

    if query.data == 'excel':
        PartnersMenu.partners_excel(bot, user)


class PartnersMenu:
    @staticmethod
    @run_async
    def partners_excel(bot, user):
        cols = {
            'Телеграм username': 'username',
            'Имя': 'first_name',
            'Фамилия': 'last_name',
            'Прибыль': 'investments_income',
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
    @run_async
    def transactions(update, user):
        top_ups = user.top_ups
        withdrawals = user.withdrawals
        _reply(update, lang.withdrawals(withdrawals))
        _reply(update, lang.top_ups(top_ups))
        return MAIN

    @staticmethod
    @run_async
    def partners(bot, update, user):

        keyboard = [
            [
                InlineKeyboardButton("Скачать excel таблицу партнёров", callback_data='excel'),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        _reply(update, lang.partners(user.chat_id, user.referral), keyboard=reply_markup)
        return MAIN

    @staticmethod
    @run_async
    def withdraw(update, user):
        if user.wallet:
            _reply(update, lang.withdraw(user.wallet))
            return MAIN
        else:
            _reply(update, lang.wallet_not_set())
            _reply(update, lang.enter_new_wallet(), ReplyKeyboardMarkup(_BACK_KEYBOARD))
            return WALLET_CHANGE

    @staticmethod
    @run_async
    def top_up(update, user):
        if user.wallet:
            _reply(update, lang.top_up())
            return MAIN
        else:
            _reply(update, lang.wallet_not_set())
            _reply(update, lang.enter_new_wallet(), ReplyKeyboardMarkup(_BACK_KEYBOARD))
            return WALLET_CHANGE

    @staticmethod
    @run_async
    def deposit(update, user):
        _reply(update, lang.deposit(user.deposit, user.balance, config.get_daily_percentage(), config.get_minimal_deposit()))
        return MAIN


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

    _reply(update, text, ReplyKeyboardMarkup(_MAIN_KEYBOARD))
    return MAIN


def _wallet_change(bot, update):
    wallet = update.message.text
    if wallet == _MAIN_BUTTONS['back']:
        _reply(update, lang.back_to_main_menu(), ReplyKeyboardMarkup(_MAIN_KEYBOARD))
        return MAIN

    if not is_eth_address(wallet):
        _reply(update, lang.invalid_input())
        return WALLET_CHANGE

    try:
        user = User.get(wallet=wallet)
        _reply(update, lang.eth_address_taken())
        return WALLET_CHANGE
    except DoesNotExist:
        pass

    user_id = update.message.chat_id
    user = User.get(chat_id=user_id)
    user.wallet = wallet.lower()
    user.save()
    _reply(update, lang.wallet_successfully_set(wallet), ReplyKeyboardMarkup(_MAIN_KEYBOARD))
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


def get_start_handler():
    start_handler = CommandHandler('start', _start, pass_args=True)
    return start_handler
