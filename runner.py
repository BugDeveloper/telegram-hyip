import datetime
import sys
import telegram
from telegram.ext import Updater, ConversationHandler, MessageHandler, Filters
import logging
import bot_states
import config
import error_handlers
import command_handlers
import input_handlers
import mq_bot
from flask_app import app
from job_callbacks import reward_users


def main(args):
    mq_bot.init()
    updater = telegram.ext.updater.Updater(bot=mq_bot.instance,
                                           request_kwargs={'read_timeout': 6, 'connect_timeout': 7})
    dispatcher = updater.dispatcher

    change_wallet_command_handler = command_handlers.change_wallet_initiation_handler()
    withdraw_command_handler = command_handlers.withdraw_command_handler()
    start_command_handler = command_handlers.start_command_handler()
    transfer_balance_to_deposit_command_handler = command_handlers.transfer_balance_to_deposit()
    transfer_balance_to_user_command_handler = command_handlers.transfer_balance_to_user()

    main_handler = input_handlers.main_menu_input_handler()
    change_wallet_handler = input_handlers.change_wallet_input_handler()
    create_withdraw_input_handler = input_handlers.withdrawal_input_handler()
    transfer_balance_to_deposit_input_handler = input_handlers.transfer_balance_to_deposit_input_handler()
    transfer_balance_to_user_input_handler = input_handlers.transfer_balance_to_user_input_handler()
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
                transfer_balance_to_deposit_command_handler,
                transfer_balance_to_user_command_handler
            ],
            bot_states.WALLET_CHANGE: [
                change_wallet_handler,
            ],
            bot_states.CREATE_WITHDRAWAL: [
                create_withdraw_input_handler,
            ],
            bot_states.TRANSFER_BALANCE_TO_DEPOSIT: [
                transfer_balance_to_deposit_input_handler,
            ],
            bot_states.TRANSFER_BALANCE_TO_USER: [
                transfer_balance_to_user_input_handler,
            ]
        },
        fallbacks=[],
        timed_out_behavior=[
            MessageHandler(
                Filters.text,
                error_handlers.timed_out_handler
            )
        ],
        run_async_timeout=1.0
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(callback_query_handler)
    dispatcher.add_error_handler(error_handlers.error_callback)

    j = updater.job_queue
    j.run_daily(reward_users, time=datetime.time(hour=3))

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

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
    app.run()
    updater.idle()


if __name__ == '__main__':
    args = sys.argv[1:]
    main(args)
