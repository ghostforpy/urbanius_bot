from typing import Union
from django.db import models
from django.db.models import Q
from django.apps import apps
from tgbot.models import User, NewUser

def inc():
    BN = apps.get_model('tgbot', 'BusinessNeeds')
    return BN.objects.all().count() + 1

class BusinessNeeds(models.Model):
    title = models.CharField("Наименование потребности", max_length=50, blank=False)
    order_number = models.IntegerField(
        "Порядковый номер в списке",
        default=inc
    )
    admin_aprooved = models.BooleanField(
        "Одобрено администратором",
        default=False
    )

    def __str__(self):
        return str(self.title)

    @classmethod
    def get_needs_by_user(cls, user: Union[User,NewUser]) -> "BusinessNeeds":
        if isinstance(user, User):
            return cls.objects.filter(
                Q(admin_aprooved=True) | Q(creators_tgbot_users__in=[user])
            ).distinct()
        elif isinstance(user, NewUser):
            return cls.objects.filter(
                Q(admin_aprooved=True) | Q(creators_tgbot_newusers__in=[user])
            ).distinct()



    class Meta:
        verbose_name_plural = 'Потребности бизнеса' 
        verbose_name = 'Потребность бизнеса'
        ordering = ['order_number', 'id']
