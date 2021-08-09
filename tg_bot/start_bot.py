import logging
import textwrap
from functools import partial

import redis
from environs import Env
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import CallbackQueryHandler, CommandHandler, Filters, MessageHandler, PreCheckoutQueryHandler, \
    ShippingQueryHandler, Updater

import settings
from moltin import moltin_authentication, moltin_cart, moltin_file, moltin_flow, moltin_product
from tg_bot import bot_cart, distance_user, payments

logger = logging.getLogger(__file__)

env = Env()
env.read_env()

REDIS_PASSWORD = env("REDIS_PASSWORD")
REDIS_HOST = env("REDIS_HOST")
REDIS_PORT = env("REDIS_PORT")
TELEGRAM_TOKEN = env("TELEGRAM_TOKEN")
MOLTIN_CLIENT_ID = env('MOLTIN_CLIENT_ID')
MOLTIN_CLIENT_SECRET = env('MOLTIN_CLIENT_SECRET')
MOLTIN_TOKEN = moltin_authentication.get_authorization_token(MOLTIN_CLIENT_ID, MOLTIN_CLIENT_SECRET)
TG_CHAT_ID = env('TG_CHAT_ID')

id_customer = None
page = 0
MENU_LEN = 8
back_button = InlineKeyboardButton("⏪ Назад", callback_data="Назад")
next_button = InlineKeyboardButton("Вперед ⏩", callback_data="Вперед")


