import logging
import telegram
import os
from functools import wraps
# from dtb.settings import ENABLE_DECORATOR_LOGGING, TELEGRAM_TOKEN
from django.utils import timezone
from tgbot.models import UserActionLog, User, Config, tgGroups
from tgbot.utils import extract_user_data_from_update, _get_file_id, send_message, send_photo, send_video, send_document
# from telegram import MessageEntity
from django.conf import settings

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
        return handler if settings.ENABLE_DECORATOR_LOGGING else func
    return decor


# def send_message(user_id, text, parse_mode=telegram.ParseMode.HTML, reply_markup=None, reply_to_message_id=None,
#                  disable_web_page_preview=True, entities=None, api_kwargs = None, tg_token=TELEGRAM_TOKEN):
#     bot = telegram.Bot(tg_token)
#     try:
#         if entities:
#             entities = [
#                 MessageEntity(type=entity['type'],
#                               offset=entity['offset'],
#                               length=entity['length']
#                 )
#                 for entity in entities
#             ]

#         m = bot.send_message(
#             chat_id=user_id,
#             text=text,
#             parse_mode=parse_mode,
#             reply_markup=reply_markup,
#             reply_to_message_id=reply_to_message_id,
#             disable_web_page_preview=disable_web_page_preview,
#             entities=entities,
#             api_kwargs = api_kwargs
#         )
#     except telegram.error.Unauthorized:
#         print(f"Can't send message to {user_id}. Reason: Bot was stopped.")
#         #User.objects.filter(user_id=user_id).update(is_blocked_bot=True)
#         success = f"Can't send message to {user_id}. Reason: Bot was stopped."
#     except Exception as e:
#         print(f"Can't send message to {user_id}. Reason: {e}")
#         success = e
#     else:
#         success = m
#         #User.objects.filter(user_id=user_id).update(is_blocked_bot=False)
#     return success

# def send_photo(user_id, photo, caption=None, disable_notification=None, reply_to_message_id=None, 
#                reply_markup=None, timeout=20, parse_mode=telegram.ParseMode.HTML, api_kwargs=None, allow_sending_without_reply=None, 
#                caption_entities=None, filename=None, protect_content=None, tg_token=TELEGRAM_TOKEN):

#     text = None
#     if caption and len(caption)>1023:
#         text = caption
#         reply_markup_txt = reply_markup
#         caption = None
#         reply_markup = None

#     bot = telegram.Bot(tg_token)
#     try:
#         m = bot.send_photo(
#             chat_id=user_id,
#             photo=photo,
#             caption=caption, 
#             disable_notification=disable_notification, 
#             reply_to_message_id=reply_to_message_id, 
#             reply_markup=reply_markup, 
#             timeout=timeout, 
#             parse_mode=parse_mode, 
#             api_kwargs=api_kwargs, 
#             allow_sending_without_reply=allow_sending_without_reply, 
#             caption_entities=caption_entities, 
#             filename=filename, 
#             protect_content=protect_content
#         )
#         if text:
#             send_message(user_id=user_id, text=text, reply_markup=reply_markup_txt)
#     except telegram.error.Unauthorized:
#         print(f"Can't send message to {user_id}. Reason: Bot was stopped.")
#         #User.objects.filter(user_id=user_id).update(is_blocked_bot=True)
#         success = f"Can't send message to {user_id}. Reason: Bot was stopped."
#     except Exception as e:
#         print(f"Can't send message to {user_id}. Reason: {e}")
#         success = e
#     else:
#         success = m
#         #User.objects.filter(user_id=user_id).update(is_blocked_bot=False)
#     return success

# def send_document(user_id, document, filename=None, caption=None, disable_notification=None, reply_to_message_id=None, 
#             reply_markup=None, timeout=20, parse_mode=telegram.ParseMode.HTML, thumb=None, api_kwargs=None, 
#             disable_content_type_detection=None, allow_sending_without_reply=None, caption_entities=None, 
#             protect_content=None, tg_token=TELEGRAM_TOKEN):

#     text = None
#     if caption and len(caption)>1023:
#         text = caption
#         reply_markup_txt = reply_markup
#         caption = None
#         reply_markup = None
#     bot = telegram.Bot(tg_token)
#     try:

#         m = bot.send_document(
#             chat_id=user_id,
#             document=document,
#             filename=filename, 
#             caption=caption, 
#             disable_notification=disable_notification, 
#             reply_to_message_id=reply_to_message_id, 
#             reply_markup=reply_markup, 
#             timeout=timeout, 
#             parse_mode=parse_mode, 
#             thumb=thumb, 
#             api_kwargs=api_kwargs, 
#             disable_content_type_detection=disable_content_type_detection, 
#             allow_sending_without_reply=allow_sending_without_reply, 
#             caption_entities=caption_entities, 
#             protect_content=protect_content
#         )
#         if text:
#             send_message(user_id=user_id, text=text, reply_markup=reply_markup_txt)
#     except telegram.error.Unauthorized:
#         print(f"Can't send message to {user_id}. Reason: Bot was stopped.")
#         #User.objects.filter(user_id=user_id).update(is_blocked_bot=True)
#         success = f"Can't send message to {user_id}. Reason: Bot was stopped."
#     except Exception as e:
#         print(f"Can't send message to {user_id}. Reason: {e}")
#         success = e
#     else:
#         success = m
#     return success

