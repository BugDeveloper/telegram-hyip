import telegram
from telegram.ext import Updater, ConversationHandler
import logging
from telegram.utils.request import Request
import config
import handlers
from mq_bot import MQBot
from telegram.ext import messagequeue as mq


def main():
    token = config.get_token()
    q = mq.MessageQueue(all_burst_limit=15, all_time_limit_ms=3000)
    request = Request(con_pool_size=8)
    bot = MQBot(token, request=request, mqueue=q)
    updater = telegram.ext.updater.Updater(bot=bot)
    dispatcher = updater.dispatcher
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    main_handler = handlers.get_main_menu_handler()
    start_handler = handlers.get_start_handler()
    change_wallet_handler = handlers.get_change_wallet_handler()
    callback_query_handler = handlers.get_callback_query_handler()

    conv_handler = ConversationHandler(
        entry_points=[
            start_handler,
            main_handler
        ],
        states={
            handlers.MAIN: [
                main_handler,
            ],
            handlers.WALLET_CHANGE: [change_wallet_handler],
        },
        fallbacks=[]
    )

    dispatcher.add_error_handler(handlers.error_callback)
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(callback_query_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
