from telegram import (LabeledPrice, ShippingOption, Update)
from environs import Env


env = Env()
env.read_env()


def start_with_shipping_callback(bot, update, chat_id, price):
    payment_token = env('TELEGRAM_PAYMENT')
    title = "Магазин sale pizza"
    description = "Payment Example using python-telegram-bot"
    payload = "Custom-Payload"
    start_parameter = "test-payment"
    currency = "RUB"
    prices = [LabeledPrice("Test", price * 100)]
    bot.sendInvoice(chat_id, title, description, payload,
                    payment_token, start_parameter, currency, prices)


def shipping_callback(bot, update):
    query = update.shipping_query
    if query.invoice_payload != 'Custom-Payload':
        bot.answer_shipping_query(shipping_query_id=query.id, ok=False,
                                  error_message="Something went wrong...")
        return
    else:
        options = list()
        options.append(ShippingOption('1', 'Shipping Option A', [LabeledPrice('A', 100)]))
        price_list = [LabeledPrice('B1', 150), LabeledPrice('B2', 200)]
        options.append(ShippingOption('2', 'Shipping Option B', price_list))
        bot.answer_shipping_query(shipping_query_id=query.id, ok=True, shipping_options=options)


def precheckout_callback(bot, update):
    query = update.pre_checkout_query

    if query.invoice_payload != 'Custom-Payload':
        bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=False,
                                      error_message="Something went wrong...")
    else:
        bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=True)


# def successful_payment_callback(bot, update):
#     update.message.reply_text("Спасибо за оплату!")