# def send_video(user_id, video, duration=None, caption=None, disable_notification=None, 
#                reply_to_message_id=None, reply_markup=None, timeout=20, width=None, height=None, 
#                parse_mode=telegram.ParseMode.HTML, supports_streaming=None, thumb=None, api_kwargs=None, 
#                allow_sending_without_reply=None, caption_entities=None, filename=None, 
#                protect_content=None, tg_token=TELEGRAM_TOKEN):

#     text = None
#     if caption and len(caption)>1023:
#         text = caption
#         reply_markup_txt = reply_markup
#         caption = None
#         reply_markup = None


#     bot = telegram.Bot(tg_token)
#     try:
#         m = bot.send_video(
#             chat_id=user_id,
#             video=video, 
#             duration=duration, 
#             caption=caption, 
#             disable_notification=disable_notification, 
#             reply_to_message_id=reply_to_message_id, 
#             reply_markup=reply_markup, 
#             timeout=timeout, 
#             width=width, 
#             height=height, 
#             parse_mode=parse_mode, 
#             supports_streaming=supports_streaming, 
#             thumb=thumb, 
#             api_kwargs=api_kwargs, 
#             allow_sending_without_reply=allow_sending_without_reply, 
#             caption_entities=caption_entities, 
#             filename=filename, 
#             protect_content=protect_content
#         )
#         if text:
#             send_message(user_id=user_id, text=text, reply_markup=reply_markup_txt)
#     except telegram.error.Unauthorized:
#         print(f"Can't send message to {user_id}. Reason: Bot was stopped.")
#         #User.objects.filter(user_id=user_id).update(is_blocked_bot=True)
#         success = f"Can't send message to {user_id}. Reason: Bot was stopped."
#     except Exception as e:
#         print(f"Can't send message to {user_id}. Reason: {e}")
#         success = e
#     else:
#         success = m
#         #User.objects.filter(user_id=user_id).update(is_blocked_bot=False)
#     return success

def get_no_foto_id():
    """
    Получает ИД фотографии заглушки, для тех у кого нет фото
    """
    config_set = Config.objects.filter(param_name = "no_foto_id")
    bot = telegram.Bot(settings.TELEGRAM_TOKEN)
    photo = settings.BASE_DIR / 'media/no_foto.jpg'
    if len(config_set) == 0:
        message = bot.send_photo(settings.TRASH_GROUP, open(photo, 'rb'), caption="no_foto")
        foto_id, _ = _get_file_id(message)
        config_no_foto_id = Config(param_name = "no_foto_id", param_val = foto_id)
        config_no_foto_id.save()
    else:
        config_no_foto_id = config_set[0]

    if wrong_file_id(config_no_foto_id.param_val):
        message = bot.send_photo(settings.TRASH_GROUP, open(photo, 'rb'), caption="no_foto")
        foto_id, _ = _get_file_id(message)
        config_no_foto_id.param_val = foto_id
        config_no_foto_id.save()
    
    return config_no_foto_id.param_val


def fill_file_id(obj, file_field: str, text: str = ""):
    """
    заполняет у объекта поле с телеграм ид файоа
    obj - оъект, file_field - имя поля с файлом
    имя поля с ид должно быть file_field + '_id'
    """

    file = getattr(obj, file_field)
    if not file:
        return
    if os.path.exists(file.path):
        file_ext = file.name.split(".")[-1]

        if file_ext in ["jpg","jpeg","png","gif","tif","tiff","bmp"]:
            mess = send_photo(settings.TRASH_GROUP, open(file.path, 'rb'), caption = text)
                    
        elif file_ext in ["mp4","avi","mov","mpeg"]:
            mess = send_video(settings.TRASH_GROUP, open(file.path, 'rb'), caption = text)
        else:
            mess = send_document(settings.TRASH_GROUP, open(file.path, 'rb'), caption = text)

        file_id, _ = _get_file_id(mess)
        setattr(obj, file_field + "_id", file_id)
        obj.save() 

def wrong_file_id(file_id: str, tg_token=settings.TELEGRAM_TOKEN):
    bot = telegram.Bot(tg_token)
    try:
        file = bot.get_file(file_id)
        return False
    except:
        return True

def  send_mess_by_tmplt(user_id, mess_template, reply_markup = None, head_text = None, fut_text = None):
    """
    Отправка сообщения по шаблону. Шаблоном может быть любой объект с полями text, file, file_id
    файл и текст пересылаются пользователь/группе с номером user_id и прикрепляется клавиатура
    """
    success = False
    mess_text = str(mess_template.text)
    if fut_text:
        mess_text += fut_text
    if head_text:
        mess_text = head_text + mess_text
        

    if not mess_template.file:
        success = send_message(user_id = user_id, text = mess_text, disable_web_page_preview=True, reply_markup = reply_markup)
    elif mess_template.file:
        if not mess_template.file_id:
            fill_file_id(mess_template, "file", text = "send_mess_by_tmplt")
        if mess_template.file.name[-3:] in ["jpeg","jpg","bmp","png"]:# в сообщении картинка
            if os.path.exists(mess_template.file.path):
                success = send_photo(
                    user_id,
                    mess_template.file_id,
                    parse_mode=telegram.ParseMode.HTML,
                    caption=mess_text,
                    reply_markup=reply_markup
                )
            else:
                success = send_message(
                    user_id=user_id,
                    text=mess_text,
                    parse_mode=telegram.ParseMode.HTML,
                    disable_web_page_preview=True,
                    reply_markup=reply_markup
                    )
        else:
            if os.path.exists(mess_template.file.path):
                success = send_document(user_id, mess_template.file_id)
            success = send_message(user_id = user_id, text = mess_text,
                                disable_web_page_preview=True, reply_markup = reply_markup)
    return success