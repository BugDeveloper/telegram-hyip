import sys
import telegram
from telegram.ext import messagequeue as mq


class MQBot(telegram.bot.Bot):

    def __init__(self, *args, is_queued_def=True, mqueue=None, **kwargs):
        super(MQBot, self).__init__(*args, **kwargs)
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = mqueue or mq.MessageQueue(all_burst_limit=25, all_time_limit_ms=1017)

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
            # print('Bytes: ' + str(sys.getsizeof(text)))
        return super(MQBot, self).send_message(*args, **kwargs)
