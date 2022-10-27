# -*- coding: utf-8 -*-

import datetime
import logging
import re
import telegram
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import ConversationHandler
from tgbot.my_telegram import ConversationHandler as ConversationHandler_my
from django.utils import timezone
from tgbot.models import User, NewUser
from tgbot.utils import extract_user_data_from_update
from tgbot.handlers.utils import handler_logging
from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.registration.messages import REGISTRATION_START_MESSS
from tgbot.handlers.registration.answers import REGISTRATION_START_BTN
from tgbot.handlers.main.answers import EMPTY, get_start_menu
from tgbot.handlers.main.messages import get_start_mess
from sheduler.tasks import restarts_tasks

logger = logging.getLogger('default')
logger.info("Command handlers check!")

@handler_logging()
def command_start(update: Update, context: CallbackContext):
    update.message.reply_text("Начало работы", reply_markup=make_keyboard(EMPTY,"usual",2))
    context.user_data.clear()
    userdata = extract_user_data_from_update(update)
    context.user_data.update(userdata)
    user_id = userdata['user_id']

    user = User.get_user_by_username_or_user_id(user_id)
    if user != None:
        if user.username != userdata.get("username"):
            user.username = userdata.get("username")
            user.save()
    
    if user == None:
        new_user = NewUser.objects.filter(user_id = user_id).first()
        if not new_user:
            new_user = NewUser(user_id = user_id)
        new_user.username = userdata.get("username")
        new_user.first_name = userdata.get("first_name")
        new_user.last_name = userdata.get("last_name")
        new_user.language_code = userdata.get("language_code")

        # Определение рекомендателя
        if not new_user.deep_link:
            new_user.deep_link = "00000000"
            if context is not None and context.args is not None and len(context.args) > 0:
                payload = context.args[0]
                if str(payload).strip() != str(user_id).strip():  # нельзя быть рекомендателем самому себе
                    new_user.deep_link = payload    
        new_user.save()
        update.message.reply_text(REGISTRATION_START_MESSS, reply_markup=make_keyboard(REGISTRATION_START_BTN,"usual",2))
    else:
        reply_markup=get_start_menu(user)
        update.message.reply_text(get_start_mess(user), reply_markup=reply_markup, 
                                  parse_mode=telegram.ParseMode.HTML)
    
    clear_conversation(context.dispatcher.handlers[0], user_id)
    return ConversationHandler.END

def clear_conversation(handlers, user_id):
    for handler in handlers:
        h_type = type(handler)
        if h_type == ConversationHandler or h_type == ConversationHandler_my:
            handler.conversations.pop((user_id,user_id),1)
            g=1
        #context._dispatcher.handlers[0][11].conversations

@handler_logging()
def command_restart_tasks(update: Update, context: CallbackContext):
    userdata = extract_user_data_from_update(update)
    user_id = userdata['user_id']
    user = User.get_user_by_username_or_user_id(user_id)
    if (user != None) and user.is_admin:
        restarts_tasks(context.job_queue)
        update.message.reply_text("Задания перезапущены")
    else:
        update.message.reply_text("Недостаточно прав")

    return ConversationHandler.END


