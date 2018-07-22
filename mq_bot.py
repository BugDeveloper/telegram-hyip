import telegram
from telegram import ReplyKeyboardMarkup
from telegram.ext import messagequeue as mq
import config
import handlers


class MQBot(telegram.bot.Bot):

    def __init__(self, *args, is_queued_def=True, mqueue=None, **kwargs):
        super(MQBot, self).__init__(*args, **kwargs)
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = mqueue or mq.MessageQueue()

    def __del__(self):
        try:
            self._msg_queue.stop()
        except:
            pass
        super(MQBot, self).__del__()

    @mq.queuedmessage
    def send_message(self, *args, **kwargs):
        text = kwargs['text']
        # if config.is_debug_mode():
        #         print(len(text.encode('utf-8')))
        return super(MQBot, self).send_message(*args, **kwargs)


if __name__ == '__main__':
    from telegram.ext import MessageHandler, Filters
    from telegram.utils.request import Request

    token = config.get_token()
    q = mq.MessageQueue(all_burst_limit=29, all_time_limit_ms=3000)
    request = Request(con_pool_size=8)
    testbot = MQBot(token, request=request, mqueue=q)
    upd = telegram.ext.updater.Updater(bot=testbot, request_kwargs={'read_timeout': 6, 'connect_timeout': 7})


    def reply(bot, update):
        chatid = update.message.chat_id
        msgt = update.message.text
        bot.send_message(
            chat_id=chatid,
            text=msgt,
            reply_markup=ReplyKeyboardMarkup(handlers._MAIN_KEYBOARD)
        )


    hdl = MessageHandler(Filters.text, reply)
    upd.dispatcher.add_handler(hdl)
    upd.start_polling()
