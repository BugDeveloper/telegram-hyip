from telegram import ReplyKeyboardMarkup

MAIN_BUTTONS = {
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
        MAIN_BUTTONS['bank'],
        MAIN_BUTTONS['transactions'],
    ],
    [
        MAIN_BUTTONS['top_up'],
        MAIN_BUTTONS['withdraw']
    ],
    [
        MAIN_BUTTONS['partners'],
        MAIN_BUTTONS['help'],
    ]
]

_BACK_KEYBOARD = [
    [
        MAIN_BUTTONS['back']
    ]
]


def main_keyboard():
    return ReplyKeyboardMarkup(_MAIN_KEYBOARD)


def back_keyboard():
    return ReplyKeyboardMarkup(_BACK_KEYBOARD)
