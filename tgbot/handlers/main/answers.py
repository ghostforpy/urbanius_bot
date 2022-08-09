
from tgbot.models import User
from tgbot.handlers.keyboard import make_keyboard

EMPTY = {}
CANCEL = {"cancel":"Отмена"}
CANCEL_SKIP = {"cancel":"Отмена","skip":"Пропустить"}
OK = {"ok":"OK"}
START = {"start":"/start"}
YES_NO = {"yes":"Да", "no":"Нет"}

TO_ADMINS = {"to_admins":"Сообщение администраторам"}

START_MENU_FULL = {
        "find_members":"Поиск участников",
        "profile":"Профиль пользователя",
        "to_admins":"Сообщение администраторам",
        "payment":"Оплатить подписку"
    }

START_MENU_SHORT = {
        "profile":"Профиль пользователя",
        "to_admins":"Сообщение администраторам"
    }

def get_start_menu(user: User):
    if user.is_banned:
        return make_keyboard(TO_ADMINS,"usual",1)
    elif user.is_blocked_bot:
        return  make_keyboard(START_MENU_SHORT,"inline",1)       
    else:
        return  make_keyboard(START_MENU_FULL,"inline",1)
