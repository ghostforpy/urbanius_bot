from tgbot.models import Status
from sheduler.models import Tasks, MessageTemplates
from events.models import EventTypes
from subscribe.models import ClubPackages
import datetime
import os
from django.conf import settings

from dtb.constants import *
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
    status = Status.objects.filter(code = StatusCode.ADMIN).first()
    if not status:
        status = Status(code =  StatusCode.ADMIN, name = "Администратор") 
        status.save()
    status = Status.objects.filter(code = StatusCode.APPLICANT).first()
    if not status:
        status = Status(code =  StatusCode.APPLICANT, name = "Соискатель") 
        status.save()
    status = Status.objects.filter(code = StatusCode.CLUB_RESIDENT).first()
    if not status:
        status = Status(code = StatusCode.CLUB_RESIDENT, name = "Резидент закрытого клуба") 
        status.save()
    status = Status.objects.filter(code = StatusCode.COMMUNITY_RESIDENT).first()
    if not status:
        status = Status(code = StatusCode.COMMUNITY_RESIDENT, name = "Резидент сообщества") 
        status.save()
    status = Status.objects.filter(code = StatusCode.GROUP_MEMBER).first()
    if not status:
        status = Status(code = StatusCode.GROUP_MEMBER, name = "Участник группы") 
        status.save()

    # create Club Packages (пакеты участия-виды подписок)
    status = ClubPackages.objects.filter(code = ClubPackagesCode.CLUB_MEMBER).first()
    if not status:
        status = ClubPackages(code =  ClubPackagesCode.CLUB_MEMBER, name = "Членство в клубе") 
        status.save()
    status = ClubPackages.objects.filter(code =  ClubPackagesCode.SOCNETS_TG).first()
    if not status:
        status = ClubPackages(code =  ClubPackagesCode.SOCNETS_TG, name = "Соцсети и чаты. Telegram") 
        status.save()
    status = ClubPackages.objects.filter(code =  ClubPackagesCode.CHAT_BOT).first()
    if not status:
        status = ClubPackages(code =  ClubPackagesCode.CHAT_BOT, name = "Чат бот") 
        status.save()
    status = ClubPackages.objects.filter(code =  ClubPackagesCode.EVENTS).first()
    if not status:
        status = ClubPackages(code =  ClubPackagesCode.EVENTS, name = "Мероприятия") 
        status.save()
    status = ClubPackages.objects.filter(code =  ClubPackagesCode.BUSINES).first()
    if not status:
        status = ClubPackages(code =  ClubPackagesCode.BUSINES, name = "Бизнес") 
        status.save()
    status = ClubPackages.objects.filter(code =  ClubPackagesCode.MEDIA_PR).first()
    if not status:
        status = ClubPackages(code =  ClubPackagesCode.MEDIA_PR, name = "Медиа и PR") 
        status.save()
    status = ClubPackages.objects.filter(code =  ClubPackagesCode.SOCNETS_FB_IG).first()
    if not status:
        status = ClubPackages(code =  ClubPackagesCode.SOCNETS_FB_IG, name = "Соцсети и чаты. FB и IG") 
        status.save()


    # create Tasks
    task = Tasks.objects.filter(code = TaskCode.RANDOM_COFFEE).first()
    if not task:
        task = Tasks()
        task.code = TaskCode.RANDOM_COFFEE
        task.name =  "Random coffee"
        task.time = datetime.time(9, 00, 00) # время запуска 9:00
        task.mon = True # по понедельникам
        task.is_active = True # активно 
        task.save()  

    task = Tasks.objects.filter(code = TaskCode.SEND_MESSAGES).first()
    if not task:
        task = Tasks()
        task.code = TaskCode.SEND_MESSAGES
        task.name =  "Рассылка сообщений"
        task.interval = 10 # повторяется с интервалом 10 сек
        task.is_active = True # активно 
        task.save()       

    task = Tasks.objects.filter(code = TaskCode.SEND_CONFIRM_EVENT).first()
    if not task:
        task = Tasks()
        task.code = TaskCode.SEND_CONFIRM_EVENT
        task.name =  "Рассылка подтверждений регистрацию"
        task.interval = 60 # повторяется с интервалом 60 сек
        task.is_active = True # активно 
        task.save()

    task = Tasks.objects.filter(code = TaskCode.HAPPY_BIRTHDAY).first()
    if not task:
        task = Tasks()
        task.code = TaskCode.HAPPY_BIRTHDAY
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

    task = Tasks.objects.filter(code = TaskCode.PAYMENT_REMINDER).first()
    if not task:
        task = Tasks()
        task.code = TaskCode.PAYMENT_REMINDER
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

    task = Tasks.objects.filter(code = TaskCode.RATING_REMINDER).first()
    if not task:
        task = Tasks()
        task.code = TaskCode.RATING_REMINDER
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

    task = Tasks.objects.filter(code = TaskCode.REG_REMINDER).first()
    if not task:
        task = Tasks()
        task.code = TaskCode.REG_REMINDER
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

    task = Tasks.objects.filter(code = TaskCode.SEND_ANONSES).first()
    if not task:
        task = Tasks()
        task.code = TaskCode.SEND_ANONSES
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

    task = Tasks.objects.filter(code = TaskCode.SEND_SPEC_OFFERS).first()
    if not task:
        task = Tasks()
        task.code = TaskCode.SEND_SPEC_OFFERS
        task.name =  "Рассылка спец. предложений"
        task.time = datetime.time(10, 55, 00) # время запуска
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
    template = MessageTemplates.objects.filter(code = MessageTemplatesCode.REG_REMINDER).first()
    if not template:
        template = MessageTemplates()
        template.code = MessageTemplatesCode.REG_REMINDER
        template.name = "Шаблон для напоминаний о продолжении регистрации"
        template.text = "Вы не завершили регистрацию в боте Urbanius Club. Для завершения регистрации введите комманду /start."
        template.save()

    template = MessageTemplates.objects.filter(code = MessageTemplatesCode.RATING_REMINDER).first()
    if not template:
        template = MessageTemplates()
        template.code = MessageTemplatesCode.RATING_REMINDER
        template.name = "Шаблон для напоминаний об оценке мероприятия"
        template.text = "Оцените, пожалуйста, прошедшее мероприятие в меню Мероприятия/Запрошенные мероприятия."
        template.save()

    template = MessageTemplates.objects.filter(code = MessageTemplatesCode.PAYMENT_REMINDER).first()
    if not template:
        template = MessageTemplates()
        template.code = MessageTemplatesCode.PAYMENT_REMINDER
        template.name = "Шаблон для напоминаний об оплате"
        template.text = "Напоминаем, что вы сделали заявку, но еще не оплатили ее."
        template.save()
 
    template = MessageTemplates.objects.filter(code = MessageTemplatesCode.HAPPY_BIRTHDAY).first()
    if not template:
        template = MessageTemplates()
        template.code = MessageTemplatesCode.HAPPY_BIRTHDAY
        template.name = "Шаблон для поздравления с днем рождения"
        template.text = "Urbanius club поздравляет вас с Днем рождения"
        template.save()

    template = MessageTemplates.objects.filter(code = MessageTemplatesCode.RANDOM_COFFEE).first()
    if not template:
        template = MessageTemplates()
        template.code = MessageTemplatesCode.RANDOM_COFFEE
        template.name = "Шаблон для сообщений Random coffee"
        template.text = "В рамках Random coffee высылаем вам контакт участника"
        template.save()

    template = MessageTemplates.objects.filter(code = MessageTemplatesCode.SEND_CONFIRM_EVENT).first()
    if not template:
        template = MessageTemplates()
        template.code = MessageTemplatesCode.SEND_CONFIRM_EVENT
        template.name = "Шаблон для сообщения о подтверждении заявки на мероприятие"
        template.text = "Ваша заявка на мероприятие подтверждена. "\
                        "Вам высылаем код подттверждения для прохода на мероприятие. "\
                        "Также его вы можете получить в меню 'Мероприятия'"
        template.save()

    template = MessageTemplates.objects.filter(code = MessageTemplatesCode.WELCOME_NEWUSER_MESSAGE).first()
    if not template:
        template = MessageTemplates()
        template.code = MessageTemplatesCode.WELCOME_NEWUSER_MESSAGE
        template.name = "Шаблон для приветственного сообщения новому пользователю"
        template.text = "Поздравляем! Вы успешно зарегистрировались в системе URBANIUS CLUB. " \
                        "Информация передана администраторам. " \
                        "Для использования полного набора функций Вам необходимо дождаться подтверждения регистрации. " \
                        "О подтверждении регистрации мы вам сообщим. А пока можете в профиле пользователя исправить введенные и заполнить дополнительные данные."
        template.save()


    template = MessageTemplates.objects.filter(code = MessageTemplatesCode.WELCOME_MESSAGE).first()
    if not template:
        template = MessageTemplates()
        template.code = MessageTemplatesCode.WELCOME_MESSAGE
        template.name = "Шаблон сообщения при начале работы для подтвержденного пользователя"
        template.text = "Добрый день! Вы находитесь в Telegram боте URBANIUS CLUB. \n" \
                        "Используйте кнопки меню для работы с ботом."
        template.save()

    template = MessageTemplates.objects.filter(code = MessageTemplatesCode.WELCOME_BLOCKERD_USR_MESSAGE).first()
    if not template:
        template = MessageTemplates()
        template.code = MessageTemplatesCode.WELCOME_BLOCKERD_USR_MESSAGE
        template.name = "Шаблон сообщения при начале работы для неподдтвержденного(заблокированного) пользователя"
        template.text = "К сожалению Ваша учетная запись все еще заблокирована. " \
                        "Ожидайте разблокировки записи или свяжитесь с администраторами. " \
                        "Вы пока можете заполнить профиль. Причина блокировки: \n" 
        template.save()

    template = MessageTemplates.objects.filter(code = MessageTemplatesCode.WELCOME_BANNED_USR_MESSAGE).first()
    if not template:
        template = MessageTemplates()
        template.code = MessageTemplatesCode.WELCOME_BANNED_USR_MESSAGE
        template.name = "Шаблон сообщения при начале работы для забаненого пользователя"
        template.text = "К сожалению Вашу учетная запись забанили. " \
                        "Для выяснения причин свяжитесь с администраторами. Причина бана: \n"   
        template.save()



    # create EventTypes
    event_type = EventTypes.objects.filter(code = EventTypeCode.CLOSE).first()
    if not event_type:
        event_type = EventTypes(code = EventTypeCode.CLOSE, name = "Закрытое")
        event_type.save()
    event_type = EventTypes.objects.filter(code = EventTypeCode.CLUB).first()
    if not event_type:
        event_type = EventTypes(code = EventTypeCode.CLUB, name = "Клубное") 
        event_type.save()
    event_type = EventTypes.objects.filter(code = EventTypeCode.OPEN).first()
    if not event_type:
        event_type = EventTypes(code = EventTypeCode.OPEN, name = "Открытое") 
        event_type.save()
except Exception as exc:
    print("Can't load init data") 
    print(exc) 
    print(traceback.format_exc())

