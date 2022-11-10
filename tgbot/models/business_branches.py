from django.db import models
from django.apps import apps


def inc():
    BB = apps.get_model('tgbot', 'BusinessBranches')
    return BB.objects.all().count() + 1

class BusinessBranches(models.Model):
    title = models.CharField("Наименование отрасли", max_length=250, blank=False)
    order_number = models.IntegerField(
        "Порялковый номер в списке",
        default=inc
    )


    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name_plural = 'Отрасли бизнеса' 
        verbose_name = 'Отрасль бизнеса'
        ordering = ['order_number', 'id']
