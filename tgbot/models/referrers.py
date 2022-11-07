from django.db import models


class UserReferrers(models.Model):
    referrer = models.ForeignKey("User",on_delete=models.CASCADE, related_name="referrer", verbose_name="Рекомендатель")
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="userreferrers_set", verbose_name="Пользователь")
    def __str__(self):
        return str(self.referrer)
    class Meta:
        verbose_name_plural = 'Рекомендатели' 
        verbose_name = 'Рекомендатель' 
        ordering = ['user', 'referrer'] 