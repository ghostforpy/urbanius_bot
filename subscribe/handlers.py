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

from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.filters import FilterPrivateNoCommand
from tgbot.handlers.utils import send_message, send_photo, send_video, fill_file_id, wrong_file_id
from tgbot.handlers.main.answers import get_start_menu
from tgbot.handlers.main.messages import get_start_mess
from tgbot.utils import extract_user_data_from_update



def stop_conversation(update: Update, context: CallbackContext):
    """ 
       Возврат к главному меню    
    """
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
    Показывает выбранное мероприятие
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
    text = f"По вашему пакету {pkg}: \n"
    text += pkg.get_subscrition_txt(user) + "\n"
    can_del = False
    text += "Заявки: \n"
    for pkg_req in pkg.packagerequests_set.filter(user = user): 
        text += pkg_req.getdescr() + "\n"
        if (not pkg_req.payed) and (not pkg_req.confirmed):
            can_del = True
    pkg_mnu = {}
    pkg_mnu[f"create_pkg_requests-{pkg.pk}"] = "Создать заявку" 
    if can_del: 
        pkg_mnu[f"del_pkg_requests-{pkg.pk}"] = "Удалить доступные заявки"
    reply_markup = make_keyboard(pkg_mnu,"inline",1,None,BACK_PKG_LST)
    query.edit_message_text(text = text, reply_markup = reply_markup, parse_mode = ParseMode.HTML)
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
        },
            # точка выхода из разговора
             fallbacks=[CommandHandler('cancel', stop_conversation, Filters.chat_type.private),
                        CommandHandler('start', stop_conversation, Filters.chat_type.private)]        
    )

    dp.add_handler(conv_handler)
    


