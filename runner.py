import datetime
import sys
import telegram
from telegram.ext import Updater, ConversationHandler
import logging
from telegram.utils.request import Request
import bot_states
import command_handlers
import config
import error_handlers
import input_handlers
from job_callbacks import reward_users
from mq_bot import MQBot
from telegram.ext import messagequeue as mq


def main(args):
    token = config.token()
    q = mq.MessageQueue(all_burst_limit=28, all_time_limit_ms=1017)
    request = Request(con_pool_size=8)
    bot = MQBot(token=token, request=request, mqueue=q)
    updater = telegram.ext.updater.Updater(bot=bot, request_kwargs={'read_timeout': 6, 'connect_timeout': 7})
    dispatcher = updater.dispatcher
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    change_wallet_command_handler = command_handlers.change_wallet_initiation_handler()
    withdraw_command_handler = command_handlers.withdraw_command_handler()
    start_command_handler = command_handlers.start_command_handler()
    transfer_balance_to_deposit_command_handler = command_handlers.transfer_balance_to_deposit()

    main_handler = input_handlers.main_menu_input_handler()
    change_wallet_handler = input_handlers.change_wallet_input_handler()
    create_withdraw_input_handler = input_handlers.withdrawal_input_handler()
    transfer_balance_to_deposit_input_handler = input_handlers.transfer_balance_to_deposit_input_handler()

    callback_query_handler = input_handlers.callback_query_handler()

    conv_handler = ConversationHandler(
        entry_points=[
            start_command_handler,
            main_handler
        ],
        states={
            bot_states.MAIN: [
                start_command_handler,
                main_handler,
                change_wallet_command_handler,
                withdraw_command_handler,
                transfer_balance_to_deposit_command_handler
            ],
            bot_states.WALLET_CHANGE: [change_wallet_handler],
            bot_states.CREATE_WITHDRAWAL: [create_withdraw_input_handler],
            bot_states.TRANSFER_BALANCE_TO_DEPOSIT: [transfer_balance_to_deposit_input_handler]
        },
        fallbacks=[]
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(callback_query_handler)
    dispatcher.add_error_handler(error_handlers.error_callback)

    j = updater.job_queue
    j.run_daily(reward_users, time=datetime.time(hour=3))

    if not len(args) or args[0] == 'polling':
        updater.start_polling()
        print('Polling updater started')
    elif args[0] == 'webhook':
        updater.start_webhook(listen='0.0.0.0',
                              port=8443,
                              url_path=config.token(),
                              key='../keys/private.key',
                              cert='../keys/cert.pem',
                              webhook_url='https://167.99.218.143:8443/' + config.token())
        print('Webhook updater started')
    else:
        raise ValueError('Wrong args provided. Use either "polling" or "webhook".')
    updater.idle()


if __name__ == '__main__':
    args = sys.argv[1:]
    main(args)
