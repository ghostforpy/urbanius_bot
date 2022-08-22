from csv import unregister_dialect
from telegram import (Update, ParseMode)
from telegram.ext import (
    Dispatcher, CommandHandler,
    MessageHandler, CallbackQueryHandler,
    Filters, CallbackContext, ConversationHandler
)
from django.conf import settings
from .messages import *
from .answers import *
from tgbot.models import tgGroups
from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.filters import FilterPrivateNoCommand, FilterGroupNoCommand
from tgbot.handlers.utils import send_message, send_mess_by_tmplt
from tgbot.handlers.main.answers import get_start_menu
from tgbot.handlers.main.messages import get_start_mess

# Возврат к главному меню
def stop_conversation(update: Update, context: CallbackContext):
    # Заканчиваем разговор.
    if update.message:
        user_id = update.message.from_user.id
    else:
        user_id = update.callback_query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    send_message(user_id=user_id, text=GROUP_FINISH, reply_markup=make_keyboard(EMPTY,"usual",1))
    send_message(user_id=user_id, text=get_start_mess(user), reply_markup=get_start_menu(user))
    return ConversationHandler.END

# Временная заглушка
def blank(update: Update, context: CallbackContext):
    update.message.reply_text(ASK_REENTER)

def bad_callback_enter(update: Update, context: CallbackContext):
    update.message.reply_text(ASK_REENTER)

# Начало разговора
def start_conversation(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    groups_menu = {}
    for group in user.usertggroups_set.all():
        groups_menu[group.group.pk] = group.group.name
    query.edit_message_text(ASK_SELECT_GROUP, reply_markup=make_keyboard(groups_menu,"inline",1,None,BACK))

    return "working"

def show_group(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    group = tgGroups.objects.get(pk = int(query.data))
    query.edit_message_text(f"<b>{group.name}</b>", reply_markup = make_keyboard(EMPTY,"inline",1))
    reply_markup=make_keyboard(EMPTY,"inline",1,None,CANCEL)
    add_text = f"\nСсылка для присоединения к группе {group.link}"
    send_mess_by_tmplt(user_id, group, reply_markup, add_text = add_text)

    return "manage_group"

def show_group_list(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    groups_menu = {}
    for group in user.usertggroups_set.all():
        groups_menu[group.group.pk] = group.group.name
    query.edit_message_reply_markup(make_keyboard(EMPTY,"inline",1))
    send_message(user_id, ASK_SELECT_GROUP, reply_markup=make_keyboard(groups_menu,"inline",1,None,BACK))

    return "working"


def setup_dispatcher_conv(dp: Dispatcher):
    # Диалог отправки сообщения
    conv_handler = ConversationHandler( 
        # точка входа в разговор      
        entry_points=[CallbackQueryHandler(start_conversation, pattern="^groups$"),
                      ],      
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            "working":[  
                       CallbackQueryHandler(stop_conversation, pattern="^back$"),            
                       CallbackQueryHandler(show_group),
                       MessageHandler(Filters.text & FilterPrivateNoCommand, blank)
                      ],
       "manage_group":[CallbackQueryHandler(show_group_list, pattern="^cancel$"),            
                       MessageHandler(Filters.text & FilterPrivateNoCommand, blank)
                      ],
        },
        # точка выхода из разговора
        fallbacks=[CommandHandler('cancel', stop_conversation, Filters.chat_type.private),
                   CommandHandler('start', stop_conversation, Filters.chat_type.private)]        
    )
    dp.add_handler(conv_handler)  

