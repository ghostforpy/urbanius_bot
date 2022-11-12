from typing import Union
from django.db import models
from django.db.models import Q
from django.apps import apps
from tgbot.models import User, NewUser


def inc():
    BB = apps.get_model('tgbot', 'BusinessBenefits')
    return BB.objects.all().count() + 1


class BusinessBenefits(models.Model):
    title = models.CharField("Наименование пользы", max_length=250, blank=False)
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
    def get_benefits_by_user(cls, user: Union[User,NewUser]) -> "BusinessBenefits":
        if isinstance(user, User):
            return cls.objects.filter(
                Q(admin_aprooved=True) | Q(creators_tgbot_users__in=[user])
            ).distinct()
        elif isinstance(user, NewUser):
            return cls.objects.filter(
                Q(admin_aprooved=True) | Q(creators_tgbot_newusers__in=[user])
            ).distinct()
    
    class Meta:
        verbose_name_plural = 'Пользы бизнеса' 
        verbose_name = 'Польза бизнеса'
        ordering = ['order_number', 'id']
