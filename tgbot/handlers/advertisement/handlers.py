from telegram import (
    Update, 
    # InlineQueryResultArticle, InputTextMessageContent, ParseMode,
    ReplyKeyboardRemove,
    InputMediaPhoto, InputMediaVideo
)
from telegram.ext import (
    Dispatcher, CommandHandler,
    MessageHandler, CallbackQueryHandler,
    Filters, CallbackContext, ConversationHandler,
    # ChosenInlineResultHandler, InlineQueryHandler
)
import os
# from telegram.ext.filters import Filters as F
from django.conf import settings
from .messages import *
from .answers import *
from tgbot.models import tgGroups, User
from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.filters import FilterPrivateNoCommand
# from tgbot.handlers.utils import send_mess_by_tmplt
from tgbot.utils import (
    send_message, _get_all_file_id, 
    get_uniq_file_name, mystr, 
    send_media_group, randomword
)
from sheduler.models import MessageTemplates
from dtb.constants import MessageTemplatesCode
from tgbot.handlers.main.answers import get_start_menu
from tgbot.handlers.main.messages import get_start_mess
from advertisement.models import Advertisement, AdvertisementImage, AdvertisementVideo

# Возврат к главному меню
def stop_conversation(update: Update, context: CallbackContext):
    # Заканчиваем разговор.
    if update.message:
        user_id = update.message.from_user.id
        user = User.get_user_by_username_or_user_id(user_id)
        update.message.reply_text(
            text=get_start_mess(user), reply_markup=get_start_menu(user)
        )
    else:
        update.callback_query.answer()
        user_id = update.callback_query.from_user.id
        user = User.get_user_by_username_or_user_id(user_id)
        update.callback_query.edit_message_text(text=get_start_mess(user), reply_markup=get_start_menu(user))
    # send_message(user_id=user_id, text=GROUP_FINISH, reply_markup=make_keyboard(EMPTY,"usual",1))
    # send_message(user_id=user_id, text=get_start_mess(user), reply_markup=get_start_menu(user))
    adv = context.user_data.get("new_advertisement", None)
    if adv is not None:
        if not adv.create_done:
            adv.delete()
    return ConversationHandler.END

# Временная заглушка
def blank(update: Update, context: CallbackContext):
    update.message.reply_text(ASK_REENTER)

