from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import (
    Dispatcher, 
    MessageHandler, 
    Filters,
)
from tgbot.models import User, tgGroups
from .models import MessageStatistic

#-------------------------------------------  
# Обработчик сообщений в группах
def proc_group_mess(update: Update, context: CallbackContext):
    user = User.get_user_by_username_or_user_id(update.message.from_user.id) 
    if not user:
        return
    group_id = update._effective_message.chat_id.first()
    tggroup = tgGroups.objects.filter(chat_id = group_id)
    if not tggroup:
        tggroup = tgGroups(name = update._effective_chat.title, chat_id = group_id, link = update._effective_chat.link)
        tggroup.save()

    mess_stat = MessageStatistic.objects.filter(group = tggroup, user = user).first()
    if not mess_stat:
        mess_stat = MessageStatistic(group = tggroup, user = user)
        tggroup.save()
    mess_stat.messages += 1
    mess_stat.save()

def setup_dispatcher_group(dp: Dispatcher):
    dp.add_handler(MessageHandler((Filters.text|Filters.photo|Filters.video|Filters.document|Filters.audio) 
                   & Filters.chat_type.groups, proc_group_mess))