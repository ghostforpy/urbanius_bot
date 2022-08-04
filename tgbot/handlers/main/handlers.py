
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import (
    Dispatcher, CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)
from tgbot.handlers.main.messages import *
from tgbot.handlers.main.answers import *
from tgbot.models import User, tgGroups
from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.filters import FilterPrivateNoCommand
from tgbot.handlers.commands import command_start
from tgbot.handlers.utils import send_message
from tgbot.utils import extract_user_data_from_update

def mess_stop(update: Update, context: CallbackContext):
    # Заканчиваем разговор.
    update.message.reply_text(SENDING_CANCELED)
    command_start(update, context)
    return ConversationHandler.END

def send_message_to_admins(update: Update, context: CallbackContext):
    update.message.reply_text(ASK_MESS, reply_markup=make_keyboard(CANCEL,"usual",1))
    return "sending"

def sending_mess(update: Update, context: CallbackContext):
    if update.message.text == CANCEL["cancel"]:
        mess_stop(update, context)
        return ConversationHandler.END
    else:
        group = tgGroups.get_group_by_name("Администраторы")
        if (group == None) or (group.chat_id == 0):
            update.message.reply_text(NO_ADMIN_GROUP)
        else:
            userdata = extract_user_data_from_update(update)
            text = " ".join(["Сообщение от пользователя", "@"+userdata["username"],
                            userdata["first_name"], userdata["last_name"],"\n", update.message.text])
            send_message(group.chat_id, text)
            update.message.reply_text(MESS_SENDED)
        command_start(update, context)
        return ConversationHandler.END


def setup_dispatcher_main(dp: Dispatcher):
    # Диалог отправки сообщения
    conv_handler_send_mess = ConversationHandler( # здесь строится логика разговора
        # точка входа в разговор
        entry_points=[MessageHandler(Filters.text(TO_ADMINS["to_admins"]) & FilterPrivateNoCommand, send_message_to_admins)],      
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            "sending":[MessageHandler(Filters.text & FilterPrivateNoCommand, sending_mess)],
        },
        # точка выхода из разговора
        fallbacks=[CommandHandler('cancel', mess_stop, Filters.chat_type.private)],
    )
    dp.add_handler(conv_handler_send_mess)   