def echo_blank(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    reply_markup=make_keyboard(BACK,"inline",1)
    # update.message.reply_text(ECHO, reply_markup=reply_markup)
    query.edit_message_text(HELLO_TEXT, reply_markup=reply_markup)

def bad_callback_enter(update: Update, context: CallbackContext):
    update.message.reply_text(ASK_REENTER)

# Начало разговора
def start_conversation(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    query.edit_message_text(
        HELLO_TEXT,
        reply_markup=make_keyboard(BACK,"inline",1)
        )
    return "handle_text_advertisement"

def handle_text_advertisement(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    if Advertisement.get_advertisements_by_user_in_time(user)\
        .filter(create_done=True).count() >= MAX_ADVERTISEMENTS_COUNT and\
        not user.is_admin:
        send_message(
            user_id,
            "Превышено максимальное количество рекламных соощений."
            )
        return stop_conversation(update, context)
    if len(update.message.text) > 900:
        send_message(
            user_id,
            "Превышена максимальная длина рекламного сообщения. "\
                "Сообщение должно быть длиной не более 900 символов."
            )
        return
    adv = Advertisement.objects.create(essence=update.message.text, author=user)
    context.user_data["new_advertisement"] = adv
    send_message(
        user_id,
        ADD_ADVERTISEMENT_FILE,
        reply_markup=make_keyboard(BACK,"inline",1, header_buttons=SAVE)
        )
    return "handle_advertisement_files"

def processing_file_txt(update: Update, context: CallbackContext):
    send_message(
        update.message.from_user.id,
        'Пришлите видео/фотографию или нажмите "Сохранить"',
        reply_markup=make_keyboard(BACK,"inline",1, header_buttons=SAVE)

    )
    return

def processing_photo(update: Update, context: CallbackContext):
    adv = context.user_data["new_advertisement"]
    foto = update.message.photo[-1]
    if adv.images.count() >= MAX_IMAGES_COUNT:
        video_txt = "Пришлите видео или нажмите" if adv.videos.count() < 1 else "Нажмите"
        send_message(
            update.message.from_user.id,
            f'Превышено максимальное количество прикрепленных изображений. {video_txt} "Сохранить"',
            reply_markup=make_keyboard(BACK,"inline",1, header_buttons=SAVE)
        )
        return
    # filename_orig = _get_all_file_id(update.message)
    foto_id = foto.file_id
    filename_orig = str(adv.id) + "-" + randomword(8) + ".jpg"
    filename_lst = filename_orig.split(".")
    newFile = context.bot.get_file(foto_id)
    if not os.path.exists(settings.BASE_DIR / "media/advertisement_files"):
        os.makedirs(settings.BASE_DIR / "media/advertisement_files")
    filename = get_uniq_file_name(settings.BASE_DIR / "media/advertisement_files",filename_lst[0],filename_lst[1])
    newFile.download(settings.BASE_DIR / ("media/advertisement_files/"+filename))
    AdvertisementImage.objects.create(
        adv=adv,
        image="advertisement_files/"+filename,
        image_id=foto_id
    )
    send_message(
        update.message.from_user.id,
        "Изображение успешно загружено",
        reply_markup=make_keyboard(BACK,"inline",1, header_buttons=SAVE)
    )
    return

def processing_video(update: Update, context: CallbackContext):
    adv = context.user_data["new_advertisement"]
    if adv.videos.count() >= MAX_VIDEOS_COUNT:
        video_txt = "Пришлите изображение или нажмите" if adv.images.count() < 1 else "Нажмите"
        send_message(
            update.message.from_user.id,
            f'Превышено максимальное количество прикрепленных видеофайлов. {video_txt} "Сохранить"',
            reply_markup=make_keyboard(BACK,"inline",1, header_buttons=SAVE)
        )
        return
    if update.message.video.duration > MAX_VIDEO_DURATION:
        video_txt = "Пришлите изображение, видео или нажмите" if adv.images.count() < 1 else "Пришлите видео или нажмите"
        send_message(
            update.message.from_user.id,
            f'Превышена максимальная длительность прикрепленного видеофайла. {video_txt} "Сохранить"',
            reply_markup=make_keyboard(BACK,"inline",1, header_buttons=SAVE)
        )
        return
    video_id, filename_orig = _get_all_file_id(update.message)
    if not os.path.exists(settings.BASE_DIR / "media/advertisement_files"):
        os.makedirs(settings.BASE_DIR / "media/advertisement_files")
    filename_orig = str(adv.id) + "-" + filename_orig
    filename_lst = filename_orig.split(".")
    newFile = context.bot.get_file(video_id)
    filename = get_uniq_file_name(
        settings.BASE_DIR / "media/advertisement_files",filename_lst[0],filename_lst[1]
    )
    newFile.download(settings.BASE_DIR / ("media/advertisement_files/"+filename))
    AdvertisementVideo.objects.create(
        adv=adv,
        video="advertisement_files/"+filename,
        video_id=video_id
    )
    send_message(
        update.message.from_user.id,
        "Видеофайл успешно загружен.",
        reply_markup=make_keyboard(BACK,"inline",1, header_buttons=SAVE)
    )
    return

def save_advertisement(update: Update, context: CallbackContext):
    adv = context.user_data["new_advertisement"]
    adv.create_done = True
    adv.save()
    send_message(
        update.callback_query.from_user.id,
        ADMERTISEMENT_CREATED,
        reply_markup=ReplyKeyboardRemove()
    )
    group = tgGroups.get_group_by_name("Администраторы")
    if (group == None) or (group.chat_id == 0):
        update.callback_query.reply_text(NO_ADMIN_GROUP)
    else:
        bn = {f"manage_new_adv-{adv.id}":"Просмотреть"}
        reply_markup =  make_keyboard(bn,"inline",1)
        text =f"Зарегистрировано новое рекламное сообщение от пользователя "\
            f"@{mystr(adv.author.username)} {adv.author.first_name} {mystr(adv.author.last_name)}"
        send_message(group.chat_id, text, reply_markup =  reply_markup)
    return stop_conversation(update, context)

def manage_new_adv(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    if (not user) or (not user.is_admin):
        text ="{}, у Вас нет прав администратора".format(query.from_user.full_name)
        send_message(update.callback_query.message.chat_id, text)
        return
    query_data = query.data.split("-")
    new_adv_id = int(query_data[1])
    new_adv = Advertisement.objects.get(id=new_adv_id)
    manage_usr_btn = {f"confirm_adv-{new_adv_id}":"Подтвердить",
                      f"unconfirm_adv-{new_adv_id}":"Отклонить",
                    #   f"back_from_user_confirm-{new_user_id}":"Отмена обработки",
                     }
    reply_markup=make_keyboard(manage_usr_btn,"inline",1)
    media = list()
    for video in new_adv.videos.all():
        media.append(InputMediaVideo(media=video.video_id))
    for image in new_adv.images.all():
        media.append(InputMediaPhoto(image.image_id))
    if len(media) > 0:
        media[0].caption = new_adv.essence
        send_media_group(
            user_id=user_id, 
            media=media, 
            )
        send_message(
            user_id=user_id,
            text="Что делать с рекламным сообщением?",
            reply_markup=reply_markup
        )
    else:
        send_message(
            user_id=user_id,
            text=new_adv.essence,
            reply_markup=reply_markup
        )

def confirm_adv(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query_data = query.data.split("-")
    adv_id = int(query_data[1])
    new_adv = Advertisement.objects.get(id=adv_id)
    new_adv.admin_aprooved = True
    new_adv.save()
    adv_user = new_adv.author
    # user_id = query.from_user.id
    # user = User.get_user_by_username_or_user_id(user_id)

    text = MessageTemplates.objects.get(code=MessageTemplatesCode.ADVERTISEMENT_APROOVED)
    send_message(adv_user.user_id, text.text)
    query.delete_message()


    groups = tgGroups.objects.filter(send_advertisements=True)
    if groups.count() == 0:
        update.message.reply_text(NO_SEND_ADVERTISEMENT_GROUPS)
    else:
        media = list()
        for video in new_adv.videos.all():
            media.append(InputMediaVideo(media=video.video_id))
        for image in new_adv.images.all():
            media.append(InputMediaPhoto(image.image_id))
        for group in groups:
            if len(media) > 0:
                media[0].caption = new_adv.essence
                send_media_group(
                    group.chat_id, 
                    media=media, 
                    )
            else:
                send_message(
                    group.chat_id,
                    text=new_adv.essence,
                )

def unconfirm_adv(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query_data = query.data.split("-")
    adv_id = int(query_data[1])
    new_adv = Advertisement.objects.get(id=adv_id)
    adv_user_user_id = new_adv.author.user_id
    new_adv.delete()
    text = MessageTemplates.objects.get(code=MessageTemplatesCode.ADVERTISEMENT_NOT_APROOVED)
    send_message(adv_user_user_id, text.text)
    query.delete_message()


def setup_dispatcher_conv(dp: Dispatcher):
    # Диалог отправки сообщения
    conv_handler = ConversationHandler( 
        # точка входа в разговор      
        entry_points=[CallbackQueryHandler(start_conversation, pattern="^affiliate$"),
                    # CallbackQueryHandler(start_conversation, pattern="^find_groups$"),
                      ],      
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            "handle_text_advertisement":[
                       MessageHandler(Filters.text & FilterPrivateNoCommand, handle_text_advertisement)
                      ],
       "handle_advertisement_files":[
                        CallbackQueryHandler(save_advertisement, pattern="^save$"),
                       MessageHandler(Filters.photo & FilterPrivateNoCommand, processing_photo),
                       MessageHandler(Filters.video & FilterPrivateNoCommand, processing_video),
                     MessageHandler(Filters.text & FilterPrivateNoCommand, processing_file_txt)
                      ],
        },
        # точка выхода из разговора
        fallbacks=[CommandHandler('cancel', stop_conversation, Filters.chat_type.private),
                   CommandHandler('start', stop_conversation, Filters.chat_type.private),
                   CallbackQueryHandler(stop_conversation, pattern="^back-from-advertisement$")]
    )
    dp.add_handler(conv_handler)
    dp.add_handler(CallbackQueryHandler(manage_new_adv, pattern="^manage_new_adv-"))
    dp.add_handler(CallbackQueryHandler(confirm_adv, pattern="^confirm_adv-"))
    dp.add_handler(CallbackQueryHandler(unconfirm_adv, pattern="^unconfirm_adv-"))

    # dp.add_handler(InlineQueryHandler(manage_find, pattern="^chats")),
    # dp.add_handler(ChosenInlineResultHandler(show_group))
    # dp.add_handler(
    #     MessageHandler(
    #         F.regex(r"Выбрана группа") & FilterPrivateNoCommand,
    #         handle_chose_group
    #         )
    # )
    # dp.add_handler(CallbackQueryHandler(stop_conversation, pattern="^back-from-advertisement$"),)
    # dp.add_handler(CallbackQueryHandler(echo_blank, pattern="^affiliate$"),)




