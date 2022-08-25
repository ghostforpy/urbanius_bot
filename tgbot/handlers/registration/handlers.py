from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import (
    Dispatcher, CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)
from dtb.constants import MessageTemplatesCode
from dtb.constants import StatusCode
from .messages import *
from .answers import *
from tgbot.handlers.main.messages import NO_ADMIN_GROUP
from tgbot.models import Status, User, UsertgGroups, tgGroups, UserReferrers, NewUser
from sheduler.models import MessageTemplates

from tgbot.handlers.utils import send_message, send_mess_by_tmplt
from tgbot.handlers.keyboard import make_keyboard
from tgbot import utils
from tgbot.handlers.filters import FilterPrivateNoCommand
from tgbot.handlers.utils import send_message


# Шаги диалога
APROVAL,PHONE,FIO,ABOUT,BIRHDAY,EMAIL,CITI,COMPANY,JOB,SITE = range(10)

def stop_conversation(update: Update, context: CallbackContext):
    # Заканчиваем разговор.
    context.user_data.clear()
    keyboard = make_keyboard(START,"usual",1)
    update.message.reply_text(REGISTRATION_CANCELED, reply_markup=keyboard)
    return ConversationHandler.END

def start_conversation(update: Update, context: CallbackContext):

    update.message.reply_text(WELCOME_REG, reply_markup=make_keyboard(APPROVAL_ANSWERS,"usual",2))
    return APROVAL  

def processing_aproval(update: Update, context: CallbackContext):
    if update.message.text == APPROVAL_ANSWERS["yes"]: # В этом поле хранится согласие       
        update.message.reply_text(ASK_PHONE,  reply_markup=make_keyboard(CANCEL_SKIP,"usual",2,REQUEST_PHONE))
        return PHONE
    elif update.message.text == APPROVAL_ANSWERS["no"]: # В этом поле хранится отказ
        stop_conversation(update, context)
        return ConversationHandler.END
    else:
        update.message.reply_text(ASK_REENTER, reply_markup=make_keyboard(APPROVAL_ANSWERS,"usual",2))

def processing_phone(update: Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id = update.message.from_user.id)
    fullname = " ".join([new_user.first_name, utils.mystr(new_user.last_name), utils.mystr(new_user.sur_name)])
    if update.message.contact != None: # Был прислан контакт        
        # Запоминаем телефон
        new_user.telefon = update.message.contact.phone_number
        new_user.save()
        # Если пользователь новый проверяем есть ли у него в Телеграмм имя пользователя
        if new_user.username == None:
             update.message.reply_text(USERNAME_NEEDED)
        keyboard = make_keyboard(CANCEL_SKIP,"usual",1)
        update.message.reply_text(ASK_FIO.format(fullname), reply_markup=keyboard)
        return FIO
    elif update.message.text == CANCEL["cancel"]: # Отказались отправить телефон
        stop_conversation(update, context)
        return ConversationHandler.END
    elif update.message.text == CANCEL_SKIP["skip"]:
        keyboard = make_keyboard(CANCEL_SKIP,"usual",2)
        update.message.reply_text(ASK_FIO.format(fullname), reply_markup=keyboard)
        return FIO
    else:
        update.message.reply_text(ASK_REENTER, reply_markup=make_keyboard(CANCEL_SKIP,"usual",2,REQUEST_PHONE))

def processing_fio(update: Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id = update.message.from_user.id)
    if update.message.text == CANCEL["cancel"]:
        stop_conversation(update, context)
        return ConversationHandler.END
    elif update.message.text == CANCEL_SKIP["skip"]:
        keyboard = make_keyboard(CANCEL_SKIP,"usual",1)
        update.message.reply_text(ASK_ABOUT + f"\n Уже введено: '{utils.mystr(utils.mystr(new_user.about))}'", reply_markup=keyboard)
        return ABOUT
    else:
        fio = update.message.text.split()
        len_fio = len(fio)
        if len_fio == 1:
            new_user.first_name = fio[0] # Имя
        elif len_fio == 2:
            new_user.first_name = fio[0] # Имя
            new_user.last_name = fio[1]  # Фамилия
        elif len_fio > 2:
            new_user.last_name = fio[0]  # Фамилия
            new_user.first_name = fio[1] # Имя
            new_user.sur_name = fio[2]   # Отчество
        new_user.save()
        keyboard = make_keyboard(CANCEL_SKIP,"usual",2)
        update.message.reply_text(ASK_ABOUT + f"\n Уже введено: '{utils.mystr(new_user.about)}'", reply_markup=keyboard)
        return ABOUT

