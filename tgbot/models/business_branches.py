from django.db import models


class BusinessBranches(models.Model):
    title = models.CharField("Наименование отрасли", max_length=250, blank=False)

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name_plural = 'Отрасли бизнеса' 
        verbose_name = 'Отрасль бизнеса'
        ordering = ['id']