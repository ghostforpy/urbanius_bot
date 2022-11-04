
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import (
    Dispatcher, CommandHandler,
    MessageHandler, CallbackQueryHandler,
    Filters,
    ConversationHandler,
)
from .messages import *
from .answers import *
from tgbot.models import User, tgGroups
from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.filters import FilterPrivateNoCommand
from tgbot.handlers.commands import command_start
from tgbot.handlers.utils import send_message
from tgbot.utils import extract_user_data_from_update
import tgbot.models as mymodels
# Обработка отправки сообщений
def stop_conversation(update: Update, context: CallbackContext):
    # Заканчиваем разговор.
    update.message.reply_text(SENDING_CANCELED, reply_markup=make_keyboard(EMPTY,"usual",1))
    command_start(update, context)
    return ConversationHandler.END


# Обработка статуса Random coffee
def stop_conversation_coffe(update: Update, context: CallbackContext):
    # Заканчиваем разговор.
    userdata = extract_user_data_from_update(update)
    user = mymodels.User.get_user_by_username_or_user_id(userdata["user_id"])    
    if user.random_coffe_on:
        text=ASK_OFF_COFFE
    else:
        text=ASK_ON_COFFE
    update.message.reply_text(text=text, reply_markup=make_keyboard(EMPTY,"usual",1))
    command_start(update, context)
    return ConversationHandler.END

def start_conversation_coffe(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    user = mymodels.User.get_user_by_username_or_user_id(user_id)
    query.answer()
    query.edit_message_text(text=COFFE_WELCOME)
    if user.random_coffe_on:
        text=ASK_OFF_COFFE
    else:
        text=ASK_ON_COFFE
    send_message(user_id=user.user_id, text=text, reply_markup=make_keyboard(ON_OFF_CANCEL,"usual",2))
    return "changing_coffe"

def changing_coffe(update: Update, context: CallbackContext):
    userdata = extract_user_data_from_update(update)
    user = mymodels.User.get_user_by_username_or_user_id(userdata["user_id"])
    if update.message.text == ON_OFF_CANCEL["cancel"]:
        stop_conversation_coffe(update, context)
        return ConversationHandler.END
    elif update.message.text == ON_OFF_CANCEL["off"]:
        user.random_coffe_on = False
        user.save()
        stop_conversation_coffe(update, context)
        return ConversationHandler.END
    elif update.message.text == ON_OFF_CANCEL["on"]:
        user.random_coffe_on = True
        user.save()
        stop_conversation_coffe(update, context)
        return ConversationHandler.END
    else:
        update.message.reply_text(ASK_REENTER, reply_markup=make_keyboard(ON_OFF_CANCEL,"usual",2))

def start_conversation_affiliate(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    user = mymodels.User.get_user_by_username_or_user_id(user_id)
    query.answer()
    text = AFFILATE_MESS
    send_message(user_id=user.user_id, text=text)
    text = f"{context.bot.link}/?start={user_id}"
    send_message(user_id=user.user_id, text=text)

    ConversationHandler.END

def setup_dispatcher_conv(dp: Dispatcher):
    # Диалог отправки сообщения
    conv_handler_send_mess = ConversationHandler( # здесь строится логика разговора
        # точка входа в разговор
        entry_points=[CallbackQueryHandler(start_conversation_coffe, pattern="^random_coffee$"),
                     # CallbackQueryHandler(start_conversation_affiliate, pattern="^affiliate$")
                      ],      
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            #"sending":[MessageHandler(Filters.text & FilterPrivateNoCommand, sending_mess)],
            "changing_coffe":[MessageHandler(Filters.text & FilterPrivateNoCommand, changing_coffe)],
        },
        # точка выхода из разговора
        fallbacks=[CommandHandler('cancel', stop_conversation, Filters.chat_type.private),
                   CommandHandler('start', stop_conversation, Filters.chat_type.private)],
    )
    dp.add_handler(conv_handler_send_mess)   