def processing_about(update: Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id = update.message.from_user.id)
    if update.message.text == CANCEL["cancel"]:
        stop_conversation(update, context)
        return ConversationHandler.END
    elif update.message.text == CANCEL_SKIP["skip"]:
        keyboard = make_keyboard(CANCEL_SKIP,"usual",1)
        update.message.reply_text(ASK_BIRHDAY + f"\n Уже введено: '{utils.mystr(new_user.date_of_birth)}'", reply_markup=keyboard)
        return BIRHDAY    
    else:
        new_user.about = update.message.text 
        new_user.save()       
        keyboard = make_keyboard(CANCEL_SKIP,"usual",2)
        update.message.reply_text(ASK_BIRHDAY + f"\n Уже введено: '{utils.mystr(new_user.date_of_birth)}'", reply_markup=keyboard)
        return BIRHDAY

def processing_birhday(update: Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id = update.message.from_user.id)
    date = utils.is_date(update.message.text)

    if update.message.text == CANCEL_SKIP["cancel"]: # решили прервать регистрацию
       stop_conversation(update, context)
       return ConversationHandler.END
    elif update.message.text == CANCEL_SKIP["skip"]:
        keyboard = make_keyboard(CANCEL_SKIP,"usual",2)
        update.message.reply_text(ASK_EMAIL + f"\n Уже введено: '{utils.mystr(new_user.email)}'", reply_markup=keyboard)
        return EMAIL
    elif not(date): # ввели неверную дату
        update.message.reply_text(BAD_DATE, make_keyboard(CANCEL_SKIP,"usual",2))
        return    
    else: # ввели верный дату
        new_user.date_of_birth = date
        new_user.save()
        keyboard = make_keyboard(CANCEL_SKIP,"usual",2)
        update.message.reply_text(ASK_EMAIL + f"\n Уже введено: '{utils.mystr(new_user.email)}'", reply_markup=keyboard)
        return EMAIL

def processing_email(update: Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id = update.message.from_user.id)
    email = utils.is_email(update.message.text)

    if update.message.text == CANCEL_SKIP["cancel"]: # решили прервать регистрацию
       stop_conversation(update, context)
       return ConversationHandler.END
    elif update.message.text == CANCEL_SKIP["skip"]:
        keyboard = make_keyboard(CANCEL_SKIP,"usual",2)
        update.message.reply_text(ASK_CITI + f"\n Уже введено: '{utils.mystr(new_user.citi)}'", reply_markup=keyboard)
        return CITI
    elif not(email): # ввели неверную email
        update.message.reply_text(BAD_EMAIL,make_keyboard(CANCEL_SKIP,"usual",2))
        return    
    else: 
        new_user.email = email
        new_user.save()
        keyboard = make_keyboard(CANCEL_SKIP,"usual",2)
        update.message.reply_text(ASK_CITI + f"\n Уже введено: '{utils.mystr(new_user.citi)}'", reply_markup=keyboard)
        return CITI

def processing_citi(update: Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id = update.message.from_user.id)
    if update.message.text == CANCEL_SKIP["cancel"]: # решили прервать регистрацию
       stop_conversation(update, context)
       return ConversationHandler.END
    elif update.message.text == CANCEL_SKIP["skip"]:
        keyboard = make_keyboard(CANCEL_SKIP,"usual",2)
        update.message.reply_text(ASK_COMPANY + f"\n Уже введено: '{utils.mystr(new_user.company)}'", reply_markup=keyboard)
        return COMPANY   
    else: 
        new_user.citi = update.message.text
        new_user.save()
        keyboard = make_keyboard(CANCEL_SKIP,"usual",2)
        update.message.reply_text(ASK_COMPANY + f"\n Уже введено: '{utils.mystr(new_user.company)}'", reply_markup=keyboard)
        return COMPANY

def processing_company(update: Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id = update.message.from_user.id)
    if update.message.text == CANCEL_SKIP["cancel"]: # решили прервать регистрацию
       stop_conversation(update, context)
       return ConversationHandler.END
    elif update.message.text == CANCEL_SKIP["skip"]:
        keyboard = make_keyboard(CANCEL_SKIP,"usual",2)
        update.message.reply_text(ASK_JOB + f"\n Уже введено: '{utils.mystr(new_user.job)}'", reply_markup=keyboard)
        return JOB   
    else: 
        new_user.company = update.message.text
        new_user.save()
        keyboard = make_keyboard(CANCEL_SKIP,"usual",2)
        update.message.reply_text(ASK_JOB + f"\n Уже введено: '{utils.mystr(new_user.job)}'", reply_markup=keyboard)
        return JOB

