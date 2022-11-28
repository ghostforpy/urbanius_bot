from django.db import models
from django.utils.timezone import now
from datetime import timedelta
# Create your models here.
class Advertisement(models.Model):
    essence = models.TextField("Суть предложения", max_length=900, blank=False)
    author = models.ForeignKey(
        "tgbot.User",
        on_delete=models.CASCADE,
        verbose_name="Автор"
    )
    file = models.FileField(
        "Прикрепленный файл", upload_to='advertisement_files', null=True, blank=True
    )
    file_id = models.CharField(
        "id прикрепленного файла", max_length=150, null=True, blank=True
    )
    admin_aprooved = models.BooleanField(
        "Одобрено администратором",
        default=False
    )
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Рекламные предложения' 
        verbose_name = 'Рекламное предложение'
        ordering = ['id']
    
    @classmethod
    def get_advertisements_by_user(cls, user):
        return cls.objects.filter(author=user)
    
    @classmethod
    def get_advertisements_by_user_in_time(cls, user, days=30):
        return cls.objects.filter(
            author=user,
            created_at__gte=now()-timedelta(days=days)
        )


