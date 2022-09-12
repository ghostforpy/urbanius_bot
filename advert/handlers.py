from importlib.util import source_hash
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
from dtb.constants import StatusCode
from tgbot.handlers.filters import FilterPrivateNoCommand
from tgbot.models import User
from events.models import EventRequests
from .models import *
from .messages import *
from .answers import *
from tgbot.handlers.utils import send_message, send_photo, send_mess_by_tmplt, _get_file_id
from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.main.answers import get_start_menu
from tgbot.handlers.main.messages import get_start_mess
from tgbot import utils

def use_partner_spec_offer (update: Update, context: CallbackContext):
    """
     Вызывается когда нажимается кнопка "Вроспользоваться предложенем"
     в спец предложении партнера
    """
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    query_data = query.data.split("-")
    offer_pk = int(query_data[-1])
    offer = SpecialOffers.objects.get(pk = offer_pk)
    so_discount = offer.specialoffersdiscounts_set.filter(for_status = user.status).first()
    if not so_discount:
        text = f"Для вашего статуса '{user.status}' данное предложение не действует"
        send_message(user_id=user_id, text = text)
        return       
    so_user_reqwest = SOUserRequests.objects.filter(offer = offer,user = user).first()
    if so_user_reqwest:
        send_message(user_id=user_id, text = REQWEST_EXIST)
        return
    so_user_reqwest = SOUserRequests()
    so_user_reqwest.offer = offer
    so_user_reqwest.user = user
    so_user_reqwest.for_status = user.status
    so_user_reqwest.discount = so_discount.discount
    so_user_reqwest.sended_to_partner = True
    so_user_reqwest.save()
    subject = "URBANIUS BOT: заявка на специальное предложение"
    message = f"Участник URBANIUS CLUB {user.last_name} {user.first_name} {user.sur_name} запросил у Вас скидку "
    message += f"по Вашему специальному предложению: '{offer}' \n"
    message += f"Номер запроса: {so_user_reqwest.pk} \n"
    message += f"Статус участника: {user.status} \n"
    message += f"Размер скидки: {so_user_reqwest.discount}% \n"
    message += f"Телефон: {user.telefon} \n"
    message += f"E-mail: {user.email} \n"
    message += "\n"
    message += "С уважением, URBANIUS BOT"
    if offer.partner and offer.partner.email:
        send_mail(subject, message, settings.EMAIL_HOST_USER, [offer.partner.email])
    if offer.user:
        if offer.user.email:
            send_mail(subject, message, settings.EMAIL_HOST_USER, [offer.user.email])
    send_message(offer.user.user_id, message)
    kontrag = str(offer.user) if offer.user else offer.partner.full_name
    text = f"Вы получили скидку {so_discount.discount}% у партнера '{kontrag}' " \
           f"на предложение '{offer}'. Для получения скидки сообщите партнеру ее номер '{so_user_reqwest.pk}'"
    send_message(user_id=user_id, text = text)


# Диалог работы со спец предложениями
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

    send_message(user_id=user_id, text=SO_FINISH, reply_markup=make_keyboard(EMPTY,"usual",1))
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
    query.edit_message_text(text=HELLO_SO_MESS, reply_markup=make_keyboard(SPEC_OFF_MNU,"inline",1,None,BACK))

    return "working"

#---------------------------------------------
#-------------VIEWING SO ---------------------

