from django.db import models
from django.apps import apps


def inc():
    BN = apps.get_model('tgbot', 'BusinessNeeds')
    return BN.objects.all().count() + 1

class BusinessNeeds(models.Model):
    title = models.CharField("Наименование потребности", max_length=50, blank=False)
    order_number = models.IntegerField(
        "Порялковый номер в списке",
        default=inc
    )

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name_plural = 'Потребности бизнеса' 
        verbose_name = 'Потребность бизнеса'
        ordering = ['order_number', 'id']
