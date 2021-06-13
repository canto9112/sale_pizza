from moltin import moltin_customer, moltin_cart
import time
from telegram_pizza.start_bot import start
from validate_email import validate_email


def send_mail(bot, update, access_token, products):
    users_reply = update.message.text
    is_valid_email = check_email(users_reply)
    if is_valid_email:
        username = update.message['chat']['first_name']
        moltin_customer.create_customer(access_token, username, users_reply)
        update.message.reply_text(f'Мы записали ваш заказ!\n'
                                  f'Информация о заказе придет на - {users_reply}\n\n'
                                  f'Ждем вас снова за покупками!')
        moltin_cart.clean_cart(access_token, update.message['chat']['id'])
        time.sleep(2.0)
        start(bot, update, products)
        return 'HANDLE_MENU'

    update.message.reply_text(f'Неправильно указана почта!\n'
                              f'Введите почту еще раз: ')
    return 'WAITING_EMAIL'


def check_email(email):
    is_valid = validate_email(email)
    return is_valid