import datetime
from dateutil.relativedelta import relativedelta
from telegram import ParseMode,  Update, LabeledPrice, CallbackQuery
from telegram.ext import (
    Dispatcher, CommandHandler,PreCheckoutQueryHandler,
    MessageHandler, CallbackQueryHandler,
    Filters, CallbackContext,
)
from tgbot.my_telegram import ConversationHandler as ConversationHandlerMy
from django.conf import settings
from tgbot.models import User, Status
from .messages import *
from .answers import *
from .models import *

from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.filters import FilterPrivateNoCommand
from tgbot.handlers.utils import send_message
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

    # send_message(user_id=user_id, text=FINISH, reply_markup=make_keyboard(EMPTY,"usual",1))
    # send_message(user_id=user_id, text=)
    return ConversationHandlerMy.END

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
    query.edit_message_text(text=HELLO_MESS, reply_markup=make_keyboard(pkg_mnu(),"inline",1,None,BACK))

    return "working"

def show_packge(update: Update, context: CallbackContext):
    """
    Показывает выбранный пакет участия
    """
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    pkg = ClubPackages.objects.get(pk = int(query.data))
    decr_obj = PackageDescrForStatus.objects.filter(package = pkg, for_status = user.status).first()
    text = f'Пакет участия: <b>{pkg.name}</b>\n'
    text += f'Для Вашего статуса <b>"{user.status}"</b> пакет дает следующие возможности:\n'
    if decr_obj:
        text += decr_obj.description + "\n"
        pkg_mnu = {}
        pkg_mnu[f"show_pkg_requests-{pkg.pk}"] = "Показать заявки" #
        reply_markup = make_keyboard(pkg_mnu,"inline",1,None,BACK_PKG_LST)
    else:
        text += "Пакет не доступен для заказа данным статусом"
        reply_markup=make_keyboard(EMPTY,"inline",1,None,BACK_PKG_LST)
    
    query.edit_message_text(text = text, reply_markup = reply_markup, parse_mode = ParseMode.HTML)
    return "manage_packge"

