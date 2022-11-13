from telegram import (
    Update, ParseMode,
    InlineQueryResultArticle, InputTextMessageContent
)
from telegram.ext import (
    Dispatcher, CommandHandler,
    MessageHandler, CallbackQueryHandler,
    Filters, CallbackContext, ConversationHandler, InlineQueryHandler,
    ChosenInlineResultHandler
)
import os
from telegram.ext.filters import Filters as F
from django.conf import settings
from .messages import *
from .answers import *
from tgbot.models import tgGroups
from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.filters import FilterPrivateNoCommand, FilterGroupNoCommand
from tgbot.handlers.utils import send_mess_by_tmplt
from tgbot.utils import send_message
from tgbot.handlers.main.answers import get_start_menu
from tgbot.handlers.main.messages import get_start_mess

# Возврат к главному меню
def stop_conversation(update: Update, context: CallbackContext):
    # Заканчиваем разговор.
    if update.message:
        user_id = update.message.from_user.id
        user = User.get_user_by_username_or_user_id(user_id)
    else:
        update.callback_query.answer()
        user_id = update.callback_query.from_user.id
        user = User.get_user_by_username_or_user_id(user_id)
    # send_message(user_id=user_id, text=GROUP_FINISH, reply_markup=make_keyboard(EMPTY,"usual",1))
    send_message(user_id=user_id, text=get_start_mess(user), reply_markup=get_start_menu(user))

    return ConversationHandler.END

# Временная заглушка
def blank(update: Update, context: CallbackContext):
    update.message.reply_text(ASK_REENTER)

def bad_callback_enter(update: Update, context: CallbackContext):
    update.message.reply_text(ASK_REENTER)

def handle_chose_group(update: Update, context: CallbackContext):
    pass

# Начало разговора
def start_conversation(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    # user_id = query.from_user.id
    # user = User.get_user_by_username_or_user_id(user_id)
    # groups_menu = {}
    # for group in user.usertggroups_set.all():
    #     groups_menu[group.group.pk] = group.group.name
    query.edit_message_text(
        HELLO_MESS_2,
        # reply_markup=make_keyboard(FIND,"inline",1,None,BACK)
        )
    return "working"

# Обработчик поиска
def manage_find(update: Update, context: CallbackContext):
    # query = update.inline_query.query.strip()
    # if len(query) < 3:
    #     return
    tg_groups = tgGroups.objects.filter(show_for_users=True)
    # tg_groups = tgGroups.objects.all()
    # users_set = User.find_users_by_keywords(query)
    # users_set = users_set.exclude(user_id = update.inline_query.from_user.id)
    results = []
    for group in tg_groups:
        # logging.info("1111111111\n{}".format(os.getenv("WEB_DOMAIN") + group.file.url))
        group_res_str = InlineQueryResultArticle(
            id=str(group.chat_id),
            title=str(group.name),
            # thumb_url=group.file.url,
            # url=group.link,
            input_message_content = InputTextMessageContent("Выбрана группа"),
            description = group.text,
        )
        if group.file != "":
            thumb_url = "https://bot.urbanius.club" + group.file.url
            group_res_str.thumb_url = thumb_url
            group_res_str.thumb_width = 25
            group_res_str.thumb_height = 25
        results.append(group_res_str)
    update.inline_query.answer(results, cache_time=10)
    # return "working"

def show_group(update: Update, context: CallbackContext):
    chosen_tg_group_id = update.chosen_inline_result.result_id
    group = tgGroups.objects.get(chat_id=chosen_tg_group_id)
    user_id = update.chosen_inline_result.from_user.id
    # query = update.callback_query
    # user_id = query.from_user.id
    # group = tgGroups.objects.get(pk = int(query.data))
    # query.edit_message_text(f"<b>{group.name}</b>", reply_markup = make_keyboard(EMPTY,"inline",1))
    ENTER_GROUP = {
        "enter_group": {
            "label": "Вступить в группу",
            "type": "switch_inline",
            "url": group.link
        }
    }
    reply_markup=make_keyboard(OTHER_GROUPS,"inline",1,ENTER_GROUP,CANCEL)
    # add_text = f"\nСсылка для присоединения к группе {group.link}"
    send_mess_by_tmplt(user_id, group, reply_markup)
    # send_mess_by_tmplt(user_id, group, reply_markup, fut_text=add_text)
    # return "manage_group" 

def show_group_list(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    groups_menu = {}
    for group in user.usertggroups_set.all():
        groups_menu[group.group.pk] = group.group.name
    query.edit_message_reply_markup(make_keyboard(EMPTY,"inline",1))
    send_message(user_id, ASK_SELECT_GROUP, reply_markup=make_keyboard(groups_menu,"inline",1,None,BACK))
    return "working"


def setup_dispatcher_conv(dp: Dispatcher):
    # Диалог отправки сообщения
    conv_handler = ConversationHandler( 
        # точка входа в разговор      
        entry_points=[CallbackQueryHandler(start_conversation, pattern="^groups$"),
                    CallbackQueryHandler(start_conversation, pattern="^find_groups$"),
                      ],      
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            "working":[
                       InlineQueryHandler(manage_find),
                      # ChosenInlineResultHandler(manage_chosen_user),             

                       CallbackQueryHandler(stop_conversation, pattern="^back$"),
                    #    CallbackQueryHandler(show_group),
                       MessageHandler(Filters.text & FilterPrivateNoCommand, blank)
                      ],
       "manage_group":[CallbackQueryHandler(show_group_list, pattern="^cancel$"),            
                       MessageHandler(Filters.text & FilterPrivateNoCommand, blank)
                      ],
        },
        # точка выхода из разговора
        fallbacks=[CommandHandler('cancel', stop_conversation, Filters.chat_type.private),
                   CommandHandler('start', stop_conversation, Filters.chat_type.private)]        
    )
    # dp.add_handler(conv_handler)
    dp.add_handler(InlineQueryHandler(manage_find, pattern="^chats")),
    dp.add_handler(ChosenInlineResultHandler(show_group))
    dp.add_handler(
        MessageHandler(
            F.regex(r"Выбрана группа") & FilterPrivateNoCommand,
            handle_chose_group
            )
    )
    dp.add_handler(CallbackQueryHandler(stop_conversation, pattern="^back-from-groups$"),)




