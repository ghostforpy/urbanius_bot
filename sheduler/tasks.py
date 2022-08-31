
import os
import pytz
import datetime
from telegram.ext import JobQueue, CallbackContext
import telegram
from django.db.models import Q
from .models import *
from tgbot.models import User, NewUser
from events.models import EventRequests, AnonsesDates
from advert.models import SpecialOffersDates
from tgbot.handlers.utils import send_message, send_photo, send_document, fill_file_id, get_no_foto_id,send_mess_by_tmplt
from tgbot.utils import get_uniq_file_name
from tgbot.handlers.keyboard import make_keyboard
from dtb import settings
from dtb.constants import TaskCode, MessageTemplatesCode

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
    curr_task = Tasks.objects.get(code = TaskCode.RANDOM_COFFEE)
    remove_job_if_exists(TaskCode.RANDOM_COFFEE, jq)
    if curr_task.is_active:
        days = curr_task.getdays()
        time = datetime.time(hour=curr_task.time.hour, minute=curr_task.time.minute, tzinfo=pytz.timezone('Europe/Moscow'))
        jq.run_daily(send_random_coffe, time, days = days, context = TaskCode.RANDOM_COFFEE, name=TaskCode.RANDOM_COFFEE)

    # Создаем/обновляем задание "Рассылка сообщений"
    curr_task = Tasks.objects.get(code = TaskCode.SEND_MESSAGES)
    remove_job_if_exists(TaskCode.SEND_MESSAGES, jq)
    if curr_task.is_active:
        jq.run_repeating(send_sheduled_message, curr_task.interval, name=TaskCode.SEND_MESSAGES)

    # Создаем/обновляем задание "Рассылка подтверждений на регистрацию"
    curr_task = Tasks.objects.get(code = TaskCode.SEND_CONFIRM_EVENT)
    remove_job_if_exists(TaskCode.SEND_CONFIRM_EVENT, jq)
    if curr_task.is_active:
        jq.run_repeating(send_confirm_event, curr_task.interval, name=TaskCode.SEND_CONFIRM_EVENT)

    # Создаем/обновляем задание "напоминание об оплате"
    curr_task = Tasks.objects.get(code = TaskCode.PAYMENT_REMINDER)
    remove_job_if_exists(TaskCode.PAYMENT_REMINDER, jq)
    if curr_task.is_active:
        days = curr_task.getdays()
        time = datetime.time(hour=curr_task.time.hour, minute=curr_task.time.minute, tzinfo=pytz.timezone('Europe/Moscow'))
        jq.run_daily(send_payment_reminder, time, days = days, name=TaskCode.PAYMENT_REMINDER)
        #jq.run_repeating(send_payment_reminder, 10, name=TaskCode.PAYMENT_REMINDER)

    # Создаем/обновляем задание "напоминание об оценке мероприятия"
    curr_task = Tasks.objects.get(code = TaskCode.RATING_REMINDER)
    remove_job_if_exists(TaskCode.RATING_REMINDER, jq)
    if curr_task.is_active:
        days = curr_task.getdays()
        time = datetime.time(hour=curr_task.time.hour, minute=curr_task.time.minute, tzinfo=pytz.timezone('Europe/Moscow'))
        jq.run_daily(send_rating_reminder, time, days = days, name=TaskCode.RATING_REMINDER)
        #jq.run_repeating(send_rating_reminder, 30, name=TaskCode.RATING_REMINDER)

    # Создаем/обновляем задание "рассылка анонсов мероприятия"
    curr_task = Tasks.objects.get(code = TaskCode.SEND_ANONSES)
    remove_job_if_exists(TaskCode.SEND_ANONSES, jq)
    if curr_task.is_active:
        days = curr_task.getdays()
        time = datetime.time(hour=curr_task.time.hour, minute=curr_task.time.minute, tzinfo=pytz.timezone('Europe/Moscow'))
        jq.run_daily(send_anonses, time, days = days, name=TaskCode.SEND_ANONSES)
        #jq.run_repeating(send_anonses, 10, name=TaskCode.SEND_ANONSES)


    # Создаем/обновляем задание "рассылка специальных предложений"
    curr_task = Tasks.objects.get(code = TaskCode.SEND_SPEC_OFFERS)
    remove_job_if_exists(TaskCode.SEND_SPEC_OFFERS, jq)
    if curr_task.is_active:
        days = curr_task.getdays()
        time = datetime.time(hour=curr_task.time.hour, minute=curr_task.time.minute, tzinfo=pytz.timezone('Europe/Moscow'))
        jq.run_daily(send_spec_offers, time, days = days, name=TaskCode.SEND_SPEC_OFFERS)
        #jq.run_repeating(send_spec_offers, 30, name=TaskCode.SEND_SPEC_OFFERS)

    # Создаем/обновляем задание "напоминание о продолжении регистрации"
    curr_task = Tasks.objects.get(code = TaskCode.REG_REMINDER)
    remove_job_if_exists(TaskCode.REG_REMINDER, jq)
    if curr_task.is_active:
        days = curr_task.getdays()
        time = datetime.time(hour=curr_task.time.hour, minute=curr_task.time.minute, tzinfo=pytz.timezone('Europe/Moscow'))
        jq.run_daily(send_reg_reminder, time, days = days, name=TaskCode.REG_REMINDER)
        #jq.run_repeating(send_reg_reminder, 10, name=TaskCode.REG_REMINDER)
   
    # Создаем/обновляем задание "поздравление с днем рождения"
    curr_task = Tasks.objects.get(code = TaskCode.HAPPY_BIRTHDAY)
    remove_job_if_exists(TaskCode.HAPPY_BIRTHDAY, jq)
    if curr_task.is_active:
        days = curr_task.getdays()
        time = datetime.time(hour=curr_task.time.hour, minute=curr_task.time.minute, tzinfo=pytz.timezone('Europe/Moscow'))
        jq.run_daily(send_happy_birthday, time, days = days, name=TaskCode.HAPPY_BIRTHDAY)
        #jq.run_repeating(send_happy_birthday, 10, name=TaskCode.HAPPY_BIRTHDAY)
  
    jq.start()         
    return jq


