from tgbot.models import Status
from sheduler.models import Tasks, MessageTemplates
from events.models import EventTypes
import datetime
import os
from dtb import settings
import traceback 

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
    if not os.path.isdir(settings.BASE_DIR / "media/downloads"):
        os.mkdir(settings.BASE_DIR / "media/downloads")
    
    # create statuses
    status = Status.objects.filter(code = "admin").first()
    if not status:
        status = Status(code = "admin", name = "Администратор") 
        status.save()
    status = Status.objects.filter(code = "club_resident").first()
    if not status:
        status = Status(code = "club_resident", name = "Резидент закрытого клуба") 
        status.save()
    status = Status.objects.filter(code = "community_resident").first()
    if not status:
        status = Status(code = "community_resident", name = "Резидент сообщества") 
        status.save()
    status = Status.objects.filter(code = "group_member").first()
    if not status:
        status = Status(code = "group_member", name = "Участник группы") 
        status.save()

    #create Tasks
    task = Tasks.objects.filter(code = "random_coffee").first()
    if not task:
        task = Tasks()
        task.code = "random_coffee"
        task.name =  "Random coffee"
        task.time = datetime.time(9, 00, 00) # время запуска 9:00
        task.mon = True # по понедельникам
        task.is_active = True # активно 
        task.save()  

    task = Tasks.objects.filter(code = "send_messages").first()
    if not task:
        task = Tasks()
        task.code = "send_messages"
        task.name =  "Рассылка сообщений"
        task.interval = 10 # повторяется с интервалом 10 сек
        task.is_active = True # активно 
        task.save()       

    task = Tasks.objects.filter(code = "send_confirm_event").first()
    if not task:
        task = Tasks()
        task.code = "send_confirm_event"
        task.name =  "Рассылка подтверждений регистрацию"
        task.interval = 60 # повторяется с интервалом 60 сек
        task.is_active = True # активно 
        task.save()

    task = Tasks.objects.filter(code = "happy_birthday").first()
    if not task:
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

    task = Tasks.objects.filter(code = "payment_reminder").first()
    if not task:
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

    task = Tasks.objects.filter(code = "rating_reminder").first()
    if not task:
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

    task = Tasks.objects.filter(code = "reg_reminder").first()
    if not task:
        task = Tasks()
        task.code = "reg_reminder"
        task.name =  "Напоминание о продолжении регистрации"
        task.time = datetime.time(10, 40, 00) # время запуска
        task.mon = True # каждый день
        task.tue = True
        task.wed = True
        task.thu = True
        task.fri = True
        task.sat = True
        task.san = True
        task.is_active = True # активно 
        task.save()


    task = Tasks.objects.filter(code = "send_anonses").first()
    if not task:
        task = Tasks()
        task.code = "send_anonses"
        task.name =  "Рассылка анонсов мероприятий"
        task.time = datetime.time(10, 50, 00) # время запуска
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
    template = MessageTemplates.objects.filter(code = "reg_reminder").first()
    if not template:
        template = MessageTemplates()
        template.code = "reg_reminder"
        template.name = "Шаблон для напоминаний о продолжении регистрации"
        template.text = "Вы не завершили регистрацию в боте Urbanius Club. Для завершения регистрации введите комманду /start."
        template.save()

    template = MessageTemplates.objects.filter(code = "rating_reminder").first()
    if not template:
        template = MessageTemplates()
        template.code = "rating_reminder"
        template.name = "Шаблон для напоминаний об оценке мероприятия"
        template.text = "Оцените, пожалуйста, прошедшее мероприятие в меню Мероприятия/Запрошенные мероприятия."
        template.save()

    template = MessageTemplates.objects.filter(code = "payment_reminder").first()
    if not template:
        template = MessageTemplates()
        template.code = "payment_reminder"
        template.name = "Шаблон для напоминаний об оплате"
        template.text = "Напоминаем, что вы сделали заявку, но еще не оплатили ее."
        template.save()
 
    template = MessageTemplates.objects.filter(code = "happy_birthday").first()
    if not template:
        template = MessageTemplates()
        template.code = "happy_birthday"
        template.name = "Шаблон для поздравления с днем рождения"
        template.text = "Urbanius club поздравляет вас с Днем рождения"
        template.save()

    template = MessageTemplates.objects.filter(code = "random_coffee").first()
    if not template:
        template = MessageTemplates()
        template.code = "random_coffee"
        template.name = "Шаблон для сообщений Random coffee"
        template.text = "В рамках Random coffee высыылаем вам контакт участника"
        template.save()

    template = MessageTemplates.objects.filter(code = "send_confirm_event").first()
    if not template:
        template = MessageTemplates()
        template.code = "send_confirm_event"
        template.name = "Шаблон для сообщения о подтверждении заявки на мероприятие"
        template.text = "Ваша заявка на мероприятие подтверждена. "\
                        "Вам высылаем код подттверждения для прохода на мероприятие. "\
                        "Также его вы можете получить в меню 'Мероприятия'"
        template.save()

    template = MessageTemplates.objects.filter(code = "welcome_newuser_message").first()
    if not template:
        template = MessageTemplates()
        template.code = "welcome_newuser_message"
        template.name = "Шаблон для приветственного сообщения новому пользователю"
        template.text = "Поздравляем! Вы успешно зарегистрировались в системе URBANIUS. " \
                        "Информация передана администраторам." \
                        "Для использования полного набора функций Вам необходимо дождаться подтвержденя регистрации. " \
                        "О подтверждении регистрации мы вам сообщим. А пока можете в профиле пользователя исправить введенные и заполнить дополнительные данные"
        template.save()


    template = MessageTemplates.objects.filter(code = "welcome_message").first()
    if not template:
        template = MessageTemplates()
        template.code = "welcome_message"
        template.name = "0."
        template.text = "Добрый день! Вы находитесь в Telegram боте URBANIUS CLUB. \n" \
                        "Используйте кнопки меню для работы с ботом."
        template.save()

    template = MessageTemplates.objects.filter(code = "welcome_blockerd_usr_message").first()
    if not template:
        template = MessageTemplates()
        template.code = "welcome_blockerd_usr_message"
        template.name = "Шаблон сообщения при начале работы для неподдтвержденного(заблокированного) пользователя"
        template.text = "К сожалению Ваша учетная запись все еще заблокирована. " \
                        "Ожидайте разблокировки записи или свяжитесь с администраторами. " \
                        "Вы пока можете заполнить профиль . Причина блокировки: \n" 
        template.save()

    template = MessageTemplates.objects.filter(code = "welcome_banned_usr_message").first()
    if not template:
        template = MessageTemplates()
        template.code = "welcome_banned_usr_message"
        template.name = "Шаблон сообщения при начале работы для забаненого пользователя"
        template.text = "К сожалению Вашу учетная запись забанили. " \
                        "Для выяснения причин свяжитесь с администраторами. Причина бана: \n"   
        template.save()



    # create EventTypes
    event_type = EventTypes.objects.filter(code = "close").first()
    if not event_type:
        event_type = EventTypes(code = "close", name = "Закрытое")
        event_type.save()
    event_type = EventTypes.objects.filter(code = "club").first()
    if not event_type:
        event_type = EventTypes(code = "club", name = "Клубное") 
        event_type.save()
    event_type = EventTypes.objects.filter(code = "open").first()
    if not event_type:
        event_type = EventTypes(code = "open", name = "Открытое") 
        event_type.save()
except Exception as exc:
    print("Can't load init data") 
    print(exc) 
    print(traceback.format_exc())

