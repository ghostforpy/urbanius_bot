import datetime
from operator import truediv
import os
from telegram import ParseMode,  Update
from telegram.ext import (
    Dispatcher, CommandHandler,
    MessageHandler, CallbackQueryHandler,
    Filters, CallbackContext, ConversationHandler
)
from django.conf import settings
from tgbot.models import User, Status
from .messages import *
from .answers import *
from .models import *

from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.filters import FilterPrivateNoCommand
from tgbot.handlers.utils import send_message, send_photo, send_video
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
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    status_club_resident = Status.objects.get(code = "club_resident")
    event_type_club = EventTypes.objects.get(code = "club")
    
    evens_set = Events.objects.filter(date__gte = datetime.datetime.now(),
                                    date__lte = datetime.datetime.now() + datetime.timedelta(days=30))
    if (user.status != status_club_resident):
        # если пользователь не резидент, исключаем клубные события
        evens_set = evens_set.exclude(type = event_type_club)

    btn_events = {}
    for event in evens_set:
        
        btn_events[event.pk] = str(event)
    if query.message.text:
        query.edit_message_text(text="Ближайшие события", reply_markup=make_keyboard(btn_events,"inline",1,None,BACK_EV_MNU))
    else:
        query.edit_message_reply_markup(make_keyboard(EMPTY,"inline",1))
        send_message(user_id=user_id, text="Ближайшие события", reply_markup=make_keyboard(btn_events,"inline",1,None,BACK_EV_MNU))
    return "select_event"

def show_event(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    event: Events
    event = Events.objects.get(pk = int(query.data))
    text = event.get_description()
    text += event.get_user_info(user)
    request = event.get_user_request(user)
    if request:
        manage_event_mnu = {}
        manage_event_mnu[f"del_request-{event.pk}"] = "Удалить заявку на событие"
        if not request.payed:
            manage_event_mnu[f"pay_request-{event.pk}"] = "Оплатить заявку на событие"             
    else:
        manage_event_mnu = {f"reg_to_event-{event.pk}":"Зарегистрироваться на событие"} 
    reply_markup = make_keyboard(manage_event_mnu,"inline",1,None,BACK_EV_CLNDR)

    if event.file:
        query.edit_message_reply_markup(make_keyboard(EMPTY,"inline",1))        
        file_ext = event.file.name.split(".")[-1]
        file_path = event.file.path
        if os.path.exists(file_path):
            if file_ext in ["jpg","jpeg","png","gif","tif","tiff","bmp"]:
                send_photo(user_id, open(file_path, 'rb'), caption = text, reply_markup = reply_markup, parse_mode = ParseMode.HTML)
            elif file_ext in ["mp4","avi","mov","mpeg"]:
                send_video(user_id, open(file_path, 'rb'), caption = text, reply_markup = reply_markup, parse_mode = ParseMode.HTML)
            else:
                query.edit_message_text(text = text, reply_markup = reply_markup, parse_mode = ParseMode.HTML)
        else:
            query.edit_message_text(text = text, reply_markup = reply_markup, parse_mode = ParseMode.HTML)
    else:
        query.edit_message_text(text = text, reply_markup = reply_markup, parse_mode = ParseMode.HTML)
    return "manage_event"

def update_event_mess(query,event,user,request):
    text = event.get_description()
    text += event.get_user_info(user)
    manage_event_mnu = {}
    manage_event_mnu[f"del_request-{event.pk}"] = "Удалить заявку на событие"

    if request:
        manage_event_mnu = {}
        manage_event_mnu[f"del_request-{event.pk}"] = "Удалить заявку на событие"
        if not request.payed:
            manage_event_mnu[f"pay_request-{event.pk}"] = "Оплатить заявку на событие"             
    else:
        manage_event_mnu = {f"reg_to_event-{event.pk}":"Зарегистрироваться на событие"} 

    if query.message.text:
        query.edit_message_text(text=text, reply_markup=make_keyboard(manage_event_mnu,"inline",1,None,BACK_EV_CLNDR))
    else:
        query.edit_message_caption(caption=text, reply_markup=make_keyboard(manage_event_mnu,"inline",1,None,BACK_EV_CLNDR))


def create_request_to_event(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    query_data = query.data.split("-")
    event = Events.objects.get(pk = int(query_data[1]))
    request = event.get_user_request(user)
    if request:
        text = f"Уже существует заявка № {request}"
        send_message(user_id=user_id, text=text)
    else:
        request = EventRequests()
        request.event = event
        request.user = user
        request.for_status = user.status
        request.price = event.get_price(user)
        if request.price == 0:
            request.payed = True
        if event.type == EventTypes.objects.get(code = "open"):
            request.confirmed = True
        request.save()
        # text = f"Зарегистрирована заявка № {request}"
        # send_message(user_id=user_id, text=text)
    update_event_mess(query,event,user,request)
    return "manage_event"

def delete_request(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    query_data = query.data.split("-")
    event = Events.objects.get(pk = int(query_data[1]))
    request = event.get_user_request(user)
    if request:
        # text = f"Удалена заявка № {request}"
        request.delete()
        request = None
        # send_message(user_id=user_id, text=text)
    update_event_mess(query,event,user,request)
    return "manage_event"

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
            "manage_event":[CallbackQueryHandler(show_event_calendar, pattern="^back_clndr$"),
                            CallbackQueryHandler(create_request_to_event, pattern="^reg_to_event-"),
                            CallbackQueryHandler(delete_request, pattern="^del_request-"),
                            CallbackQueryHandler(blank, pattern="^pay_request-"),
                            CallbackQueryHandler(blank)
                           ],
        },
        # точка выхода из разговора
        fallbacks=[CommandHandler('cancel', stop_conversation, Filters.chat_type.private),
                   CommandHandler('start', stop_conversation, Filters.chat_type.private)]        
    )
    dp.add_handler(conv_handler)  
