from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import (
    Dispatcher, CommandHandler,
    MessageHandler, CallbackQueryHandler,
    Filters,
    ConversationHandler,
)

from django.conf import settings
from .messages import *
from .answers import *
from tgbot.utils import extract_user_data_from_update
from tgbot.handlers.main.answers import get_start_menu, START_MENU_FULL
import tgbot.models as mymodels
from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.filters import FilterPrivateNoCommand
from tgbot.handlers.commands import command_start

# Возврат к главному меню
def stop_conversation(update: Update, context: CallbackContext):
    # Заканчиваем разговор.
    command_start(update, context)
    return ConversationHandler.END

# Временная заглушка
def blank(update: Update, context: CallbackContext):
    pass

def bad_callback_enter(update: Update, context: CallbackContext):
    update.message.reply_text(ASK_REENTER, reply_markup=make_keyboard(EMPTY,"usual",2))

# Начало разговора
def start_conversation(update: Update, context: CallbackContext):
   
    #update.message.reply_text(HELLO_MESS, reply_markup=make_keyboard(BACK,"usual",4))
    return "working"

# Обработчик поиска
def manage_find(update: Update, context: CallbackContext):
    if update.message.text == BACK["back"]:
        userdata = extract_user_data_from_update(update)
        user = mymodels.User.get_user_by_username_or_user_id(userdata["user_id"])   
        update.message.reply_text("Работа с поиском завершена", reply_markup=get_start_menu(user))
        return ConversationHandler.END
    else:
        users_set = mymodels.User.find_users_by_keywords(update.message.text)
        users_str = map(str, users_set)
        mess = "\n".join(users_str)
        update.message.reply_text(mess, reply_markup=make_keyboard(BACK,"usual",4))
    return "working"


def setup_dispatcher_conv(dp: Dispatcher):
    # Диалог отправки сообщения
    conv_handler = ConversationHandler( 
        # точка входа в разговор
        entry_points=[CallbackQueryHandler(start_conversation, pattern="^find_members$", run_async=True)],      
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            "working":[
                       MessageHandler(Filters.text & FilterPrivateNoCommand, manage_find, run_async=True),
                     
                       MessageHandler(Filters.text([BACK["back"]]) & FilterPrivateNoCommand, stop_conversation, run_async=True),
                       MessageHandler(Filters.text & FilterPrivateNoCommand, blank, run_async=True)
                      ],
        },
        # точка выхода из разговора
        fallbacks=[CommandHandler('cancel', stop_conversation, Filters.chat_type.private, run_async=True),
                   CommandHandler('start', stop_conversation, Filters.chat_type.private, run_async=True)]        
    )
    dp.add_handler(conv_handler)   
