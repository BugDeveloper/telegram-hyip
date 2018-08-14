from telegram.error import Unauthorized, BadRequest, TimedOut, NetworkError, ChatMigrated, TelegramError
from telegram.ext import run_async
import bot_states


@run_async
def timed_out_handler(bot, update):
    user_id = update.message.chat_id
    bot.send_message(
        chat_id=user_id,
        text='Во время обработки прошлого запроса произошла ошибка.\n'
             'Пожалуйста сообщите в тех поддержку.'
    )
    return bot_states.MAIN


def error_callback(bot, update, error):
    try:
        raise error
    except Unauthorized:
        print('remove update.message.chat_id from conversation list')
    except BadRequest:
        print('handle malformed requests - read more below!')
    except TimedOut:
        print('handle slow connection problems')
    except NetworkError:
        print('handle other connection problems')
    except ChatMigrated as e:
        print('the chat_id of a group has changed, use e.new_chat_id instead')
    except TelegramError:
        print('handle all other telegram related errors')
