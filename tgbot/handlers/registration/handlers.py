import logging
from this import d
import telegram
import datetime
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import (
    Dispatcher, CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)
from telegram import KeyboardButton, ReplyKeyboardMarkup
from tgbot.handlers.registration.messages import *
from tgbot.handlers.registration.answers import *
from tgbot.models import User
from tgbot.handlers.keyboard import make_keyboard
from tgbot import utils

# Шаги диалога
APROVAL,PHONE,FIO,BIRHDAY,EMAIL = range(5)

def registration_stop(update: Update, context: CallbackContext):
    # Заканчиваем разговор.
    context.user_data.clear()
    keyboard = make_keyboard(START,"usual",1)
    update.message.reply_text(REGISTRATION_CANCELED, reply_markup=keyboard)
    return ConversationHandler.END

def registration_start(update: Update, context: CallbackContext):
    context.user_data.clear()
    userdata = utils.extract_user_data_from_update(update)
    context.user_data.update(userdata)
    context.user_data["created_at"] = datetime.datetime.now()
    context.user_data["is_blocked_bot"] = True
    context.user_data["comment"] = "Ожидает подтверждения регистрации"
    update.message.reply_text(WELCOME, reply_markup=make_keyboard(APPROVAL_ANSWERS,"usual",2))


def processing_aproval(update: Update, context: CallbackContext):
    if update.message.text == APPROVAL_ANSWERS["yes"]: # В этом поле хранится согласие
        tg_keys = []
        tg_keys.append(KeyboardButton(text="Отправить телефонный номер", request_contact=True))
        tg_keys.append(KeyboardButton(text=CANCEL["cancel"]))
        keyboard = ReplyKeyboardMarkup([tg_keys], resize_keyboard=True)        
        update.message.reply_text(ASK_PHONE, reply_markup=keyboard)
        return PHONE
    elif update.message.text == APPROVAL_ANSWERS["no"]: # В этом поле хранится отказ
        registration_stop(update, context)
        return ConversationHandler.END
    else:
        update.message.reply_text(ASK_REENTER)

def processing_phone(update: Update, context: CallbackContext):
    if update.message.contact != None: # Был прислан контакт        
        # Запоминаем телефон
        context.user_data["telefon"] = update.message.contact.phone_number
        # Если пользователь новый проверяем есть ли у него в Телеграмм имя пользователя
        if update.message.from_user.username == None:
             update.message.reply_text(USERNAME_NEEDED)
        keyboard = make_keyboard(CANCEL,"usual",1)
        update.message.reply_text(ASK_FIO, reply_markup=keyboard)
        return FIO
    elif update.message.text == CANCEL["cancel"]: # Отказались отправить телефон
        registration_stop(update, context)
        return ConversationHandler.END
    else:
        update.message.reply_text(ASK_REENTER)

def processing_fio(update: Update, context: CallbackContext):
    if update.message.text == CANCEL["cancel"]:
        registration_stop(update, context)
        return ConversationHandler.END
    else:
        fio = update.message.text.split()
        len_fio = len(fio)
        if len_fio == 1:
            context.user_data["first_name"] = fio[0] # Имя
        elif len_fio == 2:
            context.user_data["first_name"] = fio[0] # Имя
            context.user_data["last_name"] = fio[1]  # Фамилия
        elif len_fio > 2:
            context.user_data["last_name"] = fio[0]  # Фамилия
            context.user_data["first_name"] = fio[1] # Имя
            context.user_data["sur_name"] = fio[2]   # Отчество
        
        keyboard = make_keyboard(CANCEL_SKIP,"usual",2)
        update.message.reply_text(ASK_BIRHDAY, reply_markup=keyboard)
        return BIRHDAY

def processing_birhday(update: Update, context: CallbackContext):
    date = utils.is_date(update.message.text)

    if update.message.text == CANCEL_SKIP["cancel"]: # решили прервать регистрацию
       registration_stop(update, context)
       return ConversationHandler.END
    elif update.message.text == CANCEL_SKIP["skip"]:
        keyboard = make_keyboard(CANCEL_SKIP,"usual",2)
        update.message.reply_text(ASK_EMAIL, reply_markup=keyboard)
        return EMAIL
    elif not(date): # ввели неверную дату
        update.message.reply_text(BAD_DATE)
        return    
    else: # ввели верный дату
        context.user_data["date_of_birth"] = date
        keyboard = make_keyboard(CANCEL_SKIP,"usual",2)
        update.message.reply_text(ASK_EMAIL, reply_markup=keyboard)
        return EMAIL

def processing_email(update: Update, context: CallbackContext):
    email = utils.is_email(update.message.text)

    if update.message.text == CANCEL_SKIP["cancel"]: # решили прервать регистрацию
       registration_stop(update, context)
       return ConversationHandler.END
    elif update.message.text == CANCEL_SKIP["skip"]:
        keyboard = make_keyboard(CANCEL_SKIP,"usual",2)
        update.message.reply_text(ASK_EMAIL, reply_markup=keyboard)
        return EMAIL
    elif not(email): # ввели неверную email
        update.message.reply_text(BAD_EMAIL)
        return    
    else: # ввели верный email
        context.user_data["email"] = email
        keyboard = make_keyboard(CANCEL_SKIP,"usual",2)
        update.message.reply_text(ASK_EMAIL, reply_markup=keyboard)
        return EMAIL

def setup_dispatcher_reg(dp: Dispatcher):
    conv_handler = ConversationHandler( # здесь строится логика разговора
        # точка входа в разговор
        entry_points=[MessageHandler(Filters.text, processing_aproval)],
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            PHONE: [MessageHandler(Filters.contact | Filters.text, processing_phone)],
            FIO: [MessageHandler(Filters.text, processing_fio)],
            BIRHDAY: [MessageHandler(Filters.text, processing_birhday)],
            EMAIL: [MessageHandler(Filters.text, processing_email)],

        },
        # точка выхода из разговора
        fallbacks=[CommandHandler('cancel', registration_stop)],
    )
    dp.add_handler(conv_handler)
    pass