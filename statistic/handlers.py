from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import (
    Dispatcher, CommandHandler,
    MessageHandler, CallbackQueryHandler,
    Filters,
    ConversationHandler,
)
from tgbot.models import User, tgGroups
from .models import MessageStatistic

#-------------------------------------------  
# Обработчик просмотр рейтинга
def proc_group_mess(update: Update, context: CallbackContext):
    user = User.get_user_by_username_or_user_id(update.message.from_user.id)
    group_id = update._effective_message.chat_id
    tggroup_set = tgGroups.objects.filter(chat_id = group_id)
    if len(tggroup_set) == 0:
        tggroup = tgGroups(name = update._effective_chat.title, chat_id = group_id, link = update._effective_chat.link)
        tggroup.save()
    else:
        tggroup = tggroup_set[0]

    mess_stat_set = MessageStatistic.objects.filter(group = tggroup, user = user)
    if len(mess_stat_set) == 0:
        mess_stat = MessageStatistic(group = tggroup, user = user)
        tggroup.save()
    else:
        mess_stat = mess_stat_set[0]
    mess_stat.messages += 1
    mess_stat.save()

def setup_dispatcher_group(dp: Dispatcher):
    dp.add_handler(MessageHandler((Filters.text|Filters.photo|Filters.video|Filters.document|Filters.audio) 
                   & Filters.chat_type.groups, proc_group_mess))