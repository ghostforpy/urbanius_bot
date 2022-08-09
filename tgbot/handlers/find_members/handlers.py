from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, Update
from telegram.ext import (
    Dispatcher, CommandHandler,
    MessageHandler, CallbackQueryHandler,
    Filters,
    InlineQueryHandler, CallbackContext
)
from tgbot.my_telegram import ConversationHandler
from django.conf import settings
from .messages import *
from .answers import *
import tgbot.models as mymodels
from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.filters import FilterPrivateNoCommand
from tgbot.handlers.utils import send_message
from tgbot.handlers.main.answers import get_start_menu
from tgbot.handlers.main.messages import get_start_mess
from tgbot.handlers.registration.messages import REGISTRATION_START_MESSS

# Возврат к главному меню
def stop_conversation(update: Update, context: CallbackContext):
    # Заканчиваем разговор.
    if update.message:
        user_id = update.message.from_user.id
    else:
        user_id = update.callback_query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    send_message(user_id=user_id, text=FIND_FINISH, reply_markup=make_keyboard(EMPTY,"usual",1))
    send_message(user_id=user_id, text=get_start_mess(user), reply_markup=get_start_menu(user))

    return ConversationHandler.END

# Временная заглушка
def blank(update: Update, context: CallbackContext):
    pass

def bad_callback_enter(update: Update, context: CallbackContext):
    update.message.reply_text(ASK_REENTER, reply_markup=make_keyboard(EMPTY,"usual",2))

# Начало разговора
def start_conversation(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    query.edit_message_text(text=REGISTRATION_START_MESSS)
    send_message(user_id=user_id, text=HELLO_MESS, reply_markup=make_keyboard(BACK,"usual",1))
    send_message(user_id=user_id,text=HELLO_MESS_2, reply_markup=make_keyboard(FIND,"inline",1))

    return "working"

# Обработчик поиска
def manage_find(update: Update, context: CallbackContext):
    query = update.inline_query.query.strip()

    if len(query) < 3:
        return
    users_set = mymodels.User.find_users_by_keywords(query)
    results = []
    for user in users_set:
        user_res_str = InlineQueryResultArticle(
            id=str(user.user_id),
            title=str(user),
            input_message_content=InputTextMessageContent(user.short_profile()),
            description = user.about,
            reply_markup=make_keyboard(BACK,"inline",1),
        )
        results.append(user_res_str)
    update.inline_query.answer(results)
    return "working"

def setup_dispatcher_conv(dp: Dispatcher):
    # Диалог отправки сообщения
    conv_handler = ConversationHandler( 
        # точка входа в разговор
        entry_points=[CallbackQueryHandler(start_conversation, pattern="^find_members$", run_async=True)],      
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            "working":[
                       InlineQueryHandler(manage_find),                
                       MessageHandler(Filters.text([BACK["back"]]) & FilterPrivateNoCommand, stop_conversation, run_async=True),
                       CallbackQueryHandler(stop_conversation, pattern="^back$", run_async=True),
                       MessageHandler(Filters.text & FilterPrivateNoCommand, blank, run_async=True)
                      ],
        },
        # точка выхода из разговора
        fallbacks=[CommandHandler('cancel', stop_conversation, Filters.chat_type.private, run_async=True),
                   CommandHandler('start', stop_conversation, Filters.chat_type.private, run_async=True)]        
    )
    dp.add_handler(conv_handler)   
