# -*- coding: utf-8 -*-

import datetime
import logging
import re
import telegram
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import ConversationHandler
from django.utils import timezone
from tgbot.handlers import static_text
from tgbot.models import User
from tgbot.utils import extract_user_data_from_update
from tgbot.handlers.keyboard_utils import keyboard_confirm_decline_broadcasting
from tgbot.handlers.utils import handler_logging
from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.registration.messages import REGISTRATION_START_MESSS
from tgbot.handlers.registration.answers import REGISTRATION_START_BTN
from tgbot.handlers.main.answers import get_start_menu
from tgbot.handlers.main.messages import get_start_mess

logger = logging.getLogger('default')
logger.info("Command handlers check!")

@handler_logging()
def command_start(update: Update, context: CallbackContext):
    context.user_data.clear()
    userdata = extract_user_data_from_update(update)
    user_id = userdata['user_id']
    user = User.get_user_by_username_or_user_id(user_id)
    if user != None:
        user.username = userdata["username"]
        user.save()
    if user == None:
        update.message.reply_text(REGISTRATION_START_MESSS, reply_markup=make_keyboard(REGISTRATION_START_BTN,"usual",2))
    else:
        reply_markup=get_start_menu(user)
        update.message.reply_text(get_start_mess(user), reply_markup=reply_markup)
    return ConversationHandler.END

def stats(update, context):
    """ Show help info about all secret admins commands """
    u = User.get_user(update, context)
    if not u.is_admin:
        return

    text = f"""
*Users*: {User.objects.count()}
*24h active*: {User.objects.filter(updated_at__gte=timezone.now() - datetime.timedelta(hours=24)).count()}
    """

    return update.message.reply_text(
        text, 
        parse_mode=telegram.ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )


def broadcast_command_with_message(update, context):
    """ Type /broadcast <some_text>. Then check your message in Markdown format and broadcast to users."""
    u = User.get_user(update, context)
    user_id = extract_user_data_from_update(update)['user_id']

    if not u.is_admin:
        text = static_text.broadcast_no_access
        markup = None

    else:
        text = f"{update.message.text.replace(f'{static_text.broadcast_command} ', '')}"
        markup = keyboard_confirm_decline_broadcasting()

    try:
        context.bot.send_message(
            text=text,
            chat_id=user_id,
            parse_mode=telegram.ParseMode.MARKDOWN,
            reply_markup=markup
        )
    except telegram.error.BadRequest as e:
        place_where_mistake_begins = re.findall(r"offset (\d{1,})$", str(e))
        text_error = static_text.error_with_markdown
        if len(place_where_mistake_begins):
            text_error += f"{static_text.specify_word_with_error}'{text[int(place_where_mistake_begins[0]):].split(' ')[0]}'"
        context.bot.send_message(
            text=text_error,
            chat_id=user_id
        )