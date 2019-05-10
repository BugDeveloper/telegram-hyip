from peewee import DoesNotExist
import bot_states
import lang
from models import User


def user_auth(func):
    def inner(bot, update, *args, **kwargs):
        chat_id = update.message.chat_id
        bot.chat_id = chat_id
        try:
            bot.user = User.get(chat_id=chat_id)
        except DoesNotExist:
            bot.send_message(chat_id, lang.not_registered())
            return bot_states.MAIN
        return func(bot, update, *args, **kwargs)

    return inner


def back_button(func):
    def inner(bot, update, *args, **kwargs):
        import keyboards
        text = update.message.text
        chat_id = update.message.chat_id

        if text == keyboards.MAIN_BUTTONS['back']:
            bot.send_message(
                chat_id=chat_id,
                text=lang.back_to_main_menu(),
                reply_markup=keyboards.main_keyboard()
            )
            return bot_states.MAIN
        return func(bot, update, *args, **kwargs)
    return inner
