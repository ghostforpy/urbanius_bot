import datetime
import os
from io import BytesIO
from telegram import ParseMode,  Update, LabeledPrice
from telegram.ext import (
    Dispatcher, CommandHandler,PreCheckoutQueryHandler,
    MessageHandler, CallbackQueryHandler,
    Filters, CallbackContext, ConversationHandler
)
from tgbot.my_telegram import ConversationHandler as ConversationHandlerMy
from django.conf import settings
from tgbot.models import User, Status
from .messages import *
from .answers import *
from .models import *
from dtb.constants import StatusCode, EventTypeCode
 

from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.filters import FilterPrivateNoCommand
from tgbot.handlers.utils import send_message, send_photo, send_video, fill_file_id, wrong_file_id
from tgbot.handlers.main.answers import get_start_menu
from tgbot.handlers.main.messages import get_start_mess

from payments.payments_proc import send_invois_to_tg, manage_precheckout_callback, finish_payment


def stop_conversation(update: Update, context: CallbackContext):
    """ 
       Возврат к главному меню    
    """
    # Заканчиваем разговор.
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    query.edit_message_text(get_start_mess(user), reply_markup=get_start_menu(user))
    return ConversationHandler.END

def blank(update: Update, context: CallbackContext):
    """
    Временная заглушка
    """
    pass

def bad_callback_enter(update: Update, context: CallbackContext):
    update.message.reply_text(ASK_REENTER)

def bad_input(update: Update, context: CallbackContext):
    update.message.reply_text(ASK_REENTER)


def start_conversation(update: Update, context: CallbackContext):
    """
    Начало разговора
    """
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=HELLO_MESS, reply_markup=make_keyboard(EVENTS_MENU,"inline",1,None,BACK))
    return "working"

