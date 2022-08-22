
from tgbot.models import User
from tgbot.handlers.keyboard import make_keyboard

EMPTY = {}
CANCEL = {"cancel":"Отмена"}
CANCEL_SKIP = {"cancel":"Отмена","skip":"Пропустить"}
OK = {"ok":"OK"}
START = {"start":"/start"}
YES_NO = {"yes":"Да", "no":"Нет"}

ON_OFF_CANCEL = {"on":"Включить Random coffee","off":"Выключить Random coffee","cancel":"Отмена"}

TO_ADMINS = {"to_admins":"Сообщение администраторам"}

START_MENU_FULL = {
        "random_coffee":"Random Coffee",
        "events":"Мероприятия",
        "find_members":"Найти участников",
        "profile":"Профиль пользователя",
        "messages":"Сообщения",
        "affiliate":"Партнерская программа",
        "payment":"Оплатить",
        "groups":"Группы"
    }

START_MENU_SHORT = {
        "profile":"Профиль пользователя",
        "to_admins":"Сообщение администраторам"
    }

def get_start_menu(user: User):
    if user.is_banned:
        return make_keyboard(TO_ADMINS,"inline",1)
    elif user.is_blocked_bot:
        return  make_keyboard(START_MENU_SHORT,"inline",1)       
    else:
        return  make_keyboard(START_MENU_FULL,"inline",1)


