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
        withdrawals += str(withdrawal.amount) + ' ETH - ' + str(withdrawal.created_at.date()) + '\n'
    return withdrawals


def top_ups(top_ups_list):
    if len(top_ups_list) == 0:
        return 'У вас пока нет пополнений.'
    top_ups = 'Ваши последние пополнения:\n'
    for top_up in top_ups_list:
        top_ups += str(top_up.amount) + ' ETH - ' + str(top_up.created_at.date()) + '\n'
    return top_ups


def back_to_main_menu():
    return 'Возврат в главное меню.'


def partners(user_id, user_invited_by=None):
    partners_info = ''
    if user_invited_by:
        partners_info = 'Вы были приглашены пользователем: @{}\n'.format(user_invited_by.username)
    referral_link = 'https://telegram.me/' + config.get_bot_username() + '?start=' + str(user_id)
    partners_info += f'Ваша реферальная ссылка: {referral_link}\n'

    level_percentage = config.get_referral_levels_percentage()

    for idx, percentage in enumerate(level_percentage):
        partners_info += 'Уровень {} - {}%\n'.format(idx + 1, percentage * 100)

    return partners_info


def invalid_input():
    return 'Введите валидное значение.'


def wallet_successfully_set(wallet):
    return f'ETH кошелёк {wallet} успешно привязанн к вашему аккаунту.'


def deposit(user_deposit, user_balance, sum_deposit_reward):
    return f'Ваш депозит: {user_deposit:.7f} ETH. \n' \
           f'Ваш баланс: {user_balance:.7f} ETH. \n' \
           f'Процентная ставка: {config.get_daily_reward() * 100}% в день.\n' \
           f'Суммарный заработок с депозита: {sum_deposit_reward:.7f} ETH.'


def top_up():
    return f'ETH адрес для инвестиций: {config.get_project_eth_address()}\n' \
           'Вы можете переводить на этот адрес любую сумму в любое время с вашего привязанного кошелька. ' \
           'Средства будут зачислены на Ваш счет в течение часа.\n' \
           'Чтобы изменить адрес ETH кошелька для вывода, введите команду /wallet .'


def withdraw(wallet):
    return f'Ваш адрес для вывода: {wallet}.\n' \
            'Средства будут перечислены на указанный Вами адрес в рассчетный день.\n' \
            'Чтобы изменить адрес ETH кошелька для вывода, введите команду /wallet .\n' \
            'Для вывода средств введите /withdraw <сумма>.'


def wallet_not_set():
    return 'Ваш адрес для вывода не установлен.'


def enter_new_wallet():
    return 'Введите новый адрес для вывода:'


def withdrawn(wallet):
    return f'Ваши средства успешно поставлены на вывод на кошелек {wallet} и ждут подтвержения.'


def withdraw_how_much():
    return 'Сколько вы хотите вывести?'


def help():
    return 'Для начисления процентов сумма' \
           f' депозита должна быть не менее {config.get_eth_minimal_deposit()} ETH.'
