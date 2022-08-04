
from tgbot.models import User

ASK_REENTER = "Пожалуйста, используйте доступные пункты меню."  

# Стартовый диалог
ACCOUNT_BLOCKED = "К сожалению Ваша учетная запись все еще заблокирована по причине '{}'. " \
                  "Ожидайте разблокировки записи или свяжитесь с администраторами. " \
                  "Вы пока можете использовать бота в ограниченном режиме" 

ACCOUNT_BANNED = "К сожалению Вашу учетная запись забанили по причине '{}'. " \
                  "Для выяснения причин свяжитесь с администраторами. "                  

WELCOME = "Добрый день! Вы находитесь в Telegram боте URBANIUS CLUB. \n" \
          "Используйте кнопки меню для работы с ботом." 

def get_start_mess(user: User):
    if user.is_banned:
        return ACCOUNT_BANNED.format(user.comment)
    elif user.is_blocked_bot:
        return  ACCOUNT_BLOCKED.format(user.comment)      
    else:
        return  WELCOME    

# Отправка сообщения админам
SENDING_CANCELED = "Отправка сообщения отменена"
NO_ADMIN_GROUP = 'Группа "Администраторы" не найдена или не указан ее чат. Сообщите об ошибке'
ASK_MESS = "Введите текст сообщения"
MESS_SENDED = "Сообщение отослано"