def show_pkg_requests(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    q_data = query.data.split("-")
    pkg = ClubPackages.objects.get(pk = int(q_data[-1]))
    update_reqw_list(pkg, user, query)
    return "manage_requests"

def del_pkg_requests(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    q_data = query.data.split("-")
    pkg = ClubPackages.objects.get(pk = int(q_data[-1]))
    req_mnu = {}
    for pkg_req in pkg.packagerequests_set.filter(user = user, payed = False, confirmed = False):
        req_mnu[f"del_reqw-{pkg_req.pk}"] = str(pkg_req) 
    reply_markup = make_keyboard(req_mnu,"inline",1,None,BACK_PKG_LST) 
    text = "Выберите удаляемую заявку"   
    query.edit_message_text(text = text, reply_markup = reply_markup, parse_mode = ParseMode.HTML)
    return "manage_del_requests"

def del_reqw(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    q_data = query.data.split("-")
    reqw = PackageRequests.objects.get(pk = int(q_data[-1]))
    pkg = reqw.package
    reqw.delete()
    update_reqw_list(pkg, user, query)
    return "manage_requests"

def create_pkg_request_ask_price(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    q_data = query.data.split("-")
    pkg = ClubPackages.objects.get(pk = int(q_data[-1]))
    price_mnu = {}
    for pkg_price in pkg.packageprices_set.filter(for_status = user.status):
        price_mnu[f"pkg_price-{pkg_price.pk}"] = str(pkg_price)   
    if len(price_mnu) == 0:
        text = "Для вышего статуса нет предложений по этому пакету"
    else:
        text = "Выберите вариант подписки"
    reqw_mnu = {f"show_pkg_requests-{pkg.pk}":"Вернуться к списку заявок"} #
    reply_markup = make_keyboard(price_mnu,"inline",1,None,reqw_mnu) 
    query.edit_message_text(text = text, reply_markup = reply_markup, parse_mode = ParseMode.HTML)
    return "manage_choosed_price"       

def create_pkg_request(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    q_data = query.data.split("-")
    pkg_price = PackagePrices.objects.get(pk = int(q_data[-1]))
    pkg_reqw = PackageRequests()
    pkg_reqw.package = pkg_price.package
    pkg_reqw.user = user
    pkg_reqw.for_status = user.status
    pkg_reqw.package_price = pkg_price
    pkg_reqw.price = pkg_price.price
    last_subscr_date = pkg_price.package.get_subscrition_date(user)
    if last_subscr_date:
        pkg_reqw.date_from = last_subscr_date + datetime.timedelta(1)
    else:
        pkg_reqw.date_from = datetime.date.today()

    pkg_reqw.date_to = pkg_reqw.date_from + relativedelta(months=+pkg_price.period)
    pkg_reqw.save()
    update_reqw_list(pkg_price.package, user, query)
    return "manage_requests"


def pay_pkg_requests(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    q_data = query.data.split("-")
    pkg = ClubPackages.objects.get(pk = int(q_data[-1]))
    req_mnu = {}
    for pkg_req in pkg.packagerequests_set.filter(user = user, payed = False, price__gt = 0):
        req_mnu[f"pay_reqw-{pkg_req.pk}"] = str(pkg_req) 
    reply_markup = make_keyboard(req_mnu,"inline",1,None,BACK_PKG_LST) 
    text = "Выберите оплачиваемую заявку"   
    query.edit_message_text(text = text, reply_markup = reply_markup, parse_mode = ParseMode.HTML)
    return "manage_pay_requests"


def make_invoice(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_reply_markup(make_keyboard(EMPTY,"inline",1))
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)  
    # разбираем пришедшие данные. пример 'pay_request_event-256'
    # pay_request - действие, event - имя обекта, 256 - индекс объекта в БД
    query_data = query.data.split("-")
    obj_pk = int(query_data[-1])  # получили индекс объекта в БД
 
    payment_request = PackageRequests.objects.get(pk = int(obj_pk))
    pkg = payment_request.package
    context.user_data["payment_started"] = True
    context.user_data["payment_request"] = payment_request
    send_invois_to_tg(user,pkg,payment_request)
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
    update_reqw_list(payment_request.package, user, query)
    return "manage_requests"
      
def setup_dispatcher_conv(dp: Dispatcher):
    # Диалог
    conv_handler = ConversationHandlerMy( 
        # точка входа в разговор      
        entry_points=[CallbackQueryHandler(start_conversation, pattern="^packages$"),
                     ],      
        # этапы разговора, каждый со своим списком обработчиков сообщений
            states={
             "working":[
                        CallbackQueryHandler(stop_conversation, pattern="^back$"),
                        CallbackQueryHandler(show_packge),
                        MessageHandler(Filters.text & FilterPrivateNoCommand, bad_input),# Не делать асинхронным
                        ],
        "manage_packge":[CallbackQueryHandler(start_conversation, pattern="^back_lst$"),
                        CallbackQueryHandler(show_pkg_requests, pattern="^show_pkg_requests-"),
                        CallbackQueryHandler(blank),
                        MessageHandler(Filters.text & FilterPrivateNoCommand, bad_input),# Не делать асинхронным
                        ],
        "manage_requests":[CallbackQueryHandler(start_conversation, pattern="^back_lst$"),
                        CallbackQueryHandler(del_pkg_requests, pattern="^del_pkg_requests-"),
                        CallbackQueryHandler(pay_pkg_requests, pattern="^pay_pkg_requests-"),
                        CallbackQueryHandler(create_pkg_request_ask_price, pattern="^create_pkg_requests-"),
                        CallbackQueryHandler(blank),
                        MessageHandler(Filters.text & FilterPrivateNoCommand, bad_input),# Не делать асинхронным
                        ],
        "manage_del_requests":[CallbackQueryHandler(start_conversation, pattern="^back_lst$"),
                        CallbackQueryHandler(del_reqw, pattern="^del_reqw-"),
                        CallbackQueryHandler(blank),
                        MessageHandler(Filters.text & FilterPrivateNoCommand, bad_input),# Не делать асинхронным
                        ], 
        "manage_choosed_price":[CallbackQueryHandler(show_pkg_requests, pattern="^show_pkg_requests-"),
                        CallbackQueryHandler(create_pkg_request, pattern="^pkg_price-"),
                        CallbackQueryHandler(blank),
                        MessageHandler(Filters.text & FilterPrivateNoCommand, bad_input),# Не делать асинхронным
                        ],

        "manage_pay_requests":[CallbackQueryHandler(start_conversation, pattern="^back_lst$"),
                        CallbackQueryHandler(make_invoice, pattern="^pay_reqw-"),
                        CallbackQueryHandler(blank),
                        MessageHandler(Filters.text & FilterPrivateNoCommand, bad_input),# Не делать асинхронным
                        ],  
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
    
def update_reqw_list(pkg: ClubPackages, user: User, query):
    text = f"По вашему пакету {pkg}: \n"
    text += pkg.get_subscrition_txt(user) + "\n"
    can_del = False
    text += "Заявки: \n"
    for pkg_req in pkg.packagerequests_set.filter(user = user): 
        text += pkg_req.getdescr() + "\n"
        if (not pkg_req.payed) and (not pkg_req.confirmed):
            can_del = True
    pkg_mnu = {}    
    if can_del: 
        pkg_mnu[f"pay_pkg_requests-{pkg.pk}"] = "Оплатить доступные заявки"
        pkg_mnu[f"del_pkg_requests-{pkg.pk}"] = "Удалить доступные заявки"
    else:
        pkg_mnu[f"create_pkg_requests-{pkg.pk}"] = "Создать заявку" 
    reply_markup = make_keyboard(pkg_mnu,"inline",1,None,BACK_PKG_LST)
    if type(query) == CallbackQuery:
        query.edit_message_text(text = text, reply_markup = reply_markup, parse_mode = ParseMode.HTML)
    else:
        send_message(user.user_id, text, reply_markup = reply_markup, parse_mode = ParseMode.HTML)
 