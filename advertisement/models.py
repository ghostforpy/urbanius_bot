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
    admin_aprooved = models.BooleanField(
        "Одобрено администратором",
        default=False
    )
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    create_done = models.BooleanField("Создание закончено", default=False)

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


class AdvertisementImage(models.Model):
    adv = models.ForeignKey(
        Advertisement, 
        on_delete=models.CASCADE,
        verbose_name="Изображение рекламного сообщения",
        related_name="images"
    )
    image = models.ImageField(
        "Прикрепленное изображение", upload_to='advertisement_files', null=True, blank=True
    )
    image_id = models.CharField(
        "id прикрепленного изображения", max_length=150, null=True, blank=True
    )

    class Meta:
        verbose_name_plural = 'Изображения рекламных сообщений'
        verbose_name = 'Изображение рекламного сообщения'
        ordering = ['id']


class AdvertisementVideo(models.Model):
    adv = models.ForeignKey(
        Advertisement, 
        on_delete=models.CASCADE,
        verbose_name="Видео рекламного сообщения",
        related_name="videos"
    )
    video = models.ImageField(
        "Прикрепленное видео", upload_to='advertisement_files', null=True, blank=True
    )
    video_id = models.CharField(
        "id прикрепленного видео", max_length=150, null=True, blank=True
    )

    class Meta:
        verbose_name_plural = 'Видео рекламных сообщений'
        verbose_name = 'Видео рекламного сообщения'
        ordering = ['id']