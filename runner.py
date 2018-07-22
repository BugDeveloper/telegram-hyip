import sys

import telegram
from telegram.ext import Updater, ConversationHandler
import logging
from telegram.utils.request import Request
import config
import handlers
from mq_bot import MQBot
from telegram.ext import messagequeue as mq


def main(args):
    token = config.get_token()
    q = mq.MessageQueue(all_burst_limit=28, all_time_limit_ms=1017)
    request = Request(con_pool_size=8)
    bot = MQBot(token=token, request=request, mqueue=q)
    updater = telegram.ext.updater.Updater(bot=bot, request_kwargs={'read_timeout': 6, 'connect_timeout': 7})
    dispatcher = updater.dispatcher
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    main_handler = handlers.get_main_menu_handler()
    start_handler = handlers.get_start_command_handler()
    change_wallet_handler = handlers.get_change_wallet_handler()
    change_wallet_command_handler = handlers.get_change_wallet_command_handler()
    callback_query_handler = handlers.get_callback_query_handler()

    conv_handler = ConversationHandler(
        entry_points=[
            start_handler,
            main_handler
        ],
        states={
            handlers.MAIN: [
                main_handler,
                change_wallet_command_handler
            ],
            handlers.WALLET_CHANGE: [change_wallet_handler],
        },
        fallbacks=[]
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(callback_query_handler)
    dispatcher.add_error_handler(handlers.error_callback)

    if not len(args) or args[0] == 'polling':
        updater.start_polling()
        print('Polling updater started')
    elif args[0] =='webhook':
        updater.start_webhook(listen='0.0.0.0',
                              port=8443,
                              url_path=config.get_token(),
                              key='../keys/private.key',
                              cert='../keys/cert.pem',
                              webhook_url='https://167.99.218.143:8443/' + config.get_token())
        print('Webhook updater started')
    else:
        raise ValueError('Wrong args provided. Enter either "polling" or "webhook".')
    updater.idle()


if __name__ == '__main__':
    args = sys.argv[1:]
    main(args)