def error_handler(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def shortening_menu(long_menu, size):
    short_menu = []
    while len(long_menu) > size:
        short_menu.append(long_menu[:size])
        long_menu = long_menu[size:]
    short_menu.append(long_menu)
    return short_menu


def start_keyboard(products, page):
    keyboard = [[InlineKeyboardButton(product['name'], callback_data=product['id'])] for product in products]
    menu = shortening_menu(keyboard, MENU_LEN)
    return menu[page]


def first_page(bot, update, products):
    chat_id = update.message.chat_id
    menu = start_keyboard(products, page)
    buttons = [next_button]
    menu.append(buttons)
    reply_markup = InlineKeyboardMarkup(menu)
    update.message.reply_text('Выберите пиццу:', reply_markup=reply_markup)
    db.set(str(chat_id) + '_page', page)
    return "PAGE_SELECTION"


def page_selection(bot, update, products):
    query = update.callback_query
    chat_id = query.message.chat_id
    page_number = db.get(f'{chat_id}_page').decode("utf-8")

    if query.data == 'Вперед':
        new_page = int(page_number) + 1
        menu = start_keyboard(products, new_page)

        if len(menu) < MENU_LEN:
            buttons = [back_button]
            menu.append(buttons)
            reply_markup = InlineKeyboardMarkup(menu)
            del_old_message(bot, update)
            bot.send_message(chat_id=query.message.chat_id, text='Выберите пиццу:', reply_markup=reply_markup)
            db.set(f'{chat_id}_page', new_page)
            return "PAGE_SELECTION"

        buttons = [back_button, next_button]
        menu.append(buttons)
        reply_markup = InlineKeyboardMarkup(menu)
        del_old_message(bot, update)
        bot.send_message(chat_id=query.message.chat_id, text='Выберите пиццу:', reply_markup=reply_markup)
        db.set(f'{chat_id}_page', new_page)
        return "PAGE_SELECTION"

    elif query.data == 'Назад':
        new_page = int(page_number) - 1
        menu = start_keyboard(products, new_page)

        if new_page == 0:
            buttons = [next_button]
            menu.append(buttons)
            reply_markup = InlineKeyboardMarkup(menu)
            del_old_message(bot, update)
            bot.send_message(chat_id=query.message.chat_id, text='Выберите пиццу:', reply_markup=reply_markup)
            db.set(f'{chat_id}_page', new_page)
            return "PAGE_SELECTION"

        buttons = [back_button, next_button]
        menu.append(buttons)
        reply_markup = InlineKeyboardMarkup(menu)
        del_old_message(bot, update)
        bot.send_message(chat_id=query.message.chat_id, text='Выберите пиццу:', reply_markup=reply_markup)
        db.set(f'{chat_id}_page', new_page)
        return "PAGE_SELECTION"
    else:
        handle_button_menu(bot, update)
        return "HANDLE_DESCRIPTION"


def handle_button_menu(bot, update):
    query = update.callback_query
    product = moltin_product.get_product(MOLTIN_TOKEN, query.data)
    product_name = product['data']['name']
    price = product['data']['price'][0]['amount']
    currency = product['data']['price'][0]['currency']
    description = product['data']['description']
    file_id = product['data']['relationships']['main_image']['data']['id']

    keyboard = [[InlineKeyboardButton(f"Положить в корзину {product_name}",
                                      callback_data=f'{product_name}/{query.data}')],
                [InlineKeyboardButton("Меню", callback_data=f'{"Меню"}/{query.data}')],
                [InlineKeyboardButton("Корзина", callback_data=f'{"Корзина"}/{query.data}')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    image = moltin_file.get_image_url(MOLTIN_TOKEN, file_id)
    bot.send_photo(query.message.chat_id, image, caption=f"*{product_name}*\n\n"
                                                         f"*Цена*: {price} {currency}.\n"
                                                         f"*Описание*: _{description}_",
                                                         reply_markup=reply_markup,
                                                         parse_mode=ParseMode.MARKDOWN)
    del_old_message(bot, update)
    return "HANDLE_DESCRIPTION"


def handle_description(bot, update, products):
    query = update.callback_query
    chat_id = query.message.chat_id
    button, product_id = query.data.split('/')

    if button == 'Меню':
        del_old_message(bot, update)
        page_number = db.get(f'{chat_id}_page').decode("utf-8")
        menu = start_keyboard(products, int(page_number))
        buttons = [next_button]
        menu.append(buttons)
        reply_markup = InlineKeyboardMarkup(menu)
        bot.send_message(chat_id=query.message.chat_id, text='Выберите пиццу:', reply_markup=reply_markup)
        return "PAGE_SELECTION"

    elif button == 'Корзина':
        bot_cart.update_cart(bot, update, MOLTIN_TOKEN)
        return "HANDLE_CART"

    elif button:
        moltin_cart.add_product_to_cart(MOLTIN_TOKEN, product_id, query.message.chat_id, 1)
        update.callback_query.answer(text=f"{button} добавлена в корзину")
        return "HANDLE_DESCRIPTION"


def get_cart(bot, update, products):
    query = update.callback_query
    button, total_price = query.data.split('/')
    chat_id = query.message.chat_id
    if button == 'Меню':
        del_old_message(bot, update)
        page_number = db.get(f'{chat_id}_page').decode("utf-8")
        menu = start_keyboard(products, int(page_number))
        buttons = [next_button]
        menu.append(buttons)
        reply_markup = InlineKeyboardMarkup(menu)
        bot.send_message(chat_id=query.message.chat_id, text='Выберите пиццу:', reply_markup=reply_markup)
        return "PAGE_SELECTION"

    elif button == 'Оплатить':
        bot.send_message(chat_id=query.message.chat_id, text='Введите адрес доставки: ')
        return "WAITING_ADDRESS"

    else:
        moltin_cart.delete_product_in_cart(MOLTIN_TOKEN, query.message.chat_id, button)
        bot_cart.update_cart(bot, update, MOLTIN_TOKEN)
        return "HANDLE_CART"


def waiting_address(bot, update):
    users_reply = update.message.text
    chat_id = update.message.chat_id
    lat, lon = distance_user.get_user_location(bot, update)

    if users_reply is None:
        address = distance_user.get_address_from_coords(f'{lon} {lat}')
        customer_id = moltin_flow.create_customer(MOLTIN_TOKEN,
                                                  settings.customer_flow_slug,
                                                  address,
                                                  str(chat_id),
                                                  lat, lon)
        db.set(f'{chat_id}_id_customer', customer_id['data']['id'])

    else:
        customer_id = moltin_flow.create_customer(MOLTIN_TOKEN,
                                                  settings.customer_flow_slug,
                                                  users_reply,
                                                  str(chat_id),
                                                  lat, lon)
    db.set(f'{chat_id}_id_customer', customer_id['data']['id'])
    nearby_pizzeria = get_nearby_pizzeria(lat, lon)
    send_choosing_delivery(bot, update, nearby_pizzeria)
    return "ADDRESS_OR_DELIVERY"


def get_address_or_delivery(bot, update):
    query = update.callback_query
    button, delivery_price = query.data.split('/')
    chat_id = update.callback_query.message.chat_id
    customer_id = db.get(f'{chat_id}_id_customer').decode("utf-8")
    customer_lat, customer_lon = moltin_flow.get_entry(MOLTIN_TOKEN,
                                                       settings.customer_flow_slug, customer_id)
    nearby_pizzeria = get_nearby_pizzeria(customer_lat, customer_lon)
    cart = moltin_cart.get_cart(MOLTIN_TOKEN, query.message.chat_id)
    total_price = cart['data']['meta']['display_price']['with_tax']['formatted']
    new_total = total_price.replace(' ', '')

    if button == 'Доставка':
        price = int(new_total) + int(delivery_price)
        payments.start_with_shipping_callback(bot, update, chat_id, price)

    elif button == 'Самовывоз':
        nearby_pizzeria_lat = nearby_pizzeria['lat']
        nearby_pizzeria_lon = nearby_pizzeria['lon']
        text = textwrap.dedent(f'''
                Вот адрес ближайшей пиццерии: {nearby_pizzeria["address"]}.    
                До новых встреч!
                Для возврата в начало магазина нажмите /start ''')

        bot.send_message(chat_id=query.message.chat_id,
                         text=text)
        bot.send_location(chat_id=chat_id, latitude=nearby_pizzeria_lat, longitude=nearby_pizzeria_lon)
        payments.start_with_shipping_callback(bot, update, chat_id, int(new_total))
    return 'SEND_MESSAGE_COURIER'


def successful_payment_callback(bot, update):
    update.message.reply_text("Спасибо за оплату!")
    send_message_courier(bot, update)
    return 'SEND_MESSAGE_COURIER'


def send_message_courier(bot, update):
    chat_id = update.message.chat_id
    customer_id = db.get(f'{chat_id}_id_customer').decode("utf-8")
    customer_lat, customer_lon = moltin_flow.get_entry(MOLTIN_TOKEN,
                                                       settings.customer_flow_slug, customer_id)
    nearby_pizzeria = get_nearby_pizzeria(customer_lat, customer_lon)
    courier_id = nearby_pizzeria['courier']
    bot.send_message(chat_id=courier_id, text=f'Доставить этот заказ вот сюда:')
    bot_cart.send_cart_courier(bot, update, MOLTIN_TOKEN, courier_id)
    bot.send_location(chat_id=courier_id, latitude=customer_lat, longitude=customer_lon)
    bot.send_message(chat_id=chat_id, text=f'''Курьер получил ваш заказ! До новых встреч!
                                               Для возврата в начало магазина нажмите /start''')
    moltin_cart.clean_cart(MOLTIN_TOKEN, chat_id)
    wait_time = 3
    job_queue.run_once(send_message_if_didnt_arrive, wait_time)
    return 'FINISH'


def send_message_if_didnt_arrive(bot, job):
    text = textwrap.dedent(f'''
            Приятного аппетита!   
            Если пицца не пришла, заказ бесплатно!''')
    bot.send_message(chat_id=TG_CHAT_ID, text=text)


def get_nearby_pizzeria(lat, lon):
    all_entries = moltin_flow.get_all_entries(MOLTIN_TOKEN, settings.pizzerias_flow_slug)
    all_pizzerias = []
    for entries in all_entries:
        dist = distance_user.get_distance(entries['latitude'], entries['longitude'], lat, lon)
        all_pizzerias.append({'address': entries['address'],
                              'lat': entries['latitude'],
                              'lon': entries['longitude'],
                              'distance_to_user': dist,
                              'courier': entries['courier']})

    def get_pizzerias_distance(pizzerias):
        return pizzerias['distance_to_user']

    nearby_pizzeria = min(all_pizzerias, key=get_pizzerias_distance)
    return nearby_pizzeria


def send_choosing_delivery(bot, update, nearby_pizzeria):
    up_5_km_delivery_price = 100
    up_20_km_delivery_price = 300

    if nearby_pizzeria["distance_to_user"] <= 500:
        keyboard = [
            [InlineKeyboardButton('Доставка', callback_data=f'Доставка/{""}')],
            [InlineKeyboardButton("Самовывоз", callback_data=f'Самовывоз/{""}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = textwrap.dedent(f'''
                Вы можете забрать пиццу самостоятельно по адресу:.    
                {nearby_pizzeria["address"]}.
                Или заказать бесплатную доставку ''')
        update.message.reply_text(text, reply_markup=reply_markup)

    elif 500 < nearby_pizzeria["distance_to_user"] <= 5000:
        keyboard = [
            [InlineKeyboardButton('Доставка', callback_data=f'Доставка/{up_5_km_delivery_price}')],
            [InlineKeyboardButton("Самовывоз", callback_data=f'Самовывоз/{""}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = textwrap.dedent(f'''
                Доставка будет стоить {up_5_km_delivery_price} рублей.   
                Доставляем или самовывоз?''')
        update.message.reply_text(text, reply_markup=reply_markup)

    elif 5000 < nearby_pizzeria["distance_to_user"] <= 20000:
        keyboard = [
            [InlineKeyboardButton('Доставка', callback_data=f'Доставка/{up_20_km_delivery_price}')],
            [InlineKeyboardButton("Самовывоз", callback_data=f'Самовывоз/{""}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = textwrap.dedent(f'''
                Доставка будет стоить {up_20_km_delivery_price} рублей.  
                Доставляем или самовывоз?''')
        update.message.reply_text(text, reply_markup=reply_markup)
    else:
        text = textwrap.dedent(f'''
                Слишком далеко   
                Ближайшая пиццерия аж в {int(nearby_pizzeria["distance_to_user"] / 1000)} км
                Для возврата в начало магазина нажмите /start''')
        update.message.reply_text(text)


def handle_users_reply(bot, update):
    products = moltin_product.get_all_products(MOLTIN_TOKEN)

    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(chat_id).decode("utf-8")

    states_functions = {
        'START': partial(first_page, products=products),
        "PAGE_SELECTION": partial(page_selection, products=products),
        'HANDLE_MENU': handle_button_menu,
        'HANDLE_DESCRIPTION': partial(handle_description, products=products),
        'HANDLE_CART': partial(get_cart, products=products),
        'WAITING_ADDRESS': waiting_address,
        'ADDRESS_OR_DELIVERY': get_address_or_delivery,
        'WAITING_PAYMENTS': payments.start_with_shipping_callback,
        'SEND_MESSAGE_COURIER': send_message_courier,
        'FINISH': 'FINISH'

    }
    state_handler = states_functions[user_state]
    next_state = state_handler(bot, update)
    db.set(chat_id, next_state)


def get_database_connection(host, port, password):
    database = redis.Redis(host=host,
                           port=port,
                           password=password)
    return database


def del_old_message(bot, update):
    query = update.callback_query
    old_message = update.callback_query.message['message_id']
    bot.delete_message(chat_id=query.message.chat_id,
                       message_id=old_message)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    db = get_database_connection(REDIS_HOST,
                                 REDIS_PORT,
                                 REDIS_PASSWORD)

    updater = Updater(TELEGRAM_TOKEN)
    job_queue = updater.job_queue
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.location, waiting_address))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    dispatcher.add_handler(ShippingQueryHandler(payments.shipping_callback))
    dispatcher.add_handler(PreCheckoutQueryHandler(payments.precheckout_callback))
    dispatcher.add_handler(MessageHandler(Filters.successful_payment, successful_payment_callback))

    dispatcher.add_error_handler(error_handler)
    updater.start_polling()
