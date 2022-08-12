import logging
import telegram
from typing import Optional
from functools import wraps
from dtb.settings import ENABLE_DECORATOR_LOGGING, TELEGRAM_TOKEN
from django.utils import timezone
from tgbot.models import UserActionLog, User, tgGroups
from tgbot.utils import extract_user_data_from_update
from telegram import MessageEntity


logger = logging.getLogger('default')


def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=telegram.ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func


def handler_logging(action_name=None):
    """ Turn on this decorator via ENABLE_DECORATOR_LOGGING variable in dtb.settings """
    def decor(func):
        def handler(update, context, *args, **kwargs):
            user_id = extract_user_data_from_update(update)['user_id']
            #user, _ = User.get_user_and_created(update, context)
            user = User.get_user_by_username_or_user_id(user_id)
            action = f"{func.__module__}.{func.__name__}" if not action_name else action_name
            try:
                text = update.message['text'] if update.message else ''
            except AttributeError:
                text = ''
            if user != None:
                UserActionLog.objects.create(user_id=user.user_id, action=action, text=text, created_at=timezone.now())
            return func(update, context, *args, **kwargs)
        return handler if ENABLE_DECORATOR_LOGGING else func
    return decor


def send_message(user_id, text, parse_mode=None, reply_markup=None, reply_to_message_id=None,
                 disable_web_page_preview=None, entities=None, tg_token=TELEGRAM_TOKEN):
    bot = telegram.Bot(tg_token)
    try:
        if entities:
            entities = [
                MessageEntity(type=entity['type'],
                              offset=entity['offset'],
                              length=entity['length']
                )
                for entity in entities
            ]

        m = bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            reply_to_message_id=reply_to_message_id,
            disable_web_page_preview=disable_web_page_preview,
            entities=entities,
        )
    except telegram.error.Unauthorized:
        print(f"Can't send message to {user_id}. Reason: Bot was stopped.")
        #User.objects.filter(user_id=user_id).update(is_blocked_bot=True)
        success = False
    except Exception as e:
        print(f"Can't send message to {user_id}. Reason: {e}")
        success = False
    else:
        success = True
        #User.objects.filter(user_id=user_id).update(is_blocked_bot=False)
    return success

def send_photo(user_id, photo, caption=None, disable_notification=None, reply_to_message_id=None, 
               reply_markup=None, timeout=20, parse_mode=None, api_kwargs=None, allow_sending_without_reply=None, 
               caption_entities=None, filename=None, protect_content=None, tg_token=TELEGRAM_TOKEN):

    bot = telegram.Bot(tg_token)
    try:
        m = bot.send_photo(
            chat_id=user_id,
            photo=photo,
            caption=caption, 
            disable_notification=disable_notification, 
            reply_to_message_id=reply_to_message_id, 
            reply_markup=reply_markup, 
            timeout=timeout, 
            parse_mode=parse_mode, 
            api_kwargs=api_kwargs, 
            allow_sending_without_reply=allow_sending_without_reply, 
            caption_entities=caption_entities, 
            filename=filename, 
            protect_content=protect_content
        )
    except telegram.error.Unauthorized:
        print(f"Can't send message to {user_id}. Reason: Bot was stopped.")
        #User.objects.filter(user_id=user_id).update(is_blocked_bot=True)
        success = False
    except Exception as e:
        print(f"Can't send message to {user_id}. Reason: {e}")
        success = False
    else:
        success = True
        #User.objects.filter(user_id=user_id).update(is_blocked_bot=False)
    return success

def send_document(user_id, document, filename=None, caption=None, disable_notification=None, reply_to_message_id=None, 
            reply_markup=None, timeout=20, parse_mode=None, thumb=None, api_kwargs=None, 
            disable_content_type_detection=None, allow_sending_without_reply=None, caption_entities=None, 
            protect_content=None, tg_token=TELEGRAM_TOKEN):


    bot = telegram.Bot(tg_token)
    try:
        m = bot.send_document(
            chat_id=user_id,
            document=document,
            filename=filename, 
            caption=caption, 
            disable_notification=disable_notification, 
            reply_to_message_id=reply_to_message_id, 
            reply_markup=reply_markup, 
            timeout=timeout, 
            parse_mode=parse_mode, 
            thumb=thumb, 
            api_kwargs=api_kwargs, 
            disable_content_type_detection=disable_content_type_detection, 
            allow_sending_without_reply=allow_sending_without_reply, 
            caption_entities=caption_entities, 
            protect_content=protect_content
        )
    except telegram.error.Unauthorized:
        print(f"Can't send message to {user_id}. Reason: Bot was stopped.")
        #User.objects.filter(user_id=user_id).update(is_blocked_bot=True)
        success = False
    except Exception as e:
        print(f"Can't send message to {user_id}. Reason: {e}")
        success = False
    else:
        success = True
        #User.objects.filter(user_id=user_id).update(is_blocked_bot=False)
    return success
