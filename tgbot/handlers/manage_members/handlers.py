import os
from telegram import (
    InlineQueryResultArticle,  
    ParseMode, InputTextMessageContent, Update)
from telegram.ext import (
    Dispatcher, CommandHandler,
    MessageHandler, CallbackQueryHandler,
    Filters, ChosenInlineResultHandler,
    InlineQueryHandler, CallbackContext
)
from tgbot.my_telegram import ConversationHandler
from django.conf import settings
from .messages import *
from .answers import *
import tgbot.models as mymodels
from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.filters import FilterPrivateNoCommand
from tgbot.utils import send_message, send_photo, fill_file_id, send_contact
from tgbot.handlers.utils import get_no_foto_id
from tgbot.handlers.main.answers import get_start_menu
from tgbot.handlers.main.messages import get_start_mess

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
    context.user_data["search_started"] = False
    send_message(user_id=user_id, text=FIND_FINISH, reply_markup=make_keyboard(EMPTY,"usual",1))
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
    query.edit_message_text(text=HELLO_MESS_2, reply_markup=make_keyboard(FIND,"inline",1,None,BACK))
    return "working"

# Обработчик поиска
def manage_find(update: Update, context: CallbackContext):
    query = update.inline_query.query.strip()
    if len(query) < 3:
        return
    users_set = mymodels.User.find_users_by_keywords(query).exclude(is_blocked_bot=True).exclude(is_banned=True)
    users_set = users_set.exclude(user_id = update.inline_query.from_user.id)
    results = []
    for user in users_set:
        user_res_str = InlineQueryResultArticle(
            id=str(user.user_id),
            title=str(user),
            input_message_content = InputTextMessageContent("Выбран пользователь"),
            description = user.about,
        )
        if user.main_photo != "":
            thumb_url = "https://bot.urbanius.club" + user.main_photo.url
        else:
            thumb_url = "https://bot.urbanius.club/media/no_foto.jpg"
        user_res_str.thumb_url = thumb_url
        user_res_str.thumb_width = 25
        user_res_str.thumb_height = 25
        results.append(user_res_str)
    update.inline_query.answer(results)
    return "working"

def manage_chosen_user(update: Update, context: CallbackContext):
    chosen_user_id = update.chosen_inline_result.result_id
    chosen_user = User.get_user_by_username_or_user_id(chosen_user_id)
    user_id = update.chosen_inline_result.from_user.id

    if not(chosen_user.main_photo):
        photo = settings.BASE_DIR / 'media/no_foto.jpg'
        photo_id = get_no_foto_id()
    else:
        if not chosen_user.main_photo_id:
            fill_file_id(chosen_user, "main_photo")
        photo = chosen_user.main_photo.path
        photo_id = chosen_user.main_photo_id

    manage_usr_btn = make_manage_usr_btn(chosen_user_id)

    reply_markup=make_keyboard(manage_usr_btn,"inline",1,None,BACK)
    text = chosen_user.full_profile()
    # text = chosen_user.short_profile()
    if os.path.exists(photo):
        send_photo(user_id, photo_id, caption=text, reply_markup=reply_markup)
    else:
        send_message(user_id=user_id, text = text, reply_markup=reply_markup)
    return "working"

