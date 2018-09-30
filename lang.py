import tariffs
import config


def eth_address_taken():
    return 'Данный eth адрес уже занят.'


def not_registered():
    return 'Вы не зарегистрированны в системе. Для начала введите команду /start.'


def withdrawals(withdrawals_list):
    if len(withdrawals_list) == 0:
        return 'У вас пока нет выводов.'
    withdrawals = 'Ваши последние выводы:\n'
    for index, withdrawal in enumerate(withdrawals_list):
        withdrawals += f'{withdrawal.amount:.7f} ETH - {withdrawal.created_at}\n'
    return withdrawals


def top_ups(top_ups_list):
    if len(top_ups_list) == 0:
        return 'У вас пока нет пополнений.'
    top_ups = 'Ваши последние пополнения:\n'
    for top_up in top_ups_list:
        top_ups += f'{top_up.amount:.7f} ETH - {top_up.created_at}\n'
    return top_ups


def back_to_main_menu():
    return 'Возврат в главное меню.'


def balance_transferred_to_user(amount, to_user):
    return f'Сумма в {amount:.7f} ETH успешно переведена в пользователю {to_user}.'


def balance_transferred_from_user(amount, from_user):
    return f'Пользователь {from_user} ETH перевёл вам на баланс {amount} ETH.'


def balance_transferred_to_deposit(amount):
    return f'Сумма в {amount:.7f} ETH успешно переведена в депозит.'


def not_approved_previous(amount):
    return f'Ваш прошлый вывод на сумму {amount:.7f} ETH ещё не был утверждён.' \
           f' Вы сможете создать новый запрос на вывод после утверджения предыдущего.'


def user_not_registered():
    return 'Такой пользователь не зарегистрирован.'


def not_enough_eth():
    return 'У вас недостаточно средств. Введите другую сумму.'


def wrong_command():
    return 'Введите валидную команду.'


def withdrawal_created(wallet):
    return f'Средства будут перечислены на адрес {wallet} в ближайшую среду или воскресенье.'


def minimal_withdraw_amount():
    return f'Сумма перевода должна превышать {tariffs.minimal_eth_withdraw()} ETH.'


def partners(user, bot_username, user_invited_by=None):
    partners_info = ''
    if user_invited_by:
        partners_info = f'Вы были приглашены пользователем: {user_invited_by}\n'
    referral_link = f'https://telegram.me/{bot_username}?start={str(user.chat_id)}'
    partners_info += f'Ваша реферальная ссылка: {referral_link}\n'

    level_percentage = tariffs.get_referral_levels_percentage()

    for idx, percentage in enumerate(level_percentage):
        partners_info += f'Уровень {idx + 1} - {percentage * 100 * user.deposit_reward}% в день\n'

    return partners_info


def invalid_input():
    return 'Введите валидное значение.'


def wallet_successfully_set(wallet):
    return f'ETH кошелёк {wallet} успешно привязан к вашему аккаунту.'


def deposit(user_deposit, user_balance, user_reward, sum_deposit_reward):
    text = f'Депозит: {user_deposit:.7f} ETH. \n'
    if user_deposit >= tariffs.eth_minimal_deposit():
        text += f'Баланс: {user_balance:.7f} ETH. \n' \
                f'Процентная ставка: {user_reward * 100}% в день.\n'
    else:
        text += f'Начальный депозит: {tariffs.eth_minimal_deposit()} ETH\n'
    text += 'Перевод из баланса в депозит: /transfer_deposit.\n' \
            'Перевод баланса пользователю: /transfer_user.'
    return text


def top_up(wallet):
    return f'Ваш кошелёк: {wallet}\n' \
           'Изменить адрес ETH кошелька: /wallet.\n' \
           f'ETH адрес для пополнения депозита: '


def top_up_invest_wallet():
    return f'*{config.project_eth_address()}*'


def withdraw(wallet):
    return f'Ваш кошелёк: {wallet}.\n' \
           'Изменить адрес ETH кошелька: /wallet .\n' \
           'Вывод средств: /withdraw.'


def wallet_not_set():
    return 'Ваш адрес для вывода не установлен.'


def enter_new_wallet():
    return 'Введите адрес вашего ETH кошелька:'


def transfer_balance_to_deposit(balance):
    return f'Ваш баланс: {balance:.7f} ETH .\n' \
           'Введите сумму, которую хотите перевести в депозит:'


def transfer_balance_to_user(balance):
    return f'Ваш баланс: {balance:.7f} ETH .\n' \
           'Введите имя пользователя (алиас) Telegram и сумму которую хотите перевести через пробел.\n' \
           'Например: "ivan 1"'


def create_withdrawal(balance):
    return f'Ваш баланс: {balance:.7f} ETH .\n' \
           'Введите сумму, которую хотите вывести:'


def help():
    return 'https://telegra.ph/ICO-DAY-09-14'
