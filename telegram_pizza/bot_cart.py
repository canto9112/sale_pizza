from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

from moltin import moltin_cart
import telegram_pizza
from pprint import pprint
from telegram_pizza import start_bot


def update_cart(bot, update, access_token):
    query = update.callback_query

    button_menu = [InlineKeyboardButton("Меню", callback_data="Меню")]
    button_pay = [InlineKeyboardButton("Оплатить", callback_data="Оплатить")]

    cart_items = moltin_cart.get_cart_items(access_token, query.message.chat_id)
    cart = moltin_cart.get_cart(access_token, query.message.chat_id)
    total_price = cart['data']['meta']['display_price']['with_tax']['formatted']

    products_in_cart = []
    keyboard = []
    for product_in_cart in cart_items['data']:

        product_name = product_in_cart['name']
        description = product_in_cart['description']
        price = product_in_cart['meta']['display_price']['with_tax']['unit']['formatted']
        quantity = product_in_cart['quantity']
        all_price = product_in_cart['meta']['display_price']['with_tax']['value']['formatted']

        button = [InlineKeyboardButton(f'Убрать из корзины {product_name}', callback_data=product_in_cart['id'])]
        keyboard.append(button)
        products_in_cart.append(f'{product_name}\n'
                                f'{description}\n'
                                f'{price}за пиццу\n'
                                f'{quantity} штук в корзине на {all_price}\n\n')

    keyboard.append(button_menu)
    keyboard.append(button_pay)
    reply_markup = InlineKeyboardMarkup(keyboard)
    cart_text = ''.join(products_in_cart)

    start_bot.del_old_message(bot, update)
    bot.send_message(chat_id=query.message.chat_id, text=f'{cart_text}\n'
                                                         f'*Всего на сумму: {total_price}*', reply_markup=reply_markup,
                                                         parse_mode=ParseMode.MARKDOWN)


def send_cart_courier(bot, update, access_token, courier_id):
    query = update.callback_query

    cart_items = moltin_cart.get_cart_items(access_token, query.message.chat_id)
    cart = moltin_cart.get_cart(access_token, query.message.chat_id)
    total_price = cart['data']['meta']['display_price']['with_tax']['formatted']

    products_in_cart = []
    for product_in_cart in cart_items['data']:

        product_name = product_in_cart['name']
        description = product_in_cart['description']
        price = product_in_cart['meta']['display_price']['with_tax']['unit']['formatted']
        quantity = product_in_cart['quantity']
        all_price = product_in_cart['meta']['display_price']['with_tax']['value']['formatted']

        products_in_cart.append(f'{product_name} - {quantity} шт.\n')

    cart_text = ''.join(products_in_cart)

    start_bot.del_old_message(bot, update)
    bot.send_message(chat_id=courier_id, text=f'{cart_text}\n'
                                                         f'*Всего на сумму: {total_price}*',
                                                         parse_mode=ParseMode.MARKDOWN)