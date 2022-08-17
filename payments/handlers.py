import os
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import (
    Dispatcher, CommandHandler,
    MessageHandler, CallbackQueryHandler,
    Filters,
    PreCheckoutQueryHandler,
    
)
from telegram import (LabeledPrice)
from tgbot.my_telegram import ConversationHandler

from django.conf import settings
from .messages import *
from .answers import *
from tgbot.handlers.filters import FilterPrivateNoCommand
from tgbot.handlers.commands import command_start
from tgbot.models import User
from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.main.answers import get_start_menu
from tgbot.utils import extract_user_data_from_update
from tgbot.handlers.utils import send_message

def bad_input(update: Update, context: CallbackContext):
    update.message.reply_text(ASK_REENTER, reply_markup=make_keyboard(EMPTY,"usual",2))

# Возврат к главному меню в исключительных ситуациях
def stop_conversation(update: Update, context: CallbackContext):
    # Заканчиваем разговор.
    update.message.reply_text(PAY_FINISH, reply_markup=make_keyboard(EMPTY,"usual",1))
    command_start(update, context)
    return ConversationHandler.END

def start_conversation(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    query.answer()
    query.edit_message_reply_markup(make_keyboard(EMPTY,"inline",1))
    #query.edit_message_text(text=REGISTRATION_START_MESSS)
    send_message(user_id=user.user_id, text=PAY_HELLO, reply_markup=make_keyboard(PAY_BACK,"usual",1))
    return "make_invois"
# Временная заглушка
def ask_reenter(update: Update, context: CallbackContext):
    update.message.reply_text(ASK_REENTER, reply_markup=make_keyboard(CANCEL,"usual",1))

def make_invoice(update: Update, context: CallbackContext):

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
    prices = [LabeledPrice("за 3 месяца", int(price * 100))]   
    update.message.reply_text(PAY_HELLO, reply_markup=make_keyboard(CANCEL,"usual",1))
    context.user_data["end_pay_dialog"] = ConversationHandler.END

    context.user_data["payment_started"] = True
    """Sends an invoice with shipping-payment."""
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
    return "invois_sended"

# after (optional) shipping, it's the pre-checkout
def precheckout_callback(update: Update, context: CallbackContext) -> None:
    """Answers the PreQecheckoutQuery"""
    user_id = update.pre_checkout_query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)  
    query = update.pre_checkout_query
    if context.user_data.get("payment_started"):
        # check the payload, is this from your bot?
        if query.invoice_payload != "URBANIUS_CLUB_description":
            # answer False pre_checkout_query
            query.answer(ok=False, error_message="Что-то пошло не так...")
            context.user_data["payment_started"] = False
            update.message.reply_text("Что-то пошло не так...", reply_markup=get_start_menu(user))
            return context.user_data["end_pay_dialog"]
        else:
            query.answer(ok=True)
            return "checkout"
    else:
        query.answer(ok=False, error_message="Срок платежа прошел. Начните новый платеж")
        update.message.reply_text("Срок платежа прошел. Начните новый платеж", reply_markup=get_start_menu(user))
        return context.user_data["end_pay_dialog"]


# finally, after contacting the payment provider...
def successful_payment_callback(update: Update, context: CallbackContext) -> None:
    """Confirms the successful payment."""
    # do something after successfully receiving payment?
    context.user_data["payment_started"] = False
    userdata = extract_user_data_from_update(update)
    user = User.get_user_by_username_or_user_id(userdata["user_id"])   
    update.message.reply_text("Спасибо за Ваш платеж! Подписка продлена по 31.12.2022", reply_markup=make_keyboard(EMPTY,"usual",1))
    command_start(update, context)
    return context.user_data["end_pay_dialog"]


def setup_dispatcher_conv(dp: Dispatcher):
    # Диалог отправки сообщения
    conv_handler = ConversationHandler( 
        # точка входа в разговор
        entry_points=[CallbackQueryHandler(start_conversation, pattern="^payment$")], # Не делать асинхронным    
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            "make_invois":[MessageHandler(Filters.text([PAY_BACK["pay"]]) & FilterPrivateNoCommand, make_invoice), # Не делать асинхронным
                           MessageHandler(Filters.text([PAY_BACK["back"]]) & FilterPrivateNoCommand, stop_conversation),], # Не делать асинхронным
            "invois_sended":[
                       PreCheckoutQueryHandler(precheckout_callback),                    
                       MessageHandler(Filters.text([CANCEL["cancel"]]) & FilterPrivateNoCommand, stop_conversation),# Не делать асинхронным
                       MessageHandler(Filters.text & FilterPrivateNoCommand, bad_input),# Не делать асинхронным
                      ],
            "checkout":[MessageHandler(Filters.successful_payment, successful_payment_callback)]  # Не делать асинхронным       
        },
        # точка выхода из разговора
        fallbacks=[CommandHandler('cancel', stop_conversation, Filters.chat_type.private),
                   CommandHandler('start', stop_conversation, Filters.chat_type.private),
                   MessageHandler(Filters.text([PAY_BACK["back"]]) & FilterPrivateNoCommand, stop_conversation),# Не делать асинхронным
                   MessageHandler(Filters.text([CANCEL["cancel"]]) & FilterPrivateNoCommand, stop_conversation),# Не делать асинхронным
                  ]
    )
    dp.add_handler(conv_handler)   

    