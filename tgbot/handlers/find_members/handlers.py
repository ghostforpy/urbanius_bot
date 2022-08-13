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
from tgbot.handlers.utils import send_message, send_photo
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
    users_set = mymodels.User.find_users_by_keywords(query)
    results = []
    for user in users_set:
        foto_url = settings.MEDIA_DOMAIN + user.main_photo.url
        set_rating_btn = {"setrating_"+ str(user.user_id):"Поставить оценку"}
        user_res_str = InlineQueryResultArticle(
            id=str(user.user_id),
            title=str(user),
            #input_message_content=InputTextMessageContent(user.short_profile()),
            input_message_content = InputTextMessageContent("Выбран пользователь"),
            description = user.about,
            thumb_url = foto_url,
            thumb_width = 50,
            thumb_height = 50,
            #reply_markup=make_keyboard(set_rating_btn,"inline",1,None,BACK),
        )
        results.append(user_res_str)
    update.inline_query.answer(results)
    return "working"

def manage_chosen_user(update: Update, context: CallbackContext):
    chosen_user_id = update.chosen_inline_result.result_id
    chosen_user = User.get_user_by_username_or_user_id(chosen_user_id)
    user_id = update.chosen_inline_result.from_user.id
    if not(chosen_user.main_photo):
        photo = settings.BASE_DIR / 'media/no_foto.jpg'
    else:
        photo = chosen_user.main_photo.path
    
    set_rating_btn = {"setrating_"+ str(chosen_user_id):"Поставить оценку"}
    reply_markup=make_keyboard(set_rating_btn,"inline",1,None,BACK)
    text = chosen_user.short_profile()    
    
    if os.path.exists(photo):
        send_photo(user_id, open(photo, 'rb'), caption = text, reply_markup=reply_markup, parse_mode = ParseMode.HTML)
    else:
        send_message(user_id=user_id, text = text, reply_markup=reply_markup, parse_mode = ParseMode.HTML)

# Установка оценки
def set_rating(update: Update, context: CallbackContext):
    # Запрашиваем оценку
    query = update.callback_query
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    data = query.data.split("_")
    rated_user_id = data[1]
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
    reply_markup=make_keyboard(set_rating_btn,"inline",5,None,BACK) 
    text = "Поставьте оценку пользователю: " + str(rated_user)
    send_message(user_id=user.user_id, text=text, reply_markup=reply_markup)
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

def store_rating (update: Update, context: CallbackContext):
    # Сохраняем оценку       
    user_rating = mymodels.UsersRatings()
    user_rating.rating = int(context.user_data["rating"])
    user_rating.comment = update.message.text
    user_rating.user = context.user_data["rated_user"]
    user_rating.save()
    user_id = update.message.from_user.id

    user = User.get_user_by_username_or_user_id(user_id)
    context.user_data["search_started"] = False
    send_message(user_id=user_id, text=FIND_RATING, reply_markup=make_keyboard(EMPTY,"usual",1))
    send_message(user_id=user_id, text=get_start_mess(user), reply_markup=get_start_menu(user))
    return ConversationHandler.END    

def setup_dispatcher_conv(dp: Dispatcher):
    # Диалог отправки сообщения
    conv_handler = ConversationHandler( 
        # точка входа в разговор      
        entry_points=[CallbackQueryHandler(start_conversation, pattern="^find_members$")],      
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            "working":[
                       InlineQueryHandler(manage_find),   
                       ChosenInlineResultHandler(manage_chosen_user),             
                       MessageHandler(Filters.text([BACK["back"]]) & FilterPrivateNoCommand, stop_conversation),
                       CallbackQueryHandler(stop_conversation, pattern="^back$"),
                       CallbackQueryHandler(set_rating, pattern="^setrating_"),
                       MessageHandler(Filters.text & FilterPrivateNoCommand, blank)
                      ],
            "set_rating":[
                          CallbackQueryHandler(stop_conversation, pattern="^back$"),
                          CallbackQueryHandler(set_rating_comment),
                          MessageHandler(Filters.text([BACK["back"]]) & FilterPrivateNoCommand, stop_conversation),
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
