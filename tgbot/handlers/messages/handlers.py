from telegram import (
    InlineQueryResultArticle, InlineQueryResultPhoto, InlineQueryResultCachedPhoto,
    ParseMode, InputTextMessageContent, Update, ParseMode)
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
from tgbot.models import tgGroups
from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.filters import FilterPrivateNoCommand
from tgbot.handlers.utils import send_message
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
    send_message(user_id=user_id, text=CONV_FINISH, reply_markup=make_keyboard(EMPTY,"usual",1))
    send_message(user_id=user_id, text=get_start_mess(user), reply_markup=get_start_menu(user))
    return ConversationHandler.END

# Временная заглушка
def blank(update: Update, context: CallbackContext):
    pass

def bad_callback_enter(update: Update, context: CallbackContext):
    update.message.reply_text(ASK_REENTER)
    return "working"

# Начало разговора
def start_conversation(update: Update, context: CallbackContext):
    user = User.get_user_by_username_or_user_id(update.callback_query.from_user.id)
    reply_markup = make_keyboard(MESS_MENU,"usual",1,None,BACK)
    send_message(user_id = user.user_id, text = HELLO_MESS, reply_markup = reply_markup)

    return "working"
# Обработка отправки сообщений админам
def ask_admin_mess(update: Update, context: CallbackContext):
    user = User.get_user_by_username_or_user_id(update.message.from_user.id)
    send_message(user_id=user.user_id, text=ASK_MESS, reply_markup=make_keyboard(CANCEL,"usual",1))
    return "sending_to_admins"

def sending_mess_to_admins(update: Update, context: CallbackContext):
    user = User.get_user_by_username_or_user_id(update.message.from_user.id)
    reply_markup = make_keyboard(MESS_MENU,"usual",1,None,BACK)
    if update.message.text != CANCEL["cancel"]:
        group = tgGroups.get_group_by_name("Администраторы")
        if (group == None) or (group.chat_id == 0):
            update.message.reply_text(NO_ADMIN_GROUP, reply_markup = reply_markup)
        else:
            text = f"Сообщение от пользователя {str(user)}\n{update.message.text}"
            send_message(group.chat_id, text)
            update.message.reply_text(MESS_SENDED, reply_markup = reply_markup)
    else:
        update.message.reply_text(SENDING_CANCELED, reply_markup = reply_markup)
    return "working"
# Обработка отправки сообщений в группу
def ask_anon_mess_group(update: Update, context: CallbackContext):
    user = User.get_user_by_username_or_user_id(update.message.from_user.id)
    groups_menu = {}
    for group in user.usertggroups_set.exclude(group__chat_id = None):
        groups_menu[group.group.chat_id] = group.group.name
    update.message.reply_text(SENDING_ANON_MESS, reply_markup=make_keyboard(EMPTY,"usual",1))
    update.message.reply_text(ASK_ANON_MESS_GROUP, reply_markup=make_keyboard(groups_menu,"inline",1,None,CANCEL))
    return "select_group"

def ask_anon_mess(update: Update, context: CallbackContext):
    user = User.get_user_by_username_or_user_id(update.callback_query.from_user.id)
    query = update.callback_query
    group_id = query.data
    context.user_data["group_id"] = group_id
    group = tgGroups.objects.get(chat_id = group_id)
    query.edit_message_text(text=f"Выбрана группа {group.name}")
    text = "Введите текст сообщения"
    reply_markup=make_keyboard(CANCEL,"usual",1) 
    send_message(user_id=user.user_id, text=text, reply_markup=reply_markup) 
    return "input_message" 

def sending_mess_in_group(update: Update, context: CallbackContext):
    user = User.get_user_by_username_or_user_id(update.message.from_user.id)
    reply_markup = make_keyboard(MESS_MENU,"usual",1,None,BACK)
    if update.message.text != CANCEL["cancel"]:
        group_id = context.user_data["group_id"]
        group_menu = {f"anonmess_{user.user_id}":"Ответить"}
        reply_markup_group = make_keyboard(group_menu,"inlain",1)
        text = f"Анонимное сообщение от пользователя:\n{update.message.text}"
        send_message(group_id, text = text, reply_markup = reply_markup_group)
        update.message.reply_text(MESS_SENDED, reply_markup = reply_markup)
    else:
        update.message.reply_text(SENDING_CANCELED, reply_markup = reply_markup)
    return "working" 

def setup_dispatcher_conv(dp: Dispatcher):
    # Диалог отправки сообщения
    conv_handler = ConversationHandler( 
        # точка входа в разговор      
        entry_points=[CallbackQueryHandler(start_conversation, pattern="^messages$")],      
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            "working":[              
                       MessageHandler(Filters.text([MESS_MENU["to_admins"]]) & FilterPrivateNoCommand, ask_admin_mess),
                       MessageHandler(Filters.text([MESS_MENU["anon_mess"]]) & FilterPrivateNoCommand, ask_anon_mess_group),
                       MessageHandler(Filters.text(BACK["back"]) & FilterPrivateNoCommand, stop_conversation),
                       MessageHandler(Filters.text & FilterPrivateNoCommand, blank)
                      ],
            "sending_to_admins":[
                        MessageHandler(Filters.text & FilterPrivateNoCommand, sending_mess_to_admins),
                         ],
            "select_group":[
                           CallbackQueryHandler(ask_anon_mess),
                           MessageHandler(Filters.text & FilterPrivateNoCommand, bad_callback_enter)
                         ],
            "input_message":[
                        MessageHandler(Filters.text & FilterPrivateNoCommand, sending_mess_in_group),
                         ],
        },
        # точка выхода из разговора
        fallbacks=[CommandHandler('cancel', stop_conversation, Filters.chat_type.private),
                   CommandHandler('start', stop_conversation, Filters.chat_type.private)]        
    )
    dp.add_handler(conv_handler)   