def show_event_calendar(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    status_club_resident = Status.objects.get(code = StatusCode.CLUB_RESIDENT)
    event_type_club = EventTypes.objects.get(code = EventTypeCode.CLUB)
    
    evens_set = Events.objects.filter(date__gte = datetime.date.today(),
                                    date__lte = datetime.datetime.now() + datetime.timedelta(days=30))
    if (user.status != status_club_resident):
        # если пользователь не резидент, исключаем клубные мероприятия
        evens_set = evens_set.exclude(type = event_type_club)

    btn_events = {}
    for event in evens_set:
        
        btn_events[f"show_event-{event.pk}"] = str(event)
    if query.message.text:
        query.edit_message_text(text="Ближайшие мероприятия", reply_markup=make_keyboard(btn_events,"inline",1,None,BACK_EV_MNU))
    else:
        query.edit_message_reply_markup(make_keyboard(EMPTY,"inline",1))
        send_message(user_id=user_id, text="Ближайшие мероприятия", reply_markup=make_keyboard(btn_events,"inline",1,None,BACK_EV_MNU))
    return "select_event"

def show_event(update: Update, context: CallbackContext):
    """
    Показывает выбранное мероприятие
    """
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    query_data = query.data.split("-")
    event = Events.objects.get(pk = int(query_data[1]))
    text = event.get_description()
    text += event.get_user_info(user)
    request = event.get_user_request(user)
    if request:
        manage_event_mnu = {}
        if not request.payed:
            manage_event_mnu[f"pay_request_event-{event.pk}"] = "Оплатить заявку на мероприятие" 
            manage_event_mnu[f"del_request-{event.pk}"] = "Удалить заявку на мероприятие" 
        if request.confirmed:
            manage_event_mnu[f"qr_request-{event.pk}"] = "Показать код подтверждения"           
    else:
        manage_event_mnu = {f"reg_to_event-{event.pk}":"Зарегистрироваться на мероприятие"} 
    reply_markup = make_keyboard(manage_event_mnu,"inline",1,None,BACK_EV_CLNDR)

    if event.file:
        query.edit_message_reply_markup(make_keyboard(EMPTY,"inline",1))        
        file_ext = event.file.name.split(".")[-1]
        file_path = event.file.path
        if os.path.exists(file_path):
            if (not event.file_id) or wrong_file_id(event.file_id):
                fill_file_id(event, "file", text = "show_event")
            if file_ext in ["jpg","jpeg","png","gif","tif","tiff","bmp"]:
                send_photo(user_id, event.file_id, caption = text, 
                           reply_markup = reply_markup, parse_mode = ParseMode.HTML)
            elif file_ext in ["mp4","avi","mov","mpeg"]:
                send_video(user_id, event.file_id, caption = text, 
                                      reply_markup = reply_markup, parse_mode = ParseMode.HTML)
            else:
                query.edit_message_text(text = text, reply_markup = reply_markup, parse_mode = ParseMode.HTML)
        else:
            query.edit_message_text(text = text, reply_markup = reply_markup, parse_mode = ParseMode.HTML)
    else:
        query.edit_message_text(text = text, reply_markup = reply_markup, parse_mode = ParseMode.HTML)
    return "manage_event"

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
        request.save()
        group = tgGroups.get_group_by_name("Администраторы")
        if (group == None) or (group.chat_id == 0):
            pass
        else:
            text = f"Зарегистрирована заявка на участие в мероприятии {event} от пользователя {user}"
            reply_markup = make_keyboard(EMPTY,"inline",1)
            if request.payed:
                bn = {f"manage_event_reqw-{request.number}":"Показать заявку"}
                reply_markup = make_keyboard(bn,"inline",1)
            send_message(group.chat_id, text, reply_markup = reply_markup)
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


def show_qr_code(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    query_data = query.data.split("-")
    event = Events.objects.get(pk = int(query_data[1]))
    request = event.get_user_request(user)
    if request:
        img, text = request.get_qr_code()
        bio = BytesIO()
        bio.name = 'image.jpeg'
        img.save(bio, 'JPEG')
        bio.seek(0)
        query.edit_message_reply_markup(make_keyboard(EMPTY,"inline",1))
        reply_markup = make_keyboard(EMPTY,"inline",1,None,BACK_EV_CLNDR)
        send_photo(user_id, photo = bio, caption = text, parse_mode = ParseMode.HTML, reply_markup = reply_markup)        
    return "manage_event"


def show_requested_events(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    requests_set = EventRequests.objects.filter(event__date__gte = datetime.date.today() - datetime.timedelta(days=40),
                                    event__date__lte = datetime.date.today() + datetime.timedelta(days=1), user = user, confirmed = True)
    btn_events = {}
    for request in requests_set:        
        btn_events[request.event.pk] = str(request.event)
    if query.message.text:
        query.edit_message_text(text="Прошедшие мероприятия", reply_markup=make_keyboard(btn_events,"inline",1,None,BACK_EV_MNU))
    else:
        query.edit_message_reply_markup(make_keyboard(EMPTY,"inline",1))
        send_message(user_id=user_id, text="Прошедшие мероприятия", reply_markup=make_keyboard(btn_events,"inline",1,None,BACK_EV_MNU))
    return "select_req_event"

def show_reqw_event(update: Update, context: CallbackContext):
    """
    Показывает посещенное мероприятие
    """
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    event: Events
    event = Events.objects.get(pk = int(query.data))
    text = event.get_description()
    text += event.get_user_info(user)
    set_rating_btn = {
                      "rateevent-1-" + str(event.pk):"1",
                      "rateevent-2-" + str(event.pk):"2",
                      "rateevent-3-" + str(event.pk):"3",
                      "rateevent-4-" + str(event.pk):"4",
                      "rateevent-5-" + str(event.pk):"5",
                      }   
    reply_markup = make_keyboard(set_rating_btn,"inline",5,None,BACK_EV_CLNDR)

    if event.file:
        query.edit_message_reply_markup(make_keyboard(EMPTY,"inline",1))        
        file_ext = event.file.name.split(".")[-1]
        file_path = event.file.path
        if os.path.exists(file_path):
            if (not event.file_id) or wrong_file_id(event.file_id):
                fill_file_id(event, "file", text = "show_reqw_event")
            if file_ext in ["jpg","jpeg","png","gif","tif","tiff","bmp"]:
                send_photo(user_id, event.file_id, caption = text, 
                           reply_markup = reply_markup, parse_mode = ParseMode.HTML)
            elif file_ext in ["mp4","avi","mov","mpeg"]:
                send_video(user_id, event.file_id, caption = text, 
                                      reply_markup = reply_markup, parse_mode = ParseMode.HTML)
            else:
                query.edit_message_text(text = text, reply_markup = reply_markup, parse_mode = ParseMode.HTML)
        else:
            query.edit_message_text(text = text, reply_markup = reply_markup, parse_mode = ParseMode.HTML)
    else:
        query.edit_message_text(text = text, reply_markup = reply_markup, parse_mode = ParseMode.HTML)
    return "manage_req_event"

def set_rating_to_event(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    query_data = query.data.split("-")
    rating = query_data[1]
    event = Events.objects.get(pk = int(query_data[2]))
    request = event.get_user_request(user)
    context.user_data["request_to_event"] = request
    if request:
        request.rating = int(rating)
        request.save()

    #update_req_event_mess(query,event,user,request)
    query.edit_message_reply_markup(make_keyboard(EMPTY,"inline",1))
    text = "Введите комментарий к оценке"
    send_message(user_id=user_id, text=text)

    return "set_rating_comment"

def set_rating_comment (update: Update, context: CallbackContext):
    # Сохраняем оценку
    request = context.user_data["request_to_event"]      
    request.rating_comment = update.message.text
    request.save()
    user_id = update.message.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    requests_set = EventRequests.objects.filter(event__date__gte = datetime.date.today() - datetime.timedelta(days=40),
                                    event__date__lte = datetime.date.today() + datetime.timedelta(days=1), user = user, confirmed = True)
    btn_events = {}
    for request in requests_set:        
        btn_events[request.event.pk] = str(request.event)
    
    update.message.reply_text("Мероприятию установлена оценка")     
    update.message.reply_text("Прошедшие мероприятия", reply_markup=make_keyboard(btn_events,"inline",1,None,BACK_EV_MNU))
  
    return "select_req_event"

def set_rating_comment_reminder (update: Update, context: CallbackContext):
    """
     Вызывается когда запрос оценки происходит сообщением напоминанием
    """
    # Сохраняем оценку
    request = context.user_data["request_to_event"]      
    request.rating_comment = update.message.text
    request.save()
    update.message.reply_text("Мероприятию установлена оценка")     
  
    return ConversationHandler.END


def make_invoice(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_reply_markup(make_keyboard(EMPTY,"inline",1))
    user_id = query.from_user.id
    # разбираем пришедшие данные. пример 'pay_request_event-256'
    # pay_request - действие, event - имя обекта, 256 - индекс объекта в БД
    query_data = query.data.split("-")
    obj_pk = int(query_data[1])  # получили индекс объекта в БД
    user = User.get_user_by_username_or_user_id(user_id)   
    event = Events.objects.get(pk = int(obj_pk))
    payment_request = event.get_user_request(user)

    context.user_data["payment_started"] = True
    context.user_data["payment_request"] = payment_request
    send_invois_to_tg(user,event,payment_request)
    return "invois_sended"

# after (optional) shipping, it's the pre-checkout
def precheckout_callback(update: Update, context: CallbackContext) -> None:
    
    if manage_precheckout_callback(update,context):
        return "checkout"
    else:
        return "manage_event"


# finally, after contacting the payment provider...
def successful_payment_callback(update: Update, context: CallbackContext) -> None:
    """Confirms the successful payment."""
    # do something after successfully receiving payment?
    context.user_data["payment_started"] = False
    user_id = update.message.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)   
    payment_request = context.user_data["payment_request"]
    query = update.message.successful_payment
    finish_payment(query,user,payment_request)
    group = tgGroups.get_group_by_name("Администраторы")
    if (group == None) or (group.chat_id == 0):
        pass
    else:
        text = f"Оплачена заявка на участие в мероприятии {payment_request.event} от пользователя {user}"
        bn = {f"manage_event_reqw-{payment_request.mumber}":"Показать заявку"}
        reply_markup = make_keyboard(bn,"inline",1)
        send_message(group.chat_id, text, reply_markup = reply_markup)
        
    send_event_desc(payment_request.event, user)   
    return "manage_event"


#---------------------------------------------------------------      
#---------------------Подтверждение заявок----------------------
def stop_conversation_new_reqw(update: Update, context: CallbackContext):
    """ 
       Возврат к главному меню    
    """
    # Заканчиваем разговор.
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    query.delete_message()

def manage_event_reqw(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    if (not user) or (not user.is_admin):
        text ="Нет прав администратора"
        send_message(update.callback_query.message.chat_id, text)
        return
    query_data = query.data.split("-")
    new_reqw_id = int(query_data[1])
    new_reqw = EventRequests.objects.get(number = new_reqw_id)

    profile_text = new_reqw.description()
    manage_reqw_btn = {f"confirm_reqw-{new_reqw_id}":"Подтвердить заявку",
                       f"back_from_reqw_confirm-{new_reqw_id}":"Отмена подтверждения",
                      }
    reply_markup=make_keyboard(manage_reqw_btn,"inline",1)
    send_message(user_id = user_id, text=profile_text, reply_markup=reply_markup)

    bn = {f"manage_event_reqw-{new_reqw.number}":"Показать заявку"}
    reply_markup =  make_keyboard(bn,"inline",1)       
    text = query.message.text.split('\n')[0]
    text += f'\nЗаявка отправлена в чат {context.bot.name} '
    text += f'пользователю {query.from_user.full_name}'
    query.edit_message_text(text=text, reply_markup=reply_markup)

def confirm_event_reqwest(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    query_data = query.data.split("-")
    new_reqw_id = int(query_data[1])
    new_reqw = EventRequests.objects.get(number = new_reqw_id)
    new_reqw.confirmed = True
    new_reqw.save()
    query.delete_message()
    
    # query.edit_message_reply_markup(make_keyboard(EMPTY,"inline",1))
    # send_message(user_id=user_id, text="Заявка подтверждена", reply_markup=make_keyboard(EMPTY,"usual",1))
    # send_message(user_id=user_id, text=get_start_mess(user), reply_markup=get_start_menu(user))
  

def setup_dispatcher_conv(dp: Dispatcher):

    # Диалог
    conv_handler = ConversationHandlerMy( 
        # точка входа в разговор      
        entry_points=[CallbackQueryHandler(start_conversation, pattern="^events_mnu$"),
                      CallbackQueryHandler(set_rating_to_event, pattern="^remindrateevent-"),
                      ],      
        # этапы разговора, каждый со своим списком обработчиков сообщений
            states={
             "working":[CallbackQueryHandler(show_event_calendar, pattern="^calendar$"),
                        CallbackQueryHandler(show_requested_events, pattern="^requested$"),
                        CallbackQueryHandler(stop_conversation, pattern="^back$"),
                        MessageHandler(Filters.text & FilterPrivateNoCommand, bad_input),# Не делать асинхронным
                        ],
        "select_event":[CallbackQueryHandler(start_conversation, pattern="^back_ev$"),
                        CallbackQueryHandler(show_event, pattern="^show_event-"),
                        MessageHandler(Filters.text & FilterPrivateNoCommand, bad_input),# Не делать асинхронным
                        ],
        "manage_event":[CallbackQueryHandler(show_event_calendar, pattern="^back_clndr$"),
                        CallbackQueryHandler(create_request_to_event, pattern="^reg_to_event-"),
                        CallbackQueryHandler(delete_request, pattern="^del_request-"),
                        CallbackQueryHandler(make_invoice, pattern="^pay_request_event-"),
                        CallbackQueryHandler(show_qr_code, pattern="^qr_request-"),
                        CallbackQueryHandler(blank),
                        MessageHandler(Filters.text & FilterPrivateNoCommand, bad_input),# Не делать асинхронным
                        ],
    "select_req_event":[CallbackQueryHandler(start_conversation, pattern="^back_ev$"),
                        CallbackQueryHandler(show_reqw_event),
                        MessageHandler(Filters.text & FilterPrivateNoCommand, bad_input),# Не делать асинхронным
                        ],
    "manage_req_event":[CallbackQueryHandler(show_requested_events, pattern="^back_clndr$"),
                        CallbackQueryHandler(set_rating_to_event),
                        MessageHandler(Filters.text & FilterPrivateNoCommand, bad_input),# Не делать асинхронным
                        ],
  "set_rating_comment":[MessageHandler(Filters.text & FilterPrivateNoCommand, set_rating_comment)],

       "invois_sended":[PreCheckoutQueryHandler(precheckout_callback),                    
                        MessageHandler(Filters.text([CANCEL["cancel"]]) & FilterPrivateNoCommand, stop_conversation),# Не делать асинхронным
                        MessageHandler(Filters.text & FilterPrivateNoCommand, bad_input),# Не делать асинхронным
                         ],
            "checkout":[MessageHandler(Filters.successful_payment, successful_payment_callback)]  # Не делать асинхронным       
        },
            # точка выхода из разговора
             fallbacks=[CommandHandler('cancel', stop_conversation, Filters.chat_type.private),
                        CommandHandler('start', stop_conversation, Filters.chat_type.private)]        
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CallbackQueryHandler(manage_event_reqw, pattern="^manage_event_reqw-"))
    dp.add_handler(CallbackQueryHandler(stop_conversation_new_reqw, pattern="^back_from_reqw_confirm-"))
    dp.add_handler(CallbackQueryHandler(confirm_event_reqwest, pattern="^confirm_reqw-"))
        
    # conv_handler_confirm_reqw = ConversationHandlerMy( 
    #     # точка входа в разговор
    #     entry_points=[CallbackQueryHandler(manage_event_reqw, pattern="^manage_event_reqw-")],
    #     states={
    #         "wait_event_reqw_comand":[                                  
    #                    CallbackQueryHandler(stop_conversation_new_reqw, pattern="^back_from_reqw_confirm-"),
    #                    ,
    #                   ],
    #     },
    #     # точка выхода из разговора
    #     fallbacks=[CommandHandler('cancel', stop_conversation, Filters.chat_type.private, run_async=True),
    #                CommandHandler('start', stop_conversation, Filters.chat_type.private, run_async=True)]
    # )
    # dp.add_handler(conv_handler_confirm_reqw)





def send_event_desc(event: Events, user: User):
    text = event.get_description()
    text += event.get_user_info(user)
    request = event.get_user_request(user)
    if request:
        manage_event_mnu = {}       
        if not request.payed:
            manage_event_mnu[f"pay_request_event-{event.pk}"] = "Оплатить заявку на мероприятие" 
            manage_event_mnu[f"del_request-{event.pk}"] = "Удалить заявку на мероприятие"            
        if request.confirmed:
            manage_event_mnu[f"qr_request-{event.pk}"] = "Показать код подтверждения"  
    else:
        manage_event_mnu = {f"reg_to_event-{event.pk}":"Зарегистрироваться на мероприятие"} 
    reply_markup = make_keyboard(manage_event_mnu,"inline",1,None,BACK_EV_CLNDR)

    if event.file:      
        file_ext = event.file.name.split(".")[-1]
        file_path = event.file.path
        if os.path.exists(file_path):
            if not event.file_id:
                fill_file_id(event, "file", text = "send_event_desc")
            if file_ext in ["jpg","jpeg","png","gif","tif","tiff","bmp"]:
                send_photo(user.user_id, event.file_id, caption = text, 
                           reply_markup = reply_markup)
            elif file_ext in ["mp4","avi","mov","mpeg"]:
                send_video(user.user_id, event.file_id, caption = text, 
                                      reply_markup = reply_markup)
            else:
                send_message(user.user_id, text = text, reply_markup = reply_markup)
        else:
            send_message(user.user_id, text = text, reply_markup = reply_markup)
    else:
        send_message(user.user_id, text = text, reply_markup = reply_markup)
    return "manage_event"


def update_event_mess(query,event,user,request):
    text = event.get_description()
    text += event.get_user_info(user)
    manage_event_mnu = {}
    if request:    
        if not request.payed:
            manage_event_mnu[f"pay_request_event-{event.pk}"] = "Оплатить заявку на мероприятие"
            manage_event_mnu[f"del_request-{event.pk}"] = "Удалить заявку на мероприятие"             
        if request.confirmed:
            manage_event_mnu[f"qr_request-{event.pk}"] = "Показать код подтверждения"  
    else:
        manage_event_mnu = {f"reg_to_event-{event.pk}":"Зарегистрироваться на мероприятие"} 

    if query.message.text:
        query.edit_message_text(text=text, reply_markup=make_keyboard(manage_event_mnu,"inline",1,None,BACK_EV_CLNDR))
    else:
        query.edit_message_caption(caption=text, reply_markup=make_keyboard(manage_event_mnu,"inline",1,None,BACK_EV_CLNDR))

def update_req_event_mess(query,event,user,request):
    text = event.get_description()
    text += event.get_user_info(user)
    set_rating_btn = {
                      "1_" + str(event.pk):"1",
                      "2_" + str(event.pk):"2",
                      "3_" + str(event.pk):"3",
                      "4_" + str(event.pk):"4",
                      "5_" + str(event.pk):"5",
                      }  
    if query.message.text:
        query.edit_message_text(text=text, reply_markup=make_keyboard(set_rating_btn,"inline",5,None,BACK_EV_CLNDR))
    else:
        query.edit_message_caption(caption=text, reply_markup=make_keyboard(set_rating_btn,"inline",5,None,BACK_EV_CLNDR))



