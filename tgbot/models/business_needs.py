from django.db import models


class BusinessNeeds(models.Model):
    title = models.CharField("Наименование потребности", max_length=50, blank=False)

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name_plural = 'Потребности бизнеса' 
        verbose_name = 'Потребность бизнеса'
        ordering = ['id']