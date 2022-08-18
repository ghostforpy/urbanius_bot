
import os
import pytz
import datetime
from telegram.ext import JobQueue, CallbackContext
import telegram
from django.db.models import Q
from .models import *
from tgbot.models import User, MessagesToSend, MessageTemplates
from events.models import EventRequests
from tgbot.handlers.utils import send_message, send_photo, send_document, fill_file_id, get_no_foto_id
from tgbot.utils import get_uniq_file_name
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
    # Создаем/обновляем задание "Random coffee"
    curr_task = Tasks.objects.get(code = "random_coffee")
    remove_job_if_exists("random_coffee", jq)
    if curr_task.is_active:
        days = curr_task.getdays()
        time = datetime.time(hour=curr_task.time.hour, minute=curr_task.time.minute, tzinfo=pytz.timezone('Europe/Moscow'))
        jq.run_daily(send_random_coffe, time, days = days, context = "random_coffee", name="random_coffee")

    # Создаем/обновляем задание "Рассылка сообщений"
    curr_task = Tasks.objects.get(code = "send_messages")
    remove_job_if_exists("send_messages", jq)
    if curr_task.is_active:
        jq.run_repeating(send_sheduled_message, curr_task.interval, name="send_messages")

    # Создаем/обновляем задание "Рассылка подтверждений на регистрацию"
    curr_task = Tasks.objects.get(code = "send_confirm_event")
    remove_job_if_exists("send_confirm_event", jq)
    if curr_task.is_active:
        jq.run_repeating(send_confirm_event, curr_task.interval, name="send_confirm_event")

    # Создаем/обновляем задание "напоминание об оплате"
    curr_task = Tasks.objects.get(code = "payment_reminder")
    remove_job_if_exists("payment_reminder", jq)
    if curr_task.is_active:
        days = curr_task.getdays()
        time = datetime.time(hour=curr_task.time.hour, minute=curr_task.time.minute, tzinfo=pytz.timezone('Europe/Moscow'))
        jq.run_daily(send_payment_reminder, time, days = days, name="payment_reminder")
        #jq.run_repeating(send_payment_reminder, 10, name="payment_reminder")

    # Создаем/обновляем задание "напоминание об оценке мероприятия"
    curr_task = Tasks.objects.get(code = "rating_reminder")
    remove_job_if_exists("rating_reminder", jq)
    if curr_task.is_active:
        days = curr_task.getdays()
        time = datetime.time(hour=curr_task.time.hour, minute=curr_task.time.minute, tzinfo=pytz.timezone('Europe/Moscow'))
        jq.run_daily(send_rating_reminder, time, days = days, name="rating_reminder")
        #jq.run_repeating(send_rating_reminder, 10, name="rating_reminder")

    jq.start()         
    return jq

# Это задание создает запланированные к отсылке напоминания об установке оценки мероприятия
def send_rating_reminder(context: CallbackContext):
    mess_template = MessageTemplates.objects.get(code = "rating_reminder")
    requests_set = EventRequests.objects.filter(confirmed = True, event__date = datetime.date.today() - datetime.timedelta(days=1))
    for request in requests_set:
        new_mess = MessagesToSend()
        new_mess.receiver = request.user  
        new_mess.text = mess_template.text + f"\n<b>{request.event}</b>"
        new_mess.save()

# Это задание send_payment_reminder. Оно создает запланированные к отсылке напоминания об оплате
def send_payment_reminder(context: CallbackContext):
    mess_template = MessageTemplates.objects.get(code = "payment_reminder")
    q = (
            Q(payed = False)& 
            Q(created_at__gte = datetime.date.today()-datetime.timedelta(days=1))& 
            Q(created_at__lte=datetime.date.today())
        )| \
        (
            Q(payed = False)&
            Q(event__date = datetime.date.today()+datetime.timedelta(days=1))
        )
    requests_set = EventRequests.objects.filter(q)
    for request in requests_set:
        new_mess = MessagesToSend()
        new_mess.receiver = request.user  
        new_mess.text = mess_template.text + f" Заявка на мероприятие {request.event}. Оплатить можно через меню Мероприятия/Ближайшие мероприятия"
        new_mess.save()


