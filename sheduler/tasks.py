
import os
import pytz
import datetime
from telegram.ext import JobQueue, CallbackContext
import telegram
from django.db.models import Q
from .models import *
from tgbot.models import User, NewUser
from events.models import EventRequests
from tgbot.handlers.utils import send_message, send_photo, send_document, fill_file_id, get_no_foto_id,send_mess_by_tmplr
from tgbot.utils import get_uniq_file_name
from tgbot.handlers.keyboard import make_keyboard
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
        #jq.run_daily(send_rating_reminder, time, days = days, name="rating_reminder")
        jq.run_repeating(send_rating_reminder, 10, name="rating_reminder")

    # Создаем/обновляем задание "напоминание о продолжении регистрации"
    curr_task = Tasks.objects.get(code = "reg_reminder")
    remove_job_if_exists("reg_reminder", jq)
    if curr_task.is_active:
        days = curr_task.getdays()
        time = datetime.time(hour=curr_task.time.hour, minute=curr_task.time.minute, tzinfo=pytz.timezone('Europe/Moscow'))
        #jq.run_daily(send_reg_reminder, time, days = days, name="reg_reminder")
        jq.run_repeating(send_rating_reminder, 10, name="rating_reminder")
    jq.start()         
    return jq


def send_rating_reminder(context: CallbackContext):
    """
    Это задание создает запланированные к отсылке напоминания об установке оценки мероприятия
    напоминание делается 1 раз на следующий день   
    """
    mess_template = MessageTemplates.objects.get(code = "rating_reminder")
    requests_set = EventRequests.objects.filter(confirmed = True, event__date = datetime.date.today() - datetime.timedelta(days=1))
    for request in requests_set:
        new_mess = MessagesToSend()
        new_mess.receiver = request.user  
        new_mess.text = mess_template.text
        new_mess.save()

        new_mess = MessagesToSend()
        new_mess.receiver = request.user
        text = request.event.get_description()
        text += request.event.get_user_info(request.user)
        new_mess.text = text
        new_mess.file = request.event.file
        new_mess.file_id = request.event.file_id
        set_rating_btn = {
                        "rateevent_1_" + str(request.event.pk):"1",
                        "rateevent_2_" + str(request.event.pk):"2",
                        "rateevent_3_" + str(request.event.pk):"3",
                        "rateevent_4_" + str(request.event.pk):"4",
                        "rateevent_5_" + str(request.event.pk):"5",
                        } 
        keyboard = {}
        keyboard["buttons"] = set_rating_btn  
        keyboard["type"] = "inline" 
        keyboard["btn_in_row"] = 5
        keyboard["first_btn"] = None
        keyboard["last_btn"] = None                     
        new_mess.reply_markup = keyboard        
        new_mess.save()


def send_reg_reminder(context: CallbackContext):
    """
     Это задание send_reg_reminder. Оно создает запланированные к отсылке напоминания продолжении регистрации
     напоминание делается 1 раз на следующий день    
    """
    mess_template = MessageTemplates.objects.get(code = "reg_reminder")
    q = (
            Q(registered = False)& 
            Q(created_at__gte = datetime.date.today()-datetime.timedelta(days=1))& 
            Q(created_at__lte=datetime.date.today())
        )
    requests_set = NewUser.objects.filter(q)
    for new_user in requests_set:
        new_mess = MessagesToSend()
        new_mess.receiver_user_id = new_user.user_id  
        new_mess.text = mess_template.text
        new_mess.save()


def send_payment_reminder(context: CallbackContext):
    """
     Это задание send_payment_reminder. Оно создает запланированные к отсылке напоминания об оплате
     напоминание делается 2 раз на следующий день после создания заявки и за день до начала мероприятия    
    """
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



def send_random_coffe(context: CallbackContext):
    """
     Это задание random_coffee. Оно создает запланированные к отсылке сообщения в рамках акции
     делается 1 раз в неделю (зависит от настройки задания)    
    """
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
        

def send_confirm_event(context: CallbackContext):
    """
     Это задание send_confirm_event. Оно создает запланированные к отсылке сообщения
     выполняется постоянно. Отправляет подтверждение, когда находит подтвержденную заявку    
    """
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


def send_sheduled_message(context: CallbackContext):
    """
     Это задание рассылки сообщений. Повторяется с периодичностью заданной в задаче с кодом send_messages (10 сек)
     Сообщения беруться из таблицы MessagesToSend, куда добавляются другими заданиями или вручную   
    """
    mess_set = MessagesToSend.objects.filter(sended = False).order_by("created_at")[:20]
    for mess in mess_set:
        success = False
        reply_markup = None
        if  mess.reply_markup:
            buttons = mess.reply_markup.get("buttons")
            type = mess.reply_markup.get("type")
            btn_in_row = mess.reply_markup.get("btn_in_row")
            first_btn = mess.reply_markup.get("first_btn")
            last_btn = mess.reply_markup.get("last_btn")
            reply_markup = make_keyboard(buttons,type,btn_in_row,first_btn,last_btn)
        user_id = mess.receiver.user_id if mess.receiver else mess.receiver_user_id 

        success = send_mess_by_tmplr(user_id, mess, reply_markup)         

        if success:
            mess.sended_at = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))
            mess.sended = True
            mess.save()
    return len(mess_set)