def send_happy_birthday(context: CallbackContext):
    """
     Это задание send_happy_birthday. Оно создает запланированные к отсылке поздравления с днем рождения
    """
    mess_template = MessageTemplates.objects.get(code = MessageTemplatesCode.HAPPY_BIRTHDAY)
    requests_set = User.objects.filter(date_of_birth__month = datetime.date.today().month, date_of_birth__day = datetime.date.today().day,)
    for user in requests_set:
        new_mess = MessagesToSend()
        new_mess.receiver_user_id = user.user_id  
        new_mess.text = mess_template.text
        new_mess.file = mess_template.file
        new_mess.file_id = mess_template.file_id
        
        new_mess.save()

def send_rating_reminder(context: CallbackContext):
    """
    Это задание создает запланированные к отсылке напоминания об установке оценки мероприятия
    напоминание делается 1 раз на следующий день   
    """
    mess_template = MessageTemplates.objects.get(code = MessageTemplatesCode.RATING_REMINDER)
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
                        "remindrateevent_1_" + str(request.event.pk):"1",
                        "remindrateevent_2_" + str(request.event.pk):"2",
                        "remindrateevent_3_" + str(request.event.pk):"3",
                        "remindrateevent_4_" + str(request.event.pk):"4",
                        "remindrateevent_5_" + str(request.event.pk):"5",
                        } 
        keyboard = {}
        keyboard["buttons"] = set_rating_btn  
        keyboard["type"] = "inline" 
        keyboard["btn_in_row"] = 5
        keyboard["first_btn"] = None
        keyboard["last_btn"] = None                     
        new_mess.reply_markup = keyboard        
        new_mess.save()

