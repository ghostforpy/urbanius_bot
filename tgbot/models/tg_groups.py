from django.db import models
# from tgbot.handlers import fill_file_id

class tgGroups(models.Model):
    name = models.CharField("Группа пользователей",unique=False, max_length=150, blank=False)
    chat_id = models.BigIntegerField("ИД чата в Телеграм", null=True)
    link = models.CharField("Ссылка на группу",unique=False, max_length=150, blank=True, null=True)
    text = models.TextField("Описание группыt", blank = True, null = True)
    for_all_users = models.BooleanField("Для всех пользователей", default=False)
    file = models.FileField("Фото/Видео", blank=True, null=True, upload_to="events")
    file_id = models.CharField("file_id", unique=False, max_length=255, blank=True, null = True)
    show_for_users = models.BooleanField("Показывать пользователям", default=False)

    def __str__(self):
        return self.name

    # def save(self, *args, **kwargs) -> None:
    #     fill_file_id(self, "file", text = "send_mess_by_tmplt")
    #     return super().save(*args, **kwargs)

    @classmethod
    def get_group_by_name(cls, gr_name: str) -> "tgGroups":
        return cls.objects.filter(name = gr_name).first()

    class Meta:
        verbose_name_plural = 'Группы пользователей' 
        verbose_name = 'Группа пользователей'
        ordering = ['name']

class UsertgGroups(models.Model):
    group = models.ForeignKey(tgGroups,on_delete=models.CASCADE, verbose_name="Группа")
    user = models.ForeignKey("User", on_delete=models.CASCADE, verbose_name="Пользователь")
    def __str__(self):
        return str(self.group)

    class Meta:
        verbose_name_plural = 'Группы пользователя' 
        verbose_name = 'Группа пользователя' 
        ordering = ['user', 'group']