def show_full_profile(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data.split("_")
    found_user_id = int(data[-1])
    found_user = User.get_user_by_username_or_user_id(found_user_id)
    profile_text = found_user.full_profile()
    manage_usr_btn = make_manage_usr_btn(found_user_id)
    reply_markup=make_keyboard(manage_usr_btn,"inline",1,None,BACK)
    query.edit_message_text(text=profile_text, reply_markup=reply_markup)
    return "working"

def handle_show_full_profile(update: Update, context: CallbackContext, found_user_id=None):
    if update.callback_query != None:
        query = update.callback_query
        user_id = query.from_user.id
        query.answer()
        if found_user_id == None:
            data = query.data.split("_")
            found_user_id = int(data[-1])
    else:
        user_id = update.message.from_user.id
    found_user = User.get_user_by_username_or_user_id(found_user_id)
    profile_text = found_user.full_profile()
    manage_usr_btn = make_manage_usr_btn(found_user_id)
    reply_markup=make_keyboard(manage_usr_btn,"inline",1,None,BACK)


    if not(found_user.main_photo):
        photo = settings.BASE_DIR / 'media/no_foto.jpg'
        photo_id = get_no_foto_id()
    else:
        if not found_user.main_photo_id:
            fill_file_id(found_user, "main_photo")
        photo = found_user.main_photo.path
        photo_id = found_user.main_photo_id
    if os.path.exists(photo):
        send_photo(user_id, photo_id, caption=profile_text, reply_markup=reply_markup)
    else:
        send_message(user_id=user_id, text = profile_text, reply_markup=reply_markup)

    # send_message(query.from_user.id, text=profile_text, reply_markup=reply_markup)
    # query.edit_message_text(text=profile_text, reply_markup=reply_markup)
    # try:
    #     # профиль с фотографией
    #     query.edit_message_caption(caption=profile_text, reply_markup=reply_markup)
    # except:
    #     # профиль без фотографии
    #     query.edit_message_text(text=profile_text, reply_markup=reply_markup)
    return "working"

def back_to_user(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data.split("_")
    found_user_id = int(data[-1])
    found_user = User.get_user_by_username_or_user_id(found_user_id)
    profile_text = found_user.full_profile()
    # profile_text = found_user.short_profile()
    manage_usr_btn = make_manage_usr_btn(found_user_id)
    reply_markup=make_keyboard(manage_usr_btn,"inline",1,None,BACK)
    query.edit_message_text(text=profile_text, reply_markup=reply_markup)
    return "working"

# Запрос телефона
def direct_communication(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data.split("_")
    choosen_user_id = int(data[-1])
    choosen_user = User.get_user_by_username_or_user_id(choosen_user_id)
    send_contact(
        user_id=query.from_user.id,
        phone_number=choosen_user.telefon,
        first_name=choosen_user.first_name,
        last_name=choosen_user.last_name
    )
    return

# Предложение сделки
def make_offer(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    data = query.data.split("_")
    offer_user_id = int(data[-1])
    offer_user = User.get_user_by_username_or_user_id(offer_user_id)
    context.user_data["offer"] = mymodels.Offers.objects.create(
        user=offer_user,
        from_user=user
    )

    # query.edit_message_reply_markup(make_keyboard(EMPTY,"inline",1))
    reply_markup=make_keyboard(back_to_user_btn(offer_user_id),"inline",5,None,None) 
    send_message(user_id, text=OFFER_HELLO, reply_markup=reply_markup)
    return "offer"

def send_offer(update: Update, context: CallbackContext):
    offer = context.user_data["offer"]
    offer.offer = update.message.text
    offer.create_done = True
    offer.save()
    user_id = update.message.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    send_message(
        user_id=offer.user.user_id,
        text= "Пользователь @{} {} {} предлагает Вам сделку.\n{}".format(
            user.username,
            user.first_name,
            user.last_name,
            offer.offer
        ),
        reply_markup=make_keyboard(
            {
            "accept_offer_"+ str(offer.id):"Принять",
            "reject_offer_"+ str(offer.id):"Отклонить",
            },
            "inline",
            1,
            None,
            None
        )
    )
    # manage_usr_btn = make_manage_usr_btn(offer.user.user_id)
    # reply_markup=make_keyboard(manage_usr_btn,"inline",1,None,BACK)
    # profile_text = offer.user.full_profile()
    # update.edit_message_text(text=profile_text, reply_markup=reply_markup)
    # return "working"
    send_message(user_id, FIN_OFFER)
    return handle_show_full_profile(update, context, offer.user.user_id)

def accept_offer(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    data = query.data.split("_")
    offer_id = int(data[-1])
    offer = mymodels.Offers.objects.get(id=offer_id)
    offer.decision = "accepted"
    offer.save()
    from_user = offer.from_user
    send_message(
        user_id=from_user.user_id,
        text=ACCEPTED_OFFER.format(
            user.username,
            user.first_name,
            user.last_name,
        ),
        reply_markup=make_keyboard({f"handle_full_profile_{user_id}":"Перейти в профиль пользователя"},"inline",1)
    )
    # manage_usr_btn = make_manage_usr_btn(from_user.user_id, show_full_profile=True)
    # reply_markup=make_keyboard(manage_usr_btn,"inline",1,None,BACK)
    send_message(user_id=user_id, text="Предлагаем перейти к прямой коммуникации.")
    return handle_show_full_profile(update, context, from_user.user_id)

def reject_offer(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    data = query.data.split("_")
    offer_id = int(data[-1])
    offer = mymodels.Offers.objects.get(id=offer_id)
    offer.decision = "rejected"
    offer.save()
    from_user = offer.from_user
    query.delete_message()
    send_message(
        user_id=from_user.user_id,
        text=REJECTED_OFFER.format(
            user.username,
            user.first_name,
            user.last_name,
        )
    )
    return

# Установка оценки
def set_rating(update: Update, context: CallbackContext):
    # Запрашиваем оценку
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    data = query.data.split("_")
    rated_user_id = int(data[-1])

    rated_user = User.get_user_by_username_or_user_id(rated_user_id)
    context.user_data["rated_user"] = rated_user
    #text = rated_user.short_profile()
    #query.edit_message_text(text)
    query.edit_message_reply_markup(make_keyboard(EMPTY,"inline",1))
    set_rating_btn = {
                      1:"1",
                      2:"2",
                      3:"3",
                      4:"4",
                      5:"5",
                      }    
    reply_markup=make_keyboard(set_rating_btn,"inline",5,None,back_to_user_btn(rated_user_id)) 
    text = "Поставьте оценку пользователю: " + str(rated_user)
    query.edit_message_text(text=text, reply_markup=reply_markup)
    return "set_rating"

def set_rating_comment(update: Update, context: CallbackContext):
    # Запрашиваем комментарий к оценке.
    query = update.callback_query
    user_id = query.from_user.id
    rating = query.data
    rated_user = context.user_data["rated_user"]
    context.user_data["rating"] = rating 
    text =f"Пользователю '{str(rated_user)}' поставлена оценка {rating}. Введите комментарий к оценке"
    query.edit_message_text(text)

    return "set_rating_comment"

def store_rating(update: Update, context: CallbackContext):
    # Сохраняем оценку       
    user_rating = mymodels.UsersRatings()
    user_rating.rating = int(context.user_data["rating"])
    user_rating.comment = update.message.text
    user_rating.user = context.user_data["rated_user"]
    user_rating.save()
    user_id = update.message.from_user.id

    context.user_data["search_started"] = False
    manage_usr_btn = make_manage_usr_btn(context.user_data["rated_user"].user_id, show_full_profile=True)
    reply_markup=make_keyboard(manage_usr_btn,"inline",1,None,BACK)
    send_message(user_id=user_id, text=FIN_RATING,reply_markup=reply_markup)
    return "working" 

def handle_forwarded(update: Update, context: CallbackContext):
    found_user = User.get_user_by_username_or_user_id(update.message.forward_from.id)
    user_id = update.message.from_user.id
    if found_user is not None:
        profile_text = found_user.full_profile()
        manage_usr_btn = make_manage_usr_btn(found_user.user_id)
        reply_markup=make_keyboard(manage_usr_btn,"inline",1,None,BACK)
        if not(found_user.main_photo):
            photo = settings.BASE_DIR / 'media/no_foto.jpg'
            photo_id = get_no_foto_id()
        else:
            if not found_user.main_photo_id:
                fill_file_id(found_user, "main_photo")
            photo = found_user.main_photo.path
            photo_id = found_user.main_photo_id
        if os.path.exists(photo):
            send_photo(
                user_id, 
                photo_id, 
                caption=profile_text, 
                reply_markup=reply_markup
                )
        else:
            send_message(
                user_id=user_id, 
                text=profile_text, 
                reply_markup=reply_markup
                )
    else:
        send_message(
            user_id=user_id, 
            text="Пользователь не найден",
        )
    return "working"

def setup_dispatcher_conv(dp: Dispatcher):
    # Диалог отправки сообщения
    conv_handler = ConversationHandler( 
        # точка входа в разговор      
        entry_points=[CallbackQueryHandler(start_conversation, pattern="^find_members$"),
                      CallbackQueryHandler(show_full_profile, pattern="^full_profile_"),
                      CallbackQueryHandler(handle_show_full_profile, pattern="^handle_full_profile_"),
                      CallbackQueryHandler(set_rating, pattern="^setuserrating_"),
                      MessageHandler(Filters.forwarded & Filters.private, handle_forwarded)
                     ],      
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            "working":[
                       InlineQueryHandler(manage_find),
                       ChosenInlineResultHandler(manage_chosen_user),             
                       CallbackQueryHandler(stop_conversation, pattern="^back$"),
                       CallbackQueryHandler(set_rating, pattern="^setuserrating_"),
                       CallbackQueryHandler(show_full_profile, pattern="^full_profile_"),
                       CallbackQueryHandler(direct_communication, pattern="^direct_communication_"),
                       CallbackQueryHandler(make_offer, pattern="^make_offer_"),
                       CallbackQueryHandler(handle_show_full_profile, pattern="^handle_full_profile_"),
                       MessageHandler(Filters.text & FilterPrivateNoCommand, blank)
                      ],
            "offer":[
                    CallbackQueryHandler(back_to_user, pattern="^back_to_user_"),
                    MessageHandler(Filters.text & FilterPrivateNoCommand, send_offer)
            ],
            "set_rating":[
                          CallbackQueryHandler(back_to_user, pattern="^back_to_user_"),
                          CallbackQueryHandler(set_rating_comment),
                         ],
            "set_rating_comment":[
                          MessageHandler(Filters.text & FilterPrivateNoCommand, store_rating),
                         ],
        },
        # точка выхода из разговора
        fallbacks=[CommandHandler('cancel', stop_conversation, Filters.chat_type.private),
                   CommandHandler('start', stop_conversation, Filters.chat_type.private)]        
    )
    dp.add_handler(conv_handler)  
    dp.add_handler(CallbackQueryHandler(accept_offer, pattern="^accept_offer_"))
    dp.add_handler(CallbackQueryHandler(reject_offer, pattern="^reject_offer_"))
