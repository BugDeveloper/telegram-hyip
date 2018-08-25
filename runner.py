import datetime
import logging
import pickle
import sys
import threading
import time
import telegram
from telegram.ext import Updater, ConversationHandler, MessageHandler, Filters
from telegram.utils.promise import Promise
import bot_states
import command_handlers
import config
import error_handlers
import input_handlers
import mq_bot
from flask_app import app
from job_callbacks import reward_users


def main(args):
    def loadData():
        try:
            f = open('backup/conversations', 'rb')
            conv_handler.conversations = pickle.load(f)
            f.close()
        except FileNotFoundError:
            logging.error("Data file not found")
        except Exception:
            logging.error(sys.exc_info()[0])

    def saveData():
        resolved = dict()
        for k, v in conv_handler.conversations.items():
            if isinstance(v, tuple) and len(v) is 2 and isinstance(v[1], Promise):
                try:
                    new_state = v[1].result()
                except:
                    new_state = v[0]
                resolved[k] = new_state
            else:
                resolved[k] = v
        try:
            f = open('backup/conversations', 'wb+')
            pickle.dump(resolved, f)
            f.close()
        except:
            logging.error(sys.exc_info()[0])

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
        fallbacks=[

        ],
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
    loadData()
    app.run()
    updater.stop()
    print('DO NOT TURN OFF THE BUT UNTIL ITS DATA IS SAVED')
    print('Saving data...')
    saveData()
    print('DATA SAVED.')


if __name__ == '__main__':
    args = sys.argv[1:]
    main(args)
