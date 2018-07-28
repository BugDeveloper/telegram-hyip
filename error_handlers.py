from telegram.error import Unauthorized, BadRequest, TimedOut, NetworkError, ChatMigrated, TelegramError
from models import User


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
