
import os
import pytz
import datetime
from telegram.ext import JobQueue, CallbackContext
import telegram
from .models import *
from tgbot.models import User, MessagesToSend, MessageTemplates
from tgbot.handlers.utils import send_message, send_photo, send_document
from dtb import settings

def remove_job_if_exists(name: str, jq: JobQueue):
    """
       Удаляет задание с заданным именем. 
       Возвращает, было ли задание удалено
    """
    current_jobs = jq.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

def restarts_tasks(jq: JobQueue) -> JobQueue:
    # Создаем/обновляем задание "Random coffe"
    task_coffe = Tasks.objects.get(code = "random_coffe")
    remove_job_if_exists("random_coffe", jq)
    if task_coffe.is_active:
        days = task_coffe.getdays()
        time = datetime.time(hour=task_coffe.time.hour, minute=task_coffe.time.minute, tzinfo=pytz.timezone('Europe/Moscow'))
        jq.run_daily(send_random_coffe, time, days = days, context = "random_coffe", name="random_coffe")

    # Создаем/обновляем задание "Рассылка сообщений"
    task_send_messages = Tasks.objects.get(code = "send_messages")
    remove_job_if_exists("send_messages", jq)
    if task_send_messages.is_active:
        jq.run_repeating(send_sheduled_message, task_send_messages.interval, name="send_messages")

    jq.start()         
    return jq

# Это задание random_coffe. Оно создает запланированные к отсылке сообщения
def send_random_coffe(context: CallbackContext):
    random_coffe_template = MessageTemplates.objects.get(code = "random_coffe")
    user_set = User.objects.filter(random_coffe_on = True, is_blocked_bot = False, is_banned = False)
    for user in user_set:
        recomended_user_set = User.objects.filter(random_coffe_on = True, is_blocked_bot = False, is_banned = False).exclude(pk = user.pk).order_by('?')
        if len(recomended_user_set) == 0:
            continue
        recomended_user = recomended_user_set[0]
        new_mess = MessagesToSend()
        new_mess.receiver = user  
        new_mess.text = random_coffe_template.text
        new_mess.created_at = datetime.datetime.now()
        new_mess.recommended_friend = recomended_user
        new_mess.save()

# Это задание рассылки сообщений. Повторяется с периодичностью заданной в задаче с кодом send_messages (10 сек)
# Сообщения беруться из таблицы MessagesToSend, куда добавляются другими заданиями или вручную
def send_sheduled_message(context: CallbackContext):
    mess_set = MessagesToSend.objects.filter(sended = False).order_by("created_at")[:20]
    for mess in mess_set:
        success = False    
        if (not mess.file)and(mess.recommended_friend is None):
            success = send_message(user_id = mess.receiver.user_id, text = mess.text, parse_mode = telegram.ParseMode.HTML, disable_web_page_preview=True)
        elif mess.file:
            if mess.file.name[-3:] in ["jpg","bmp","png"]:# в сообщении картинка
                if os.path.exists(mess.file.path):
                    success = send_photo(mess.receiver.user_id, open(mess.file.path, 'rb'), caption = mess.text, parse_mode = telegram.ParseMode.HTML)
                else:
                    success = send_message(user_id = mess.receiver.user_id, text = mess.text + "\nПриложенный файл потерялся", 
                                        parse_mode = telegram.ParseMode.HTML, disable_web_page_preview=True)
            else:
                if os.path.exists(mess.file.path):
                    success = send_document(mess.receiver.user_id, open(mess.file.path, 'rb'), caption = mess.text, parse_mode = telegram.ParseMode.HTML)
                else:
                    success = send_message(user_id = mess.receiver.user_id, text = mess.text + "\nПриложенный файл потерялся",
                                        parse_mode = telegram.ParseMode.HTML, disable_web_page_preview=True)
        elif mess.recommended_friend:
            user = mess.recommended_friend
            if not(user.main_photo):
                photo = settings.BASE_DIR / 'media/no_foto.jpg'
            else:
                photo = user.main_photo.path
            if os.path.exists(photo):
                send_photo(mess.receiver.user_id, open(photo, 'rb'), caption = user.short_profile(), parse_mode = telegram.ParseMode.HTML)
            else:
                send_message(user_id = mess.receiver.user_id,text = user.short_profile() + "\nФайл фото потерялся", parse_mode = telegram.ParseMode.HTML)
            success = send_message(user_id = mess.receiver.user_id, text = mess.text, parse_mode = telegram.ParseMode.HTML, disable_web_page_preview=True)    
        if success:
            mess.sended_at = datetime.datetime.now()
            mess.sended = True
            mess.save()
    return len(mess_set)