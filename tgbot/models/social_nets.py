from django.db import models


class SocialNetSites(models.Model):
    name = models.CharField("Название сайта", max_length=50, blank=False)
    link = models.URLField("Ссылка", blank=False)
    def __str__(self):
        return str(self.name)
    class Meta:
        verbose_name_plural = 'Сайты соц. сетей' 
        verbose_name = 'Сайт соц. сети'
        ordering = ['name']

class SocialNets(models.Model):
    soc_net_site = models.ForeignKey(SocialNetSites, on_delete=models.CASCADE, verbose_name="Сайт соц. сети")
    link = models.URLField("Страница", blank=False)
    user = models.ForeignKey("User", on_delete=models.CASCADE, verbose_name="Пользователь")
    def __str__(self):
        return ": ".join([str(self.soc_net_site), str(self.link)])
    class Meta:
        verbose_name_plural = 'Страницы в соц. сети' 
        verbose_name = 'Страница в соц. сети'
        ordering = ['user']