def processing_job(update: Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id = update.message.from_user.id)
    if update.message.text == CANCEL_SKIP["cancel"]: # решили прервать регистрацию
       stop_conversation(update, context)
       return ConversationHandler.END
    elif update.message.text == CANCEL_SKIP["skip"]:
        keyboard = make_keyboard(CANCEL_SKIP,"usual",2)
        update.message.reply_text(ASK_SITE + f"\n Уже введено: '{utils.mystr(new_user.site)}'", reply_markup=keyboard)
        return SITE   
    else: 
        new_user.job = update.message.text
        new_user.save()
        keyboard = make_keyboard(CANCEL_SKIP,"usual",2)
        update.message.reply_text(ASK_SITE + f"\n Уже введено: '{utils.mystr(new_user.site)}'", reply_markup=keyboard)
        return SITE

def processing_site(update: Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id = update.message.from_user.id)
    if update.message.text == CANCEL_SKIP["cancel"]: # решили прервать регистрацию
       stop_conversation(update, context)
       return ConversationHandler.END
    elif update.message.text == CANCEL_SKIP["skip"]:
        site = ""   
    else:
        site = update.message.text
    
    new_user.site = site
    new_user.registered = True
    new_user.save()

    user = User(user_id=new_user.user_id)
    user.username = new_user.username
    user.last_name = new_user.last_name
    user.first_name = new_user.first_name
    user.email = new_user.email
    user.telefon = new_user.telefon
    user.sur_name = new_user.sur_name
    user.date_of_birth = new_user.date_of_birth
    user.company = new_user.company
    user.job = new_user.job
    user.branch = new_user.branch
    user.citi = new_user.citi
    user.job_region = new_user.job_region
    user.site = new_user.site
    user.about = new_user.about
    user.created_at = new_user.created_at
    user.language_code = new_user.language_code
    user.deep_link = new_user.deep_link
    user.status = Status.objects.get(code = StatusCode.APPLICANT)
    user.is_blocked_bot = True
    user.comment = "Ожидает подтверждения регистрации"
    user.save()
    # Назначение пользователю рекомендателя, если он пришел по партнерской ссылке
    referrer = User.get_user_by_username_or_user_id(user.deep_link)
    if referrer:
        user_referer = UserReferrers(referrer = referrer, user = user)
        user_referer.save()
    # Назначение пользователю групп по умолчанию
    groups_set = tgGroups.objects.filter(for_all_users = True)
    for group in groups_set:
        user_group = UsertgGroups(group,user)
        user_group.save()
        
    reply_markup = make_keyboard(START,"usual",1)
    mess_template = MessageTemplates.objects.get(code = MessageTemplatesCode.WELCOME_NEWUSER_MESSAGE)

    send_mess_by_tmplt(user.user_id, mess_template, reply_markup) 

    group = tgGroups.get_group_by_name("Администраторы")
    if (group == None) or (group.chat_id == 0):
        update.message.reply_text(NO_ADMIN_GROUP)
    else:
        text = " ".join(["Зарегистрирован новый пользователь", "@"+utils.mystr(user.username),
                        user.first_name, utils.mystr(user.last_name)])
        send_message(group.chat_id, text)
    context.user_data.clear()   
    return ConversationHandler.END


def setup_dispatcher_conv(dp: Dispatcher):
    conv_handler_reg = ConversationHandler( # здесь строится логика разговора
        # точка входа в разговор
        entry_points=[MessageHandler(Filters.text(REGISTRATION_START_BTN["reg_start"]) & FilterPrivateNoCommand, start_conversation, run_async=True)],      
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            APROVAL:[MessageHandler(Filters.text & FilterPrivateNoCommand, processing_aproval, run_async=True)],
            PHONE: [MessageHandler((Filters.contact | Filters.text) & FilterPrivateNoCommand, processing_phone, run_async=True)],
            FIO: [MessageHandler(Filters.text & FilterPrivateNoCommand, processing_fio, run_async=True)],
            ABOUT: [MessageHandler(Filters.text & FilterPrivateNoCommand, processing_about, run_async=True)],
            BIRHDAY: [MessageHandler(Filters.text & FilterPrivateNoCommand, processing_birhday, run_async=True)],
            EMAIL: [MessageHandler(Filters.text & FilterPrivateNoCommand, processing_email, run_async=True)],
            CITI: [MessageHandler(Filters.text & FilterPrivateNoCommand, processing_citi, run_async=True)],
            COMPANY: [MessageHandler(Filters.text & FilterPrivateNoCommand, processing_company, run_async=True)],
            JOB: [MessageHandler(Filters.text & FilterPrivateNoCommand, processing_job, run_async=True)],
            SITE: [MessageHandler(Filters.text & FilterPrivateNoCommand, processing_site, run_async=True)],
        },
        # точка выхода из разговора
        fallbacks=[CommandHandler('cancel', stop_conversation, Filters.chat_type.private, run_async=True),
                   CommandHandler('start', stop_conversation, Filters.chat_type.private, run_async=True)]
    )
    dp.add_handler(conv_handler_reg)
    