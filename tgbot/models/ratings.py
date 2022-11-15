from django.db import models


class UsersRatings(models.Model):
    rating = models.IntegerField("Оценка пользователя", default=3, null=True, blank=True)
    comment = models.TextField("Комментарий к оценке", null=True, blank=True)
    created_at = models.DateTimeField("Создана", auto_now_add=True)
    user = models.ForeignKey("User", on_delete=models.CASCADE, verbose_name="Пользователь")

    def __str__(self):
        return str(str(self.rating) + ", " + str(self.comment))
    class Meta:
        verbose_name_plural = 'Оценки пользователей' 
        verbose_name = 'Оценка пользователя' 
        ordering = ['user', 'rating'] 