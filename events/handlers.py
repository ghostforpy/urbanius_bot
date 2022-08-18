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
from payments.models import Payments
from .messages import *
from .answers import *
from .models import *

from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.filters import FilterPrivateNoCommand
from tgbot.handlers.utils import send_message, send_photo, send_video, fill_file_id, wrong_file_id
from tgbot.handlers.main.answers import get_start_menu
from tgbot.handlers.main.messages import get_start_mess
from tgbot.utils import extract_user_data_from_update


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

def bad_input(update: Update, context: CallbackContext):
    update.message.reply_text(ASK_REENTER)


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
        # если пользователь не резидент, исключаем клубные мероприятия
        evens_set = evens_set.exclude(type = event_type_club)

    btn_events = {}
    for event in evens_set:
        
        btn_events[event.pk] = str(event)
    if query.message.text:
        query.edit_message_text(text="Ближайшие мероприятия", reply_markup=make_keyboard(btn_events,"inline",1,None,BACK_EV_MNU))
    else:
        query.edit_message_reply_markup(make_keyboard(EMPTY,"inline",1))
        send_message(user_id=user_id, text="Ближайшие мероприятия", reply_markup=make_keyboard(btn_events,"inline",1,None,BACK_EV_MNU))
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
                fill_file_id(event, "file")
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
    pay_request = event.get_user_request(user)
    str_request = str(pay_request)
    title = event.name
    description = str_request
    payload = "URBANIUS_CLUB"
    currency = "RUB"
    price = pay_request.price
    # price * 100 so as to include 2 decimal points
    prices = [LabeledPrice(str_request, int(price * 100))]

    context.user_data["payment_started"] = True
    context.user_data["payment_request"] = pay_request
    """Sends an invoice with shipping-payment."""
    # optionally pass need_name=True, need_phone_number=True,
    # need_email=True, need_shipping_address=True, is_flexible=True
    context.bot.send_invoice(
        user_id,
        title,
        description,
        payload,
        settings.PAYMENT_PROVIDER_TOKEN,
        currency,
        prices,
        need_name=True,
        need_phone_number=True,
        need_email=True,
    )
    return "invois_sended"

# after (optional) shipping, it's the pre-checkout
def precheckout_callback(update: Update, context: CallbackContext) -> None:
    """Answers the PreQecheckoutQuery"""
    user_id = update.pre_checkout_query.from_user.id
    query = update.pre_checkout_query
    if context.user_data.get("payment_started"):
        # check the payload, is this from your bot?
        if query.invoice_payload != "URBANIUS_CLUB":
            # answer False pre_checkout_query
            query.answer(ok=False, error_message="Что-то пошло не так...")
            context.user_data["payment_started"] = False
            send_message(user_id=user_id, text = "Что-то пошло не так...")
            return "manage_event"
        else:
            query.answer(ok=True)
            return "checkout"
    else:
        query.answer(ok=False, error_message="Срок платежа прошел. Начните новый платеж")
        send_message(user_id=user_id, text = "Срок платежа прошел. Начните новый платеж")
        return "manage_event"


# finally, after contacting the payment provider...
def successful_payment_callback(update: Update, context: CallbackContext) -> None:
    """Confirms the successful payment."""
    # do something after successfully receiving payment?
    context.user_data["payment_started"] = False
    userdata = extract_user_data_from_update(update)
    user = User.get_user_by_username_or_user_id(userdata["user_id"])   
    payment_request = context.user_data["payment_request"]
    query = update.message.successful_payment
    payment = Payments()
    payment.user = user
    payment.price = payment_request.price
    payment.invoice_payload = query.invoice_payload
    payment.provider_payment_charge_id = query.provider_payment_charge_id
    payment.telegram_payment_charge_id = query.telegram_payment_charge_id
    payment.email = query.order_info.email
    payment.name = query.order_info.name
    payment.phone_number = query.order_info.phone_number
    payment.total_amount = query.total_amount/100
    payment.save()
    
    payment_request.payment = payment
    payment_request.payed = True
    payment_request.save()
    send_message(user_id=user.user_id, text = "Спасибо за Ваш платеж!")
    send_event_desc(payment_request.event, user)   
    return "manage_event"


