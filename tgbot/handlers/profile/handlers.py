
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import (
    Dispatcher, CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)
from tgbot.handlers.profile.messages import *
from tgbot.handlers.profile.answers import *
from tgbot.handlers.main.answers import START_MENU_FULL
from tgbot.models import User, tgGroups
from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.filters import FilterPrivateNoCommand
from tgbot.handlers.commands import command_start
from tgbot.handlers.utils import send_message
from tgbot.utils import extract_user_data_from_update, mystr

def prof_stop(update: Update, context: CallbackContext):
    # Заканчиваем разговор.
    command_start(update, context)
    return ConversationHandler.END

def start_manage_profile(update: Update, context: CallbackContext):
    userdata = extract_user_data_from_update(update)
    user = User.get_user_by_username_or_user_id(userdata["user_id"])
    context.user_data["user"] = user    
    update.message.reply_text(PROF_HELLO, reply_markup=make_keyboard(PROF_MENU,"usual",4))
    return "working"

def manage_fio(update: Update, context: CallbackContext):
    user = context.user_data["user"]
    fio = " ".join([mystr(user.last_name), mystr(user.first_name), mystr(user.sur_name)])
    update.message.reply_text(ASK_FIO.format(fio), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choos_action_fio"
  
# Обработчик фамилиии
def manage_fio_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:        
        user = context.user_data["user"]
        fio = update.message.text.split()
        len_fio = len(fio)
        if len_fio == 1:
            user.last_name = ""  # Фамилия
            user.first_name = fio[0] # Имя
            user.sur_name = ""   # Отчество
        elif len_fio == 2:
            user.first_name = fio[0] # Имя
            user.last_name = fio[1]  # Фамилия
            user.sur_name = ""   # Отчество
        elif len_fio > 2:
            user.last_name = fio[0]  # Фамилия
            user.first_name = fio[1] # Имя
            user.sur_name = fio[2]   # Отчество
        user.save()
        text = "ФИО изменены"
    else:
        text = "ФИО не изменены"
    update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4))
    return "working"
#-------------------------------------------  
# Обработчик телефона
def manage_phone(update: Update, context: CallbackContext):
    user = context.user_data["user"]
    update.message.reply_text(ASK_PHONE.format(user.telefon), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choos_action_phone"

def manage_phone_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:        
        user = context.user_data["user"]
        user.telefon = update.message.text
        user.save()
        text = "Телефон изменен"
    else:
        text = "Телефон не изменен"
    update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4))
    return "working"
#-------------------------------------------  
# Обработчик о себе
def manage_about(update: Update, context: CallbackContext):
    user = context.user_data["user"]
    update.message.reply_text(ASK_ABOUT.format(user.about), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choos_action_about"

def manage_about_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:        
        user = context.user_data["user"]
        user.telefon = update.message.text
        user.save()
        text = "Информация 'О себе' изменена"
    else:
        text = "Информация 'О себе' не изменена"
    update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4))
    return "working"
#-------------------------------------------  
# Обработчик Город
def manage_citi(update: Update, context: CallbackContext):
    user = context.user_data["user"]
    update.message.reply_text(ASK_CITI.format(user.citi), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choos_action_citi"

def manage_citi_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:        
        user = context.user_data["user"]
        user.citi = update.message.text
        user.save()
        text = "Город изменен"
    else:
        text = "Город не изменен"
    update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4))
    return "working"
#-------------------------------------------  
# Обработчик Компания
def manage_company(update: Update, context: CallbackContext):
    user = context.user_data["user"]
    update.message.reply_text(ASK_COMPANY.format(user.company), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choos_action_company"

def manage_company_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:        
        user = context.user_data["user"]
        user.company = update.message.text
        user.save()
        text = "Компания изменена"
    else:
        text = "Компания не изменена"
    update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4))
    return "working"

#-------------------------------------------  
# Обработчик Должность
def manage_job(update: Update, context: CallbackContext):
    user = context.user_data["user"]
    update.message.reply_text(ASK_JOB.format(user.job), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choos_action_job"

def manage_job_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:        
        user = context.user_data["user"]
        user.job = update.message.text
        user.save()
        text = "Должность изменена"
    else:
        text = "Должность не изменена"
    update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4))
    return "working"

#-------------------------------------------  
# Обработчик Сайт
def manage_site(update: Update, context: CallbackContext):
    user = context.user_data["user"]
    update.message.reply_text(ASK_SITE.format(user.site), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choos_action_site"

def manage_site_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:        
        user = context.user_data["user"]
        user.site = update.message.text
        user.save()
        text = "Сайт изменен"
    else:
        text = "Сайт не изменен"
    update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4))
    return "working"

def blank(update: Update, context: CallbackContext):
    pass

def back_to_start(update: Update, context: CallbackContext):
    # Заканчиваем разговор.
    command_start(update, context)
    return ConversationHandler.END

def setup_dispatcher_prof(dp: Dispatcher):
    # Диалог отправки сообщения
    conv_handler = ConversationHandler( 
        # точка входа в разговор
        entry_points=[MessageHandler(Filters.text(START_MENU_FULL["profile"]) & FilterPrivateNoCommand, start_manage_profile)],      
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            "working":[
                       MessageHandler(Filters.text(PROF_MENU["fio"]) & FilterPrivateNoCommand, manage_fio),
                       MessageHandler(Filters.text(PROF_MENU["telefon"]) & FilterPrivateNoCommand, manage_phone),
                       MessageHandler(Filters.text(PROF_MENU["about"]) & FilterPrivateNoCommand, manage_about),
                       MessageHandler(Filters.text(PROF_MENU["citi"]) & FilterPrivateNoCommand, manage_citi),
                       MessageHandler(Filters.text(PROF_MENU["company"]) & FilterPrivateNoCommand, manage_company),
                       MessageHandler(Filters.text(PROF_MENU["job"]) & FilterPrivateNoCommand, manage_job),
                       MessageHandler(Filters.text(PROF_MENU["site"]) & FilterPrivateNoCommand, manage_site),

                       MessageHandler(Filters.text(PROF_MENU["back"]) & FilterPrivateNoCommand, back_to_start),
                       MessageHandler(Filters.text & FilterPrivateNoCommand, blank)
                      ],
            "choos_action_fio":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_fio_action)],
            "choos_action_phone":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_phone_action)],
            "choos_action_about":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_about_action)],
            "choos_action_citi":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_citi_action)],
            "choos_action_company":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_company_action)],
            "choos_action_job":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_job_action)],
            "choos_action_site":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_site_action)],
        },
        # точка выхода из разговора
        fallbacks=[CommandHandler('cancel', prof_stop, Filters.chat_type.private)]
    )
    dp.add_handler(conv_handler)   