from io import BytesIO
from django.conf import settings
from django.core.mail import send_mail
import datetime
from telegram import Update
from telegram.ext import (
    Dispatcher, MessageHandler, Filters,
    CallbackQueryHandler, CommandHandler,
    CallbackContext, ConversationHandler
)
from tgbot.handlers.filters import FilterPrivateNoCommand
from tgbot.models import User
from events.models import EventRequests
from .models import *
from .messages import *
from .answers import *
from tgbot.handlers.utils import send_message, send_photo
from tgbot.handlers.keyboard import make_keyboard
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

    send_message(user_id=user_id, text=REQW_FINISH, reply_markup=make_keyboard(EMPTY,"usual",1))
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
    query.edit_message_text(text=HELLO_MESS, reply_markup=make_keyboard(REQW_MNU,"inline",1,None,BACK))

    return "working"


def show_so_reqwests_list(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    so_reqw_set = user.souserrequests_set.filter(offer__valid_until__gte = datetime.date.today())
    btn_reqw = {}
    for so_reqw in so_reqw_set:
        btn_reqw[f"show_so_reqwest-{so_reqw.pk}"] = str(so_reqw)
    if len(btn_reqw) > 0:
        text = "Выберите вашу заявку для просмотра подробностей"
    else:
        text = "У Вас отсутствуют заявки"    
    reply_markup = make_keyboard(btn_reqw,"inline",1,None,BACK)
    query.edit_message_text(text=text, reply_markup = reply_markup)   
    return "show_so_reqwests_list"

def show_so_reqwest(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    query_data = query.data.split("-")
    request = SOUserRequests.objects.get(pk = int(query_data[-1]))
    text = f"Вы получили скидку {request.discount}% у партнера '{request.offer.partner.full_name}' " \
           f"на предложение '{request.offer}'. Для получения скидки сообщите партнеру ее номер '{request.pk}'"
    reply_markup = make_keyboard(REQW_LST,"inline",1,None,BACK)
    query.edit_message_text(text = text, reply_markup = reply_markup)
    return "show_so_reqwest"


def show_event_reqwests_list(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    ev_reqw_set = user.eventrequests_set.reverse()[:10]
    btn_reqw = {}
    for ev_reqw in ev_reqw_set:
        btn_reqw[f"show_ev_reqwest-{ev_reqw.number}"] = str(ev_reqw)
    if len(btn_reqw) > 0:
        text = "Выберите вашу заявку для просмотра подробностей"
    else:
        text = "У Вас отсутствуют заявки"    
    reply_markup = make_keyboard(btn_reqw,"inline",1,None,BACK)
    query.edit_message_text(text=text, reply_markup = reply_markup)   
    return "show_ev_reqwests_list"

def show_ev_reqwest(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    query_data = query.data.split("-")
    request = EventRequests.objects.get(number = int(query_data[-1]))
    text = request.description()
    btns = {}
    if request.confirmed:
        btns[f"show_qr-{request.number}"] = "Показать код подтверждения"
    btns["reqw_lst"] = "Вернуться к списку заявок" #
    reply_markup = make_keyboard(btns,"inline",1,None,BACK)
    query.edit_message_text(text = text, reply_markup = reply_markup)
    return "show_ev_reqwest"


def show_qr_code(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    query_data = query.data.split("-")
    request = EventRequests.objects.get(number = int(query_data[-1]))
    if request:
        img, text = request.get_qr_code()
        bio = BytesIO()
        bio.name = 'image.jpeg'
        img.save(bio, 'JPEG')
        bio.seek(0)
        query.edit_message_reply_markup(make_keyboard(EMPTY,"inline",1))
        reply_markup = make_keyboard(REQW_LST,"inline",1,None, BACK)
        send_photo(user_id, photo = bio)  
        send_message(user_id, text = text, reply_markup = reply_markup)        
    return "manage_qr"

def setup_dispatcher_conv(dp: Dispatcher):

    conv_handler = ConversationHandler( 
        # точка входа в разговор      
        entry_points=[CallbackQueryHandler(start_conversation, pattern="^my_requests$")],      
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            "working":[             
                       CallbackQueryHandler(stop_conversation, pattern="^back$"),
                       CallbackQueryHandler(show_so_reqwests_list, pattern="^so_reqwests$"),
                       CallbackQueryHandler(show_event_reqwests_list, pattern="^event_reqwests$"),
                       MessageHandler(Filters.text & FilterPrivateNoCommand, blank)
                      ],
            "show_so_reqwests_list":[
                          CallbackQueryHandler(stop_conversation, pattern="^back$"),
                          CallbackQueryHandler(show_so_reqwest, pattern="^show_so_reqwest-"),
                          MessageHandler(Filters.text([BACK["back"]]) & FilterPrivateNoCommand, stop_conversation),
                         ],
            "show_so_reqwest":[
                          CallbackQueryHandler(stop_conversation, pattern="^back$"),
                          CallbackQueryHandler(show_so_reqwests_list, pattern="^reqw_lst$"),
                          MessageHandler(Filters.text([BACK["back"]]) & FilterPrivateNoCommand, stop_conversation),
                         ],
            "show_ev_reqwests_list":[
                          CallbackQueryHandler(stop_conversation, pattern="^back$"),
                          CallbackQueryHandler(show_ev_reqwest, pattern="^show_ev_reqwest-"),
                          MessageHandler(Filters.text([BACK["back"]]) & FilterPrivateNoCommand, stop_conversation),
                         ],
            "show_ev_reqwest":[
                          CallbackQueryHandler(stop_conversation, pattern="^back$"),
                          CallbackQueryHandler(show_event_reqwests_list, pattern="^reqw_lst$"),
                          CallbackQueryHandler(show_qr_code, pattern="^show_qr-"),
                          MessageHandler(Filters.text([BACK["back"]]) & FilterPrivateNoCommand, stop_conversation),
                         ],
            "manage_qr":[
                          CallbackQueryHandler(stop_conversation, pattern="^back$"),
                          CallbackQueryHandler(show_event_reqwests_list, pattern="^reqw_lst$"),
                          MessageHandler(Filters.text([BACK["back"]]) & FilterPrivateNoCommand, stop_conversation),
                         ],
        },
        # точка выхода из разговора
        fallbacks=[CommandHandler('cancel', stop_conversation, Filters.chat_type.private),
                   CommandHandler('start', stop_conversation, Filters.chat_type.private)]        
    )
    dp.add_handler(conv_handler) 