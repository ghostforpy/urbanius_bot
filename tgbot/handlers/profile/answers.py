
from tgbot.models import User
from tgbot.handlers.keyboard import make_keyboard

EMPTY = {}
CANCEL = {"cancel":"Отмена"}
CANCEL_SKIP = {"cancel":"Отмена","skip":"Пропустить"}
SKIP = {"skip":"Пропустить"}
OK = {"ok":"OK"}
START = {"start":"/start"}
YES_NO = {"yes":"Да", "no":"Нет"}
CHANGE_SAVE = {"change":"Изменить", "save":"Не менять"}
ADD_DEL_SAVE = {"add":"Добавить", "del":"Удалить", "save":"Не менять"}


PROF_MENU = {
                "fio":"Ф.И.О",
                "date_of_birth":"Дата рождения",   
                "main_photo":"Фотография",
                "telefon":"Телефон",
                "email":"e-mail",
                "citi":"Город",
                "company":"Компания",
                "job":"Должность",
                "site":"Web сайт",
                "tags":"Тэги",
                "about":"О себе",
                "job_region":"Регион присутствия",
                "branch":"Отрасль",
                "offers":"Предложения",
                "social_nets":"Соц. сети",
                "needs":"Потребности",
                "sport":"Спорт",
                "hobby":"Хобби",
                "referes":"Рекомендатели",
                "status":"Статус",
                "groups":"Группы",
                "back":"Вернуться в основное меню"
            }