def send_anonses(context: CallbackContext):
    """
     Это задание send_anonses. Оно создает запланированные анонсы мероприятий
     отсылается в группы и даты указанные в анонсе    
    """
    requests_set = AnonsesDates.objects.filter(anons_date = datetime.datetime.today(), sended = False)
    for anons_day in requests_set:
        if not anons_day.anons.event.file_id:
            fill_file_id(anons_day.anons.event, "file", text = "send_anonses_event")
        if not anons_day.anons.file_id:
            fill_file_id(anons_day.anons, "file", text = "send_anonses_anons")

        if anons_day.anons.file:
            file = anons_day.anons.file
            file_id = anons_day.anons.file_id            
        else:
            file = anons_day.anons.event.file
            file_id = anons_day.anons.event.file_id
        for group in anons_day.anons.sending_groups.all():
            new_mess = MessagesToSend()
            new_mess.receiver_user_id = group.chat_id  
            new_mess.text = anons_day.anons.text
            new_mess.file = file
            new_mess.file_id = file_id
            new_mess.save()
        anons_day.sended = True
        anons_day.save()

    
def send_spec_offers(context: CallbackContext):
    """
     Это задание send_spec_offers. Оно создает запланированные спец предложения
     отсылается в группы и даты указанные в предложения    
    """
    requests_set = SpecialOffersDates.objects.filter(offer_date = datetime.datetime.today(), sended = False)
    for offer_day in requests_set:
        use_offer_btn = {
                        "use_offer-" + str(offer_day.offer.pk):"Воспользоваться предложением"
                        } 
        keyboard = {}
        keyboard["buttons"] = use_offer_btn  
        keyboard["type"] = "inline" 
        keyboard["btn_in_row"] = 1
        keyboard["first_btn"] = None
        keyboard["last_btn"] = None                     

        if not offer_day.offer.file_id:
            fill_file_id(offer_day.offer, "file", text = "send_spec_offers")
        for group in offer_day.offer.sending_groups.all():
            new_mess = MessagesToSend()
            new_mess.receiver_user_id = group.chat_id 

            text = f"Специальное предложение от партнера {offer_day.offer.partner.full_name} \n"
            text += f"{offer_day.offer.name} \n"
            text += f"{offer_day.offer.text} \n"
            text += "Предложение действует до " + offer_day.offer.valid_until.strftime("%d.%m.%Y")
            new_mess.text = text
            new_mess.file = offer_day.offer.file
            new_mess.file_id = offer_day.offer.file_id
            new_mess.reply_markup = keyboard              
            new_mess.save()
        offer_day.sended = True
        offer_day.save()

def send_reg_reminder(context: CallbackContext):
    """
     Это задание send_reg_reminder. Оно создает запланированные к отсылке напоминания продолжении регистрации
     напоминание делается 1 раз на следующий день    
    """
    mess_template = MessageTemplates.objects.get(code = MessageTemplatesCode.REG_REMINDER)
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
    mess_template = MessageTemplates.objects.get(code = MessageTemplatesCode.PAYMENT_REMINDER)
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
    mess_template = MessageTemplates.objects.get(code = MessageTemplatesCode.RANDOM_COFFEE)
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
                fill_file_id(recomended_user, "main_photo", text = "send_random_coffe")
            new_mess.file = recomended_user.main_photo
            new_mess.file_id = recomended_user.main_photo_id
        new_mess.save()
        

def send_confirm_event(context: CallbackContext):
    """
     Это задание send_confirm_event. Оно создает запланированные к отсылке сообщения
     выполняется постоянно. Отправляет подтверждение, когда находит подтвержденную заявку    
    """
    mess_template = MessageTemplates.objects.get(code = MessageTemplatesCode.SEND_CONFIRM_EVENT)
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
            kb_type = mess.reply_markup.get("type")
            btn_in_row = mess.reply_markup.get("btn_in_row")
            first_btn = mess.reply_markup.get("first_btn")
            last_btn = mess.reply_markup.get("last_btn")
            reply_markup = make_keyboard(buttons,kb_type,btn_in_row,first_btn,last_btn)
        user_id = mess.receiver.user_id if mess.receiver else mess.receiver_user_id 

        success = send_mess_by_tmplt(user_id, mess, reply_markup)         

        if type(success) != telegram.message.Message:
            mess.comment = str(success)
        else:
            mess.sended_at = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))
        mess.sended = True
        mess.save()
    return len(mess_set)