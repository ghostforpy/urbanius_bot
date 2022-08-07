import os
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import (
    Dispatcher, CommandHandler,
    MessageHandler,
    Filters,
    PreCheckoutQueryHandler,
)
from telegram import (LabeledPrice)
from telegram import __version__ as TG_VER

from django.conf import settings
from tgbot.handlers.payments.messages import *
from tgbot.handlers.payments.answers import *

from tgbot.handlers.filters import FilterPrivateNoCommand
from tgbot.handlers.commands import command_start
import tgbot.models as mymodels
from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.main.answers import get_start_menu, START_MENU_FULL
from tgbot.utils import extract_user_data_from_update

# Возврат к главному меню в исключительных ситуациях
def pay_stop(update: Update, context: CallbackContext):
    # Заканчиваем разговор.
    command_start(update, context)

# Временная заглушка
def ask_reenter(update: Update, context: CallbackContext):
    update.message.reply_text(ASK_REENTER, reply_markup=make_keyboard(CANCEL,"usual",1))

# Возврат к главному меню по кнопке
def back_to_start(update: Update, context: CallbackContext):
    # Заканчиваем разговор.
    context.user_data["payment_started"] = False
    command_start(update, context)

def make_invoice(update: Update, context: CallbackContext):
    """Sends an invoice with shipping-payment."""
    context.user_data["payment_started"] = True
    chat_id = update.message.chat_id
    title = "Платеж за подписку"
    description = "Платеж за подписку за дополнительные услуги URBANIUS CLUB"
    # select a payload just for you to recognize its the donation from your bot
    payload = "URBANIUS_CLUB_description"
    # In order to get a provider_token see https://core.telegram.org/bots/payments#getting-a-token
    currency = "RUB"
    # price in rubls
    price = 125.37

    # price * 100 so as to include 2 decimal points
    # check https://core.telegram.org/bots/payments#supported-currencies for more details
    prices = [LabeledPrice("за 3 месяца", int(price * 100 * 3))]
    
    update.message.reply_text(PAY_HELLO, reply_markup=make_keyboard(CANCEL,"usual",1))
    # optionally pass need_name=True, need_phone_number=True,
    # need_email=True, need_shipping_address=True, is_flexible=True
    context.bot.send_invoice(
        chat_id,
        title,
        description,
        payload,
        settings.PAYMENT_PROVIDER_TOKEN,
        currency,
        prices,
        need_name=True,
        need_phone_number=True,
        need_email=True,
    )

# after (optional) shipping, it's the pre-checkout
def precheckout_callback(update: Update, context: CallbackContext) -> None:
    """Answers the PreQecheckoutQuery"""
    query = update.pre_checkout_query
    if context.user_data.get("payment_started"):
        # check the payload, is this from your bot?
        if query.invoice_payload != "URBANIUS_CLUB_description":
            # answer False pre_checkout_query
            query.answer(ok=False, error_message="Что-то пошло не так...")
        else:
            query.answer(ok=True)
    else:
        query.answer(ok=False, error_message="Срок платежа прошел. Начните новый платеж")

# finally, after contacting the payment provider...
def successful_payment_callback(update: Update, context: CallbackContext) -> None:
    """Confirms the successful payment."""
    # do something after successfully receiving payment?
    context.user_data["payment_started"] = False
    userdata = extract_user_data_from_update(update)
    user = mymodels.User.get_user_by_username_or_user_id(userdata["user_id"])   
    update.message.reply_text("Спасибо за Ваш платеж! Подписка продлена по 31.12.2022", reply_markup=get_start_menu(user))


def setup_dispatcher_pay(dp: Dispatcher):
    # Диалог оплаты

    # точка входа в разговор    # точка входа в разговор 
    dp.add_handler(MessageHandler(Filters.text(START_MENU_FULL["payment"]) & FilterPrivateNoCommand, make_invoice))
    # этапы разговора, каждый со своим списком обработчиков сообщений
    dp.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    dp.add_handler(MessageHandler(Filters.text(CANCEL["cancel"]) & FilterPrivateNoCommand, pay_stop))
    dp.add_handler(MessageHandler(Filters.successful_payment, successful_payment_callback))
    # точка выхода из разговора
    dp.add_handler(CommandHandler('cancel', pay_stop, Filters.chat_type.private))
    dp.add_handler(MessageHandler(Filters.text & FilterPrivateNoCommand, ask_reenter))


    