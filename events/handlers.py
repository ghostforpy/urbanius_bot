import datetime
from telegram import (
    InlineQueryResultArticle,  
    ParseMode, InputTextMessageContent, Update)
from telegram.ext import (
    Dispatcher, CommandHandler,
    MessageHandler, CallbackQueryHandler,
    Filters, ChosenInlineResultHandler,
    InlineQueryHandler, CallbackContext
)
from tgbot.my_telegram import ConversationHandler
from django.conf import settings
from .messages import *
from .answers import *
from .models import *

from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.filters import FilterPrivateNoCommand
from tgbot.handlers.utils import send_message, send_photo
from tgbot.handlers.main.answers import get_start_menu
from tgbot.handlers.main.messages import get_start_mess

# Возврат к главному меню
def stop_conversation(update: Update, context: CallbackContext):
    # Заканчиваем разговор.
    if update.message:
        user_id = update.message.from_user.id
    else:
        query = update.callback_query
        query.answer()
        user_id = query.from_user.id
        query.edit_message_reply_markup(make_keyboard(EMPTY,"inline",1))

    user = User.get_user_by_username_or_user_id(user_id)
    send_message(user_id=user_id, text=FINISH, reply_markup=make_keyboard(EMPTY,"usual",1))
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
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=HELLO_MESS, reply_markup=make_keyboard(EVENTS_MENU,"inline",1,None,BACK))

    return "working"

def show_event_calendar(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    evens_set = Events.objects.filter(date__gte = datetime.datetime.now(),
                                      date__lte = datetime.datetime.now() + datetime.timedelta(days=30))
    btn_events = {}
    for event in evens_set:
        str_date = event.date.strftime("%d.%m.%Y")
        if event.time:
            str_time = event.time.strftime("%H:%M")
        else:
            str_time = ""
        btn_events[event.pk] = f"{str_date}, {str_time} - {event.name}"

    query.edit_message_text(text="Ближайшие события", reply_markup=make_keyboard(btn_events,"inline",1,None,BACK_EV_MNU))
    return "select_event"

def show_event(update: Update, context: CallbackContext):
    pass
    

def setup_dispatcher_conv(dp: Dispatcher):
    # Диалог отправки сообщения
    conv_handler = ConversationHandler( 
        # точка входа в разговор      
        entry_points=[CallbackQueryHandler(start_conversation, pattern="^events$")],      
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            "working":[CallbackQueryHandler(show_event_calendar, pattern="^calendar$"),
                       CallbackQueryHandler(stop_conversation, pattern="^back$")
                      ],
            "select_event":[CallbackQueryHandler(start_conversation, pattern="^back_ev$"),
                            CallbackQueryHandler(show_event)
                           ],
        },
        # точка выхода из разговора
        fallbacks=[CommandHandler('cancel', stop_conversation, Filters.chat_type.private),
                   CommandHandler('start', stop_conversation, Filters.chat_type.private)]        
    )
    dp.add_handler(conv_handler)  
