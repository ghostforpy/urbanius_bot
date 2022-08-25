
from tgbot.models import User
from sheduler.models import MessageTemplates
from dtb.constants import MessageTemplatesCode

ASK_REENTER = "Пожалуйста, используйте доступные пункты меню."  

# Стартовый диалог
WELCOME = "Добрый день! Вы находитесь в Telegram боте URBANIUS CLUB. \n" \
          "Используйте кнопки меню для работы с ботом." 
AFFILATE_MESS = "Если вы хотите видеть своего коллегу/партнера/друга в нашем сообществе "\
                "и готовы его рекомендовать и ручаться, перешлите ему ссылку-приглашение. " \
                "Если он пройдет по ней регистрацию, то Вы будете указаны у него в рекомендателях, "\
                "а Вам это учтется в рейтинге \n"

def get_start_mess(user: User):
    if user.is_banned:
        mess_template = MessageTemplates.objects.get(code = MessageTemplatesCode.WELCOME_BANNED_USR_MESSAGE)
        res = mess_template.text + user.comment
    elif user.is_blocked_bot:
        mess_template = MessageTemplates.objects.get(code = MessageTemplatesCode.WELCOME_BLOCKERD_USR_MESSAGE)
        res =  mess_template.text + user.comment
    else:
        mess_template = MessageTemplates.objects.get(code = MessageTemplatesCode.WELCOME_MESSAGE)
        res =  mess_template.text

    if not user.username:
        res += "\n<b>У Вас в Телеграм не введено имя пользователя. " \
               "Это может затруднить общение с вами. Введите его в настройках Телеграм</b>" 
    if not user.status:
        res += "\n<b>Вам не присвоен статус пользователя. " \
               "Многие функции бота работать не будут. Сообщите об этом администраторам</b>" 

    return res 

# Отправка сообщения админам
SENDING_WELCOME = "Вы в режиме отправки сообщения администраторам"
SENDING_CANCELED = "Отправка сообщения отменена"
NO_ADMIN_GROUP = 'Группа "Администраторы" не найдена или не указан ее чат. Сообщите об ошибке'
ASK_MESS = "Введите текст сообщения"
MESS_SENDED = "Сообщение отослано"
# Обработка Random coffee 
COFFE_WELCOME = "Вы в режиме переключения Random coffee"
COFFE_CANCELED = "Переключение Random coffee завершено"
ASK_OFF_COFFE = "В данный момент услуга Random coffee подключена"
ASK_ON_COFFE = "В данный момент услуга Random coffee отключена"
COFFE_ON = "Переключение Random coffee завершено. Услуга Random coffee подключена"
COFFE_OFF = "Переключение Random coffee завершено. Услуга Random coffee отключена"