def show_so_list(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    so_set = SpecialOffers.objects.filter(valid_until__gte = datetime.date.today(), confirmed = True)
    btns = {}
    for so in so_set:
        btns[f"show_so-{so.pk}"] = str(so)
    if len(btns) > 0:
        text = "Выберите спецпредложение для просмотра подробностей"
    else:
        text = "Отсутствуют спецпредложения"    
    reply_markup = make_keyboard(btns,"inline",1,None,BACK)
    query.edit_message_text(text=text, reply_markup = reply_markup)   
    return "show_so_list"


def show_so(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    query_data = query.data.split("-")
    so = SpecialOffers.objects.get(pk = int(query_data[-1]))
    kontrag = so.partner if so.partner else so.user
    head_text = f"<b>Спецпредложение :</b> {so.name} \n"
    head_text += f"<b>От:</b> {kontrag}\n"
    head_text += f"<b>Текст предложения:</b> "

    valid_until = mystr(so.valid_until)
    fut_text = f"\n<b>Действует до:</b> {valid_until}\n"
    fut_text +=  "<b>Подтверждено</b>" if so.confirmed else "<b>Не подтверждено</b>"

    bns = {}
    bns[f"use_offer_from_list-{so.pk}"] = "Воспользоваться предложением"
    bns["reqw_lst"] = "Вернуться к списку предложений"

    reply_markup = make_keyboard(bns,"inline",1,None,BACK)
    query.edit_message_reply_markup(make_keyboard(EMPTY,"inline",1))
    send_mess_by_tmplt(user_id, so, reply_markup ,head_text = head_text, fut_text = fut_text) 
    return "show_so"


def use_so(update: Update, context: CallbackContext):
    use_partner_spec_offer(update, context)
    stop_conversation(update, context)
    return ConversationHandler.END

#---------------------------------------
#-------------ADDING SO ----------------
def add_spec_offer(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    keyboard = make_keyboard(CANCEL,"usual",1)
    send_message(user_id, ASK_SO_NAME, reply_markup=keyboard)
    return "ask_so_name"

def rem_so_name(update: Update, context: CallbackContext):
    context.user_data["so_name"] = update.message.text
    keyboard = make_keyboard(CANCEL,"usual",1)
    update.message.reply_text(ASK_SO_TEXT, reply_markup=keyboard)
    return "ask_so_text"

def rem_so_text(update: Update, context: CallbackContext):
    context.user_data["so_text"] = update.message.text
    keyboard = make_keyboard(CANCEL,"usual",1)
    update.message.reply_text(ASK_SO_VALID_DATE, reply_markup=keyboard)
    return "ask_so_valid_date"

def rem_so_valid_date(update: Update, context: CallbackContext):
    date = utils.is_date(update.message.text)
    if not(date): # ввели неверную дату
        update.message.reply_text(BAD_DATE, make_keyboard(CANCEL,"usual",1))
        return  
    context.user_data["so_valid_date"] = date
    keyboard = make_keyboard(CANCEL_SKIP,"usual",1)
    update.message.reply_text(ASK_SO_IMAGE, reply_markup=keyboard)
    return "ask_so_image"

def rem_so_image(update: Update, context: CallbackContext):
    user = User.get_user_by_username_or_user_id(update.message.from_user.id)
    so = SpecialOffers()
    so.user = user
    so.name = context.user_data["so_name"]
    so.text = context.user_data["so_text"]
    so.valid_until = context.user_data["so_valid_date"]
    if len(update.message.photo)>0:
        foto_id, filename_orig = _get_file_id(update.message)
        filename_lst = filename_orig.split(".")
        newFile = context.bot.get_file(foto_id)
        filename = utils.get_uniq_file_name(settings.BASE_DIR / "media/advert",filename_lst[0],filename_lst[1])
        newFile.download(settings.BASE_DIR / ("media/advert/"+filename))
        so.file = "advert/"+filename
        so.file_id = foto_id
    so.save()
    so_dis = SpecialOffersDiscounts()
    so_dis.offer = so
    so_dis.for_status = Status.objects.get(code = StatusCode.GROUP_MEMBER)
    so_dis.discount = 10
    so_dis.save()
    so_dis = SpecialOffersDiscounts()
    so_dis.offer = so
    so_dis.for_status = Status.objects.get(code = StatusCode.COMMUNITY_RESIDENT)
    so_dis.discount = 20
    so_dis.save()
    so_dis = SpecialOffersDiscounts()
    so_dis.offer = so
    so_dis.for_status = Status.objects.get(code = StatusCode.CLUB_RESIDENT)
    so_dis.discount = 30
    so_dis.save()
    keyboard = make_keyboard(EMPTY,"usual",1)
    update.message.reply_text(SO_SAVED, reply_markup=keyboard)
    stop_conversation(update, context)

    group = tgGroups.get_group_by_name("Администраторы")
    if (group == None) or (group.chat_id == 0):
        pass
    else:
        text = f"Зарегистрировано спецпредложение от пользователя {user} Тема: {so.name}"
        reply_markup = make_keyboard(EMPTY,"inline",1)
        send_message(group.chat_id, text, reply_markup = reply_markup)

    return ConversationHandler.END


def setup_dispatcher_conv(dp: Dispatcher):
    dp.add_handler(CallbackQueryHandler(use_partner_spec_offer, pattern="^use_offer-"))
    
    conv_handler = ConversationHandler( 
        # точка входа в разговор      
        entry_points=[CallbackQueryHandler(start_conversation, pattern="^spec_offers$")],      
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            "working":[             
                       CallbackQueryHandler(stop_conversation, pattern="^back$"),
                       CallbackQueryHandler(show_so_list, pattern="^spec_offers_list$"),
                       CallbackQueryHandler(add_spec_offer, pattern="^add_spec_offer$"),
                       MessageHandler(Filters.text & FilterPrivateNoCommand, blank)
                      ],
            "show_so_list":[
                          CallbackQueryHandler(stop_conversation, pattern="^back$"),
                          CallbackQueryHandler(show_so, pattern="^show_so-"),
                          MessageHandler(Filters.text([BACK["back"]]) & FilterPrivateNoCommand, stop_conversation),
                         ],
            "show_so":[
                          CallbackQueryHandler(stop_conversation, pattern="^back$"),
                          CallbackQueryHandler(show_so_list, pattern="^reqw_lst$"),
                          CallbackQueryHandler(use_so, pattern="use_offer_from_list-"),
                          MessageHandler(Filters.text([BACK["back"]]) & FilterPrivateNoCommand, stop_conversation),
                         ],    
            "ask_so_name":[
                          MessageHandler(Filters.text([CANCEL["cancel"]]) & FilterPrivateNoCommand, start_conversation),
                          MessageHandler(Filters.text([BACK["back"]]) & FilterPrivateNoCommand, stop_conversation),
                          MessageHandler(Filters.text & FilterPrivateNoCommand, rem_so_name),
                         ],
            "ask_so_text":[
                          MessageHandler(Filters.text([CANCEL["cancel"]]) & FilterPrivateNoCommand, start_conversation),
                          MessageHandler(Filters.text([BACK["back"]]) & FilterPrivateNoCommand, stop_conversation),
                          MessageHandler(Filters.text & FilterPrivateNoCommand, rem_so_text),
                         ],
     "ask_so_valid_date":[
                          MessageHandler(Filters.text([CANCEL["cancel"]]) & FilterPrivateNoCommand, start_conversation),
                          MessageHandler(Filters.text([BACK["back"]]) & FilterPrivateNoCommand, stop_conversation),
                          MessageHandler(Filters.text & FilterPrivateNoCommand, rem_so_valid_date),
                         ],
         "ask_so_image":[

                          MessageHandler(Filters.text([CANCEL["cancel"]]) & FilterPrivateNoCommand, start_conversation),
                          MessageHandler(Filters.text([BACK["back"]]) & FilterPrivateNoCommand, stop_conversation),
                          MessageHandler((Filters.photo | Filters.text) & FilterPrivateNoCommand, rem_so_image),
                         ],
         },
        # точка выхода из разговора
        fallbacks=[CommandHandler('cancel', stop_conversation, Filters.chat_type.private),
                   CommandHandler('start', stop_conversation, Filters.chat_type.private)]        
    )
    dp.add_handler(conv_handler) 