def show_requested_events(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    requests_set = EventRequests.objects.filter(event__date__gte = datetime.datetime.now() - datetime.timedelta(days=40),
                                    event__date__lte = datetime.datetime.now() + datetime.timedelta(days=1), user = user, confirmed = True)
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
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    event: Events
    event = Events.objects.get(pk = int(query.data))
    text = event.get_description()
    text += event.get_user_info(user)
    set_rating_btn = {
                      "1_" + str(event.pk):"1",
                      "2_" + str(event.pk):"2",
                      "3_" + str(event.pk):"3",
                      "4_" + str(event.pk):"4",
                      "5_" + str(event.pk):"5",
                      }   
    reply_markup = make_keyboard(set_rating_btn,"inline",5,None,BACK_EV_CLNDR)

    if event.file:
        query.edit_message_reply_markup(make_keyboard(EMPTY,"inline",1))        
        file_ext = event.file.name.split(".")[-1]
        file_path = event.file.path
        if os.path.exists(file_path):
            if (not event.file_id) or wrong_file_id(event.file_id):
                fill_file_id(event, "file")
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
    query_data = query.data.split("_")
    rating = query_data[0]
    event = Events.objects.get(pk = int(query_data[1]))
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
    requests_set = EventRequests.objects.filter(event__date__gte = datetime.datetime.now() - datetime.timedelta(days=40),
                                    event__date__lte = datetime.datetime.now() + datetime.timedelta(days=30), user = user, confirmed = True)
    btn_events = {}
    for request in requests_set:        
        btn_events[request.event.pk] = str(request.event)
    
    update.message.reply_text("Мероприятию установлена оценка")     
    update.message.reply_text("Прошедшие мероприятия", reply_markup=make_keyboard(btn_events,"inline",1,None,BACK_EV_MNU))
  
    return "select_req_event"



def setup_dispatcher_conv(dp: Dispatcher):

    # Диалог
    conv_handler = ConversationHandlerMy( 
        # точка входа в разговор      
        entry_points=[CallbackQueryHandler(start_conversation, pattern="^events$")],      
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            "working":[CallbackQueryHandler(show_event_calendar, pattern="^calendar$"),
                       CallbackQueryHandler(show_requested_events, pattern="^requested$"),
                       CallbackQueryHandler(stop_conversation, pattern="^back$"),
                       MessageHandler(Filters.text & FilterPrivateNoCommand, bad_input),# Не делать асинхронным
                      ],
            "select_event":[CallbackQueryHandler(start_conversation, pattern="^back_ev$"),
                            CallbackQueryHandler(show_event),
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
    "set_rating_comment":[
                          MessageHandler(Filters.text & FilterPrivateNoCommand, set_rating_comment),
                         ],

            "invois_sended":[
                       PreCheckoutQueryHandler(precheckout_callback),                    
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
                fill_file_id(event, "file")
            if file_ext in ["jpg","jpeg","png","gif","tif","tiff","bmp"]:
                send_photo(user.user_id, event.file_id, caption = text, 
                           reply_markup = reply_markup, parse_mode = ParseMode.HTML)
            elif file_ext in ["mp4","avi","mov","mpeg"]:
                send_video(user.user_id, event.file_id, caption = text, 
                                      reply_markup = reply_markup, parse_mode = ParseMode.HTML)
            else:
                send_message(user.user_id, text = text, reply_markup = reply_markup, parse_mode = ParseMode.HTML)
        else:
            send_message(user.user_id, text = text, reply_markup = reply_markup, parse_mode = ParseMode.HTML)
    else:
        send_message(user.user_id, text = text, reply_markup = reply_markup, parse_mode = ParseMode.HTML)
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



