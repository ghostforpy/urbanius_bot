
from tgbot.models import User
from tgbot.handlers.keyboard import make_keyboard

EMPTY = {}
CANCEL = {"back-from-groups": "Назад"}
CANCEL_SKIP = {"cancel":"Отмена","skip":"Пропустить"}
SKIP = {"skip":"Пропустить"}
OK = {"ok":"OK"}
START = {"start":"/start"}
FINISH = {"finish":"Завершить"}
YES_NO = {"yes":"Да", "no":"Нет"}
CHANGE_SKIP = {"change":"Изменить", "skip":"Пропустить"}
BACK = {"back":"Вернуться в основное меню"} 

FIND = {
    "find_groups":{
        "label": "Найти группы",
        "type": "switch_inline",
        "switch_inline_query_current_chat": "chats"
        }
    }

OTHER_GROUPS = {
    "groups":{
        "label": "🗃 Другие группы",
        "type": "switch_inline",
        "switch_inline_query_current_chat": "chats"
    }
}