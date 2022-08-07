import os
import urllib.parse as urllibparse
from telegram import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import (
    Dispatcher, CommandHandler,
    MessageHandler, CallbackQueryHandler,
    Filters,
    ConversationHandler,
    PreCheckoutQueryHandler,
    ShippingQueryHandler,
    ContextTypes
)
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, 
                     KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove,
                     LabeledPrice, ShippingOption)
from telegram import __version__ as TG_VER

from django.conf import settings
from tgbot.handlers.payments.messages import *
from tgbot.handlers.payments.answers import *
from tgbot.handlers.main.answers import START_MENU_FULL
import tgbot.models as mymodels
from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.filters import FilterPrivateNoCommand
from tgbot.handlers.commands import command_start
from tgbot.handlers.utils import send_message
from tgbot.utils import extract_user_data_from_update, mystr, is_date, is_email, get_uniq_file_name
from tgbot.handlers.files import _get_file_id
# Возврат к главному меню в исключительных ситуациях
def pay_stop(update: Update, context: CallbackContext):
    # Заканчиваем разговор.
    command_start(update, context)
    return ConversationHandler.END

# Временная заглушка
def blank(update: Update, context: CallbackContext):
    A=90
    pass

# Возврат к главному меню по кнопке
def back_to_start(update: Update, context: CallbackContext):
    # Заканчиваем разговор.
    command_start(update, context)
    return ConversationHandler.END

def bad_callback_enter(update: Update, context: CallbackContext):
    update.message.reply_text(ASK_REENTER, reply_markup=make_keyboard(EMPTY,"usual",2))

# Начало работы с платежами
# def start_manage_pay(update: Update, context: CallbackContext):
#     userdata = extract_user_data_from_update(update)
#     user = mymodels.User.get_user_by_username_or_user_id(userdata["user_id"])
#     context.user_data["user"] = user
  
#     update.message.reply_text(PAY_HELLO, reply_markup=make_keyboard(PAY_BACK,"usual",1))
#     return "start_payment"


def make_invoice(update: Update, context: CallbackContext):
    """Sends an invoice with shipping-payment."""
    chat_id = update.message.chat_id
    title = "Payment Example"
    description = "Payment Example using python-telegram-bot"
    # select a payload just for you to recognize its the donation from your bot
    payload = "Custom-Payload"
    # In order to get a provider_token see https://core.telegram.org/bots/payments#getting-a-token
    currency = "RUB"
    # price in rubls
    price = 125.37
    # price * 100 so as to include 2 decimal points
    # check https://core.telegram.org/bots/payments#supported-currencies for more details
    prices = [LabeledPrice("Test", int(price * 100))]

    # optionally pass need_name=True, need_phone_number=True,
    # need_email=True, need_shipping_address=True, is_flexible=True
    # context.bot.send_invoice(
    #     chat_id,
    #     title,
    #     description,
    #     payload,
    #     settings.PAYMENT_PROVIDER_TOKEN,
    #     currency,
    #     prices,
    #     need_name=True,
    #     need_phone_number=True,
    #     need_email=True,
    #     need_shipping_address=True,
    #     is_flexible=True,
    # )

    context.bot.send_invoice(
        chat_id,
        title=title,
        description=description,
        provider_token=settings.PAYMENT_PROVIDER_TOKEN,
        currency=currency,
        is_flexible=False,  # True если конечная цена зависит от способа доставки
        prices=prices,
        need_phone_number=True,
        need_email=True,
        need_shipping_address=True,
        payload=payload,
        start_parameter='my-invoice-example',
    )

    return "proc_invoice"

# after (optional) shipping, it's the pre-checkout
def precheckout_callback(update: Update, context: CallbackContext) -> None:
    """Answers the PreQecheckoutQuery"""
    query = update.pre_checkout_query
    # check the payload, is this from your bot?
    if query.invoice_payload != "Custom-Payload":
        # answer False pre_checkout_query
        query.answer(ok=False, error_message="Something went wrong...")
    else:
        query.answer(ok=True)
    return 

def shipping_callback(update: Update, context: CallbackContext) -> None:
    """Answers the ShippingQuery with ShippingOptions"""
    query = update.shipping_query
    # check the payload, is this from your bot?
    if query.invoice_payload != "Custom-Payload":
        # answer False pre_checkout_query
        query.answer(ok=False, error_message="Something went wrong...")
        return

    # First option has a single LabeledPrice
    options = [ShippingOption("1", "Shipping Option A", [LabeledPrice("A", 100)])]
    # second option has an array of LabeledPrice objects
    price_list = [LabeledPrice("B1", 150), LabeledPrice("B2", 200)]
    options.append(ShippingOption("2", "Shipping Option B", price_list))
    query.answer(ok=True, shipping_options=options)
    return 


# finally, after contacting the payment provider...
def successful_payment_callback(update: Update, context: CallbackContext) -> None:
    """Confirms the successful payment."""
    # do something after successfully receiving payment?
    update.message.reply_text("Thank you for your payment!")


def setup_dispatcher_pay(dp: Dispatcher):
    # Диалог отправки сообщения
    conv_handler = ConversationHandler( 
        # точка входа в разговор 
        entry_points=[MessageHandler(Filters.text(START_MENU_FULL["payment"]) & FilterPrivateNoCommand, make_invoice)],      
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            "start_payment":[
                       MessageHandler(Filters.text(PAY_BACK["pay"]) & FilterPrivateNoCommand, make_invoice),
                       MessageHandler(Filters.text(PAY_BACK["back"]) & FilterPrivateNoCommand, back_to_start),
                       MessageHandler(Filters.text & FilterPrivateNoCommand, blank)
                      ],
            
            "proc_invoice":[PreCheckoutQueryHandler(precheckout_callback), 
                            ShippingQueryHandler(shipping_callback),
                            MessageHandler(Filters.successful_payment, successful_payment_callback)], 


        },
        # точка выхода из разговора
        fallbacks=[CommandHandler('cancel', pay_stop, Filters.chat_type.private)]
    )
    dp.add_handler(conv_handler)   
    pass