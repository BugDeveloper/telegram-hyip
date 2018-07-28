import datetime

import config


# 'После пополнения счета, сумма на счете будет расти' \
# ' в соответствии с установленной процентной ставкой, а также количеством Ваших рефералов.\n' \

def eth_address_taken():
    return 'Данный eth адрес уже занят.'


def not_registered():
    return 'Вы не зарегистрированны в системе. Для начала введите команду /start.'


def withdrawals(withdrawals_list):
    if len(withdrawals_list) == 0:
        return 'У вас пока нет выводов.'
    withdrawals = 'Ваши последние выводы:\n'
    for index, withdrawal in enumerate(withdrawals_list):
        withdrawals += f'{withdrawal.amount} ETH - {withdrawal.created_at}\n'
    return withdrawals


def top_ups(top_ups_list):
    if len(top_ups_list) == 0:
        return 'У вас пока нет пополнений.'
    top_ups = 'Ваши последние пополнения:\n'
    for top_up in top_ups_list:
        top_ups += f'{top_up.amount} ETH - {top_up.created_at}\n'
    return top_ups


def back_to_main_menu():
    return 'Возврат в главное меню.'


def balance_transferred_to_deposit(amount):
    return f'Сумма в {amount} ETH успешно переведена в депозит.'


def not_enough_eth():
    return 'У вас недостаточно средств. Введите другую сумму.'


def withdrawal_created(wallet):
    return f'Средства будут перечислены на адрес {wallet} Вами адрес в рассчетный день.'


def minimal_withdraw_amount():
    return f'Сумма перевода должна превышать {config.minimal_eth_withdraw()} ETH.'


def partners(user_id, user_invited_by=None):
    partners_info = ''
    if user_invited_by:
        partners_info = 'Вы были приглашены пользователем: @{}\n'.format(user_invited_by.username)
    referral_link = 'https://telegram.me/' + config.bot_username() + '?start=' + str(user_id)
    partners_info += f'Ваша реферальная ссылка: {referral_link}\n'

    level_percentage = config.get_referral_levels_percentage()

    for idx, percentage in enumerate(level_percentage):
        partners_info += 'Уровень {} - {}%\n'.format(idx + 1, percentage * 100)

    return partners_info


def invalid_input():
    return 'Введите валидное значение.'


def wallet_successfully_set(wallet):
    return f'ETH кошелёк {wallet} успешно привязан к вашему аккаунту.'


def deposit(user_deposit, user_balance, sum_deposit_reward):
    return f'Ваш депозит: {user_deposit:.7f} ETH. \n' \
           f'Ваш баланс: {user_balance:.7f} ETH. \n' \
           f'Процентная ставка: {config.daily_reward() * 100}% в день.\n' \
           f'Суммарный заработок с депозита: {sum_deposit_reward:.7f} ETH.\n' \
           'Для перевода средств из баланса в депозит введите команду /transfer_deposit.'


def top_up():
    return f'ETH адрес для инвестиций: {config.project_eth_address()}\n' \
           'Для увеличения депозита, вы можете переводить на этот адрес любую сумму с вашего привязанного кошелька.\n' \
           'Чтобы изменить адрес ETH кошелька, введите команду /wallet .'


def withdraw(wallet):
    return f'Ваш адрес для вывода: {wallet}.\n' \
           'Чтобы изменить адрес ETH кошелька, введите команду /wallet .\n' \
           'Для вывода средств используйте команду /withdraw.'


def wallet_not_set():
    return 'Ваш адрес для вывода не установлен.'


def enter_new_wallet():
    return 'Введите новый адрес для вывода:'


def transfer_balance_to_deposit(balance):
    return f'Ваш баланс: {balance} ETH .\n' \
           'Введите сумму, которую хотите перевести в депозит:'


def create_withdrawal(balance):
    return f'Ваш баланс: {balance} ETH .\n' \
           'Введите сумму, которую хотите вывести:'


def help():
    return 'Для начисления процентов сумма' \
           f' депозита должна быть не менее {config.eth_minimal_deposit()} ETH.'
