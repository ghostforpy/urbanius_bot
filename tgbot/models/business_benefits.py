from django.db import models


class BusinessBenefits(models.Model):
    title = models.CharField("Наименование пользы", max_length=250, blank=False)

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name_plural = 'Пользы бизнеса' 
        verbose_name = 'Польза бизнеса'
        ordering = ['id']