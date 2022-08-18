from tgbot.models import Status, MessageTemplates
from sheduler.models import Tasks
from events.models import EventTypes
import datetime
import os
from dtb import settings

try:
    if not os.path.isdir(settings.BASE_DIR / "media/events"):
        os.mkdir(settings.BASE_DIR / "media/events")
    if not os.path.isdir(settings.BASE_DIR / "media/messages"):
        os.mkdir(settings.BASE_DIR / "media/messages")
    if not os.path.isdir(settings.BASE_DIR / "media/offers"):
        os.mkdir(settings.BASE_DIR / "media/offers")
    if not os.path.isdir(settings.BASE_DIR / "media/qr_codes"):
        os.mkdir(settings.BASE_DIR / "media/qr_codes")
    if not os.path.isdir(settings.BASE_DIR / "media/user_fotos"):
        os.mkdir(settings.BASE_DIR / "media/user_fotos")


    
    # create statuses
    status_set = Status.objects.filter(code = "admin")
    if status_set.count() == 0:
        status = Status(code = "admin", name = "Администратор") 
        status.save()
    status_set = Status.objects.filter(code = "club_resident")
    if status_set.count() == 0:
        status = Status(code = "club_resident", name = "Резидент закрытого клуба") 
        status.save()
    status_set = Status.objects.filter(code = "community_resident")
    if status_set.count() == 0:
        status = Status(code = "community_resident", name = "Резидент сообщества") 
        status.save()
    status_set = Status.objects.filter(code = "group_member")
    if status_set.count() == 0:
        status = Status(code = "group_member", name = "Участник группы") 
        status.save()

    #create Tasks
    task_set = Tasks.objects.filter(code = "random_coffee")
    if task_set.count() == 0:
        task = Tasks()
        task.code = "random_coffee"
        task.name =  "Random coffee"
        task.time = datetime.time(9, 00, 00) # время запуска 9:00
        task.mon = True # по понедельникам
        task.is_active = True # активно 
        task.save()  

    task_set = Tasks.objects.filter(code = "send_messages")
    if task_set.count() == 0:
        task = Tasks()
        task.code = "send_messages"
        task.name =  "Рассылка сообщений"
        task.interval = 10 # повторяется с интервалом 10 сек
        task.is_active = True # активно 
        task.save()       

    task_set = Tasks.objects.filter(code = "send_confirm_event")
    if task_set.count() == 0:
        task = Tasks()
        task.code = "send_confirm_event"
        task.name =  "Рассылка подтверждений регистрацию"
        task.interval = 60 # повторяется с интервалом 60 сек
        task.is_active = True # активно 
        task.save()

    task_set = Tasks.objects.filter(code = "happy_birthday")
    if task_set.count() == 0:
        task = Tasks()
        task.code = "happy_birthday"
        task.name =  "Поздравление с днем рождения"
        task.time = datetime.time(9, 30, 00) # время запуска 9:30
        task.mon = True # каждый день
        task.tue = True
        task.wed = True
        task.thu = True
        task.fri = True
        task.sat = True
        task.san = True
        task.is_active = True # активно 
        task.save() 

    task_set = Tasks.objects.filter(code = "payment_reminder")
    if task_set.count() == 0:
        task = Tasks()
        task.code = "payment_reminder"
        task.name =  "Напоминание об оплате"
        task.time = datetime.time(10, 30, 00) # время запуска 9:30
        task.mon = True # каждый день
        task.tue = True
        task.wed = True
        task.thu = True
        task.fri = True
        task.sat = True
        task.san = True
        task.is_active = True # активно 
        task.save() 

    task_set = Tasks.objects.filter(code = "rating_reminder")
    if task_set.count() == 0:
        task = Tasks()
        task.code = "rating_reminder"
        task.name =  "Напоминание об оценке мероприятия"
        task.time = datetime.time(10, 35, 00) # время запуска 9:30
        task.mon = True # каждый день
        task.tue = True
        task.wed = True
        task.thu = True
        task.fri = True
        task.sat = True
        task.san = True
        task.is_active = True # активно 
        task.save() 

    # create message templates
    template_set = MessageTemplates.objects.filter(code = "rating_reminder")
    if template_set.count() == 0:
        template = MessageTemplates()
        template.code = "rating_reminder"
        template.name = "Шаблон для напоминаний об оценке мероприятия"
        template.text = "Оцените, пожалуйста, прошедшее мероприятие в меню Мероприятия/Запрошенные мероприятия."
        template.save()

    template_set = MessageTemplates.objects.filter(code = "payment_reminder")
    if template_set.count() == 0:
        template = MessageTemplates()
        template.code = "payment_reminder"
        template.name = "Шаблон для напоминаний об оплате"
        template.text = "Напоминаем, что вы сделали заявку, но еще не оплатили ее."
        template.save()
 
    template_set = MessageTemplates.objects.filter(code = "happy_birthday")
    if template_set.count() == 0:
        template = MessageTemplates()
        template.code = "happy_birthday"
        template.name = "Шаблон для поздравления с днем рождения"
        template.text = "Urbanius club поздравляет вас с Днем рождения"
        template.save()

    template_set = MessageTemplates.objects.filter(code = "random_coffee")
    if template_set.count() == 0:
        template = MessageTemplates()
        template.code = "random_coffee"
        template.name = "Шаблон для сообщений Random coffee"
        template.text = "В рамках Random coffee высыылаем вам контакт участника"
        template.save()

    template_set = MessageTemplates.objects.filter(code = "send_confirm_event")
    if template_set.count() == 0:
        template = MessageTemplates()
        template.code = "send_confirm_event"
        template.name = "Шаблон для сообщения о подтверждении заявки на мероприятие"
        template.text = "Ваша заявка на мероприятие подтверждена. "\
                        "Вам высылаем код подттверждения для прохода на мероприятие. "\
                        "Также его вы можете получить в меню 'Мероприятия'"
        template.save()

    # create EventTypes
    event_type_set = EventTypes.objects.filter(code = "close")
    if event_type_set.count() == 0:
        event_type = EventTypes(code = "close", name = "Закрытое") 
        event_type.save()
    event_type_set = EventTypes.objects.filter(code = "club")
    if event_type_set.count() == 0:
        event_type = EventTypes(code = "club", name = "Клубное") 
        event_type.save()
    event_type_set = EventTypes.objects.filter(code = "open")
    if event_type_set.count() == 0:
        event_type = EventTypes(code = "open", name = "Открытое") 
        event_type.save()
except Exception:
    print("Can't load init data") 
    print(Exception)   
