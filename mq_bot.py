import sys

import telegram
from telegram import ReplyKeyboardMarkup
from telegram.ext import messagequeue as mq
import handlers
import config


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
        if 'text' in kwargs:
            text = kwargs['text']
            print(sys.getsizeof(text))
        return super(MQBot, self).send_message(*args, **kwargs)
