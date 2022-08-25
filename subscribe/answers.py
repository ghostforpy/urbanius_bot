
from tgbot.models import User
from subscribe.models import ClubPackages

EMPTY = {}
CANCEL = {"cancel":"Отмена"}
CANCEL_SKIP = {"cancel":"Отмена","skip":"Пропустить"}
OK = {"ok":"OK"}
YES_NO = {"yes":"Да", "no":"Нет"}
BACK = {"back":"Вернуться в основное меню"} #
BACK_PKG_LST = {"back_lst":"Вернуться к списку пакетов"} #

def pkg_mnu():
  mnu = {}
  pkg_set = ClubPackages.objects.all()
  for pkg in pkg_set:
    mnu[pkg.pk] = pkg.name
  return mnu