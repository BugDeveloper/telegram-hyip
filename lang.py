from decimal import Decimal, ROUND_HALF_EVEN

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
    return f'Сумма в {amount:.7f} ETH успешно переведена в пользователю @{to_user}.'


def balance_transferred_from_user(amount, from_user):
    return f'Пользователь @{from_user} ETH перевёл вам на баланс {amount} ETH.'


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


def partners(user_id, user_invited_by=None):
    partners_info = ''
    if user_invited_by:
        partners_info = 'Вы были приглашены пользователем: @{}\n'.format(user_invited_by.username)
    referral_link = 'https://telegram.me/' + config.bot_username() + '?start=' + str(user_id)
    partners_info += f'Ваша реферальная ссылка: {referral_link}\n'

    level_percentage = tariffs.get_referral_levels_percentage()

    for idx, percentage in enumerate(level_percentage):
        partners_info += f'Уровень {idx + 1} - {percentage * 100}%\n'

    return partners_info


def invalid_input():
    return 'Введите валидное значение.'


def wallet_successfully_set(wallet):
    return f'ETH кошелёк {wallet} успешно привязан к вашему аккаунту.'


def deposit(user_deposit, user_balance, user_reward, sum_deposit_reward):
    text = f'Депозит: {user_deposit:.7f} ETH. \n'

    user_deposit_dec = Decimal(user_deposit).quantize(Decimal('.0001'), rounding=ROUND_HALF_EVEN)
    minimal_eth_deposit_dec = Decimal(
        tariffs.eth_minimal_deposit()).quantize(
        Decimal('.0001'),
        rounding=ROUND_HALF_EVEN
    )

    if user_deposit_dec.compare(minimal_eth_deposit_dec) < 0:
        text += f'Минимальная сумма депозита для начисления процентов: {tariffs.eth_minimal_deposit()} ETH'
        return text
    text += f'Баланс: {user_balance:.7f} ETH. \n' \
            f'Процентная ставка: {user_reward * 100}% в день.\n' \
            f'Суммарный заработок с депозита: {sum_deposit_reward:.7f} ETH.\n' \
            'Для перевода средств из баланса в депозит введите команду /transfer_deposit.\n' \
            'Для перевода средст другому пользователю введите команду /transfer_user.'
    return text


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
    return f'Для начисления процентов сумма депозита должна быть не менее {tariffs.eth_minimal_deposit()} ETH.'