# Это задание random_coffee. Оно создает запланированные к отсылке сообщения
def send_random_coffe(context: CallbackContext):
    mess_template = MessageTemplates.objects.get(code = "random_coffee")
    user_set = User.objects.filter(random_coffe_on = True, is_blocked_bot = False, is_banned = False)
    for user in user_set:
        recomended_user_set = User.objects.filter(random_coffe_on = True, is_blocked_bot = False, is_banned = False).exclude(pk = user.pk).order_by('?')
        if len(recomended_user_set) == 0:
            continue
        recomended_user = recomended_user_set[0]
        new_mess = MessagesToSend()
        new_mess.receiver = user  
        new_mess.text = mess_template.text
        new_mess.save()
        new_mess = MessagesToSend()
        new_mess.receiver = user 
        new_mess.text = recomended_user.short_profile()
        if not(recomended_user.main_photo):
            new_mess.file = 'no_foto.jpg'
            new_mess.file_id = get_no_foto_id()
        else:
            if not recomended_user.main_photo_id:
                fill_file_id(user, "main_photo")
            new_mess.file = user.main_photo
            new_mess.file_id = user.main_photo_id
        new_mess.save()
        
# Это задание send_confirm_event. Оно создает запланированные к отсылке сообщения
def send_confirm_event(context: CallbackContext):
    mess_template = MessageTemplates.objects.get(code = "send_confirm_event")
    requests_set = EventRequests.objects.filter(confirmed = True, qr_code_sended = False)

    for request in requests_set:
        new_mess = MessagesToSend()
        new_mess.receiver = request.user  
        new_mess.text = mess_template.text
        new_mess.save()
        new_mess = MessagesToSend()
        new_mess.receiver = request.user 
        img,text = request.get_qr_code()
        filename = get_uniq_file_name(settings.BASE_DIR / "media/qr_codes","qr_code","png")
        img.save(settings.BASE_DIR / ("media/qr_codes/"+filename))
        new_mess.file = "qr_codes/"+filename
        new_mess.text = text
        new_mess.save()
        request.qr_code_sended = True
        request.save()

# Это задание рассылки сообщений. Повторяется с периодичностью заданной в задаче с кодом send_messages (10 сек)
# Сообщения беруться из таблицы MessagesToSend, куда добавляются другими заданиями или вручную
def send_sheduled_message(context: CallbackContext):
    mess_set = MessagesToSend.objects.filter(sended = False).order_by("created_at")[:20]
    for mess in mess_set:
        success = False    
        if not mess.file:
            success = send_message(user_id = mess.receiver.user_id, text = mess.text, parse_mode = telegram.ParseMode.HTML, disable_web_page_preview=True)
        elif mess.file:
            if not mess.file_id:
                fill_file_id(mess, "file")
            if mess.file.name[-3:] in ["jpg","bmp","png"]:# в сообщении картинка
                if os.path.exists(mess.file.path):
                    success = send_photo(mess.receiver.user_id, mess.file_id, caption = mess.text, parse_mode = telegram.ParseMode.HTML)
                else:
                    success = send_message(user_id = mess.receiver.user_id, text = mess.text + "\nПриложенный файл потерялся", 
                                        parse_mode = telegram.ParseMode.HTML, disable_web_page_preview=True)
            else:
                if os.path.exists(mess.file.path):
                    success = send_document(mess.receiver.user_id, mess.file_id, caption = mess.text, parse_mode = telegram.ParseMode.HTML)
                else:
                    success = send_message(user_id = mess.receiver.user_id, text = mess.text + "\nПриложенный файл потерялся",
                                        parse_mode = telegram.ParseMode.HTML, disable_web_page_preview=True)
        if success:
            mess.sended_at = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))
            mess.sended = True
            mess.save()
    return len(mess_set)