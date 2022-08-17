# -*- coding: utf-8 -*-

from random import random
from django.db.models import Q, Avg

from typing import Dict, Tuple

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

from tgbot.utils import mystr, extract_user_data_from_update

class Offers(models.Model):
    offer = models.TextField("Суть предложения", blank = True, null = True)
    image = models.FileField("Файл", blank=True, upload_to="offers")
    user = models.ForeignKey("User", on_delete=models.CASCADE, verbose_name="Пользователь")
    def __str__(self):
        return  self.offer
    class Meta:
        verbose_name_plural = 'Предложения' 
        verbose_name = 'Предложение' 
        ordering = ['user']

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

class Status(models.Model):
    code = models.CharField("Код", max_length=50, blank=True)
    name = models.CharField("Статус пользователя", unique=True, max_length=150, blank=False)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Статусы пользователя' 
        verbose_name = 'Статус пользователя' 
        ordering = ['name']

class tgGroups(models.Model):
    name = models.CharField("Группа пользователей",unique=False, max_length=150, blank=False)
    chat_id = models.BigIntegerField("ИД чата в Телеграм", null=True)
    link = models.CharField("Ссылка на группу",unique=False, max_length=150, blank=True, null=True)
    def __str__(self):
        return self.name

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


class UserReferrers(models.Model):
    referrer = models.ForeignKey("User",on_delete=models.CASCADE, related_name="referrer", verbose_name="Рекомендатель")
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="userreferrers_set", verbose_name="Пользователь")
    def __str__(self):
        return str(self.referrer)
    class Meta:
        verbose_name_plural = 'Рекомендатели' 
        verbose_name = 'Рекомендатель' 
        ordering = ['user', 'referrer'] 

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

class User(models.Model):
    # Личная инфо:
    user_id = models.BigIntegerField(primary_key=True)
    username = models.CharField("Телеграм логин",max_length=32, null=True, blank=True)
    last_name = models.CharField("Фамилия", max_length=256, null=True, blank=True)
    first_name = models.CharField("Имя", max_length=256)
    email = models.EmailField("E-mail", max_length=100, null=True, blank=True)
    telefon = models.CharField("Телефон", max_length=13, null=True, blank=True)
    sur_name = models.CharField("Отчество", max_length=150, null=True, blank=True)
    date_of_birth = models.DateField("Дата рождения", null=True, default=timezone.now)    
    main_photo = models.ImageField("Основное фото", upload_to='user_fotos', null=True, blank=True)
    main_photo_id = models.CharField("id основного фото", max_length=150, null=True, blank=True)
    status = models.ForeignKey(Status, on_delete=models.PROTECT, verbose_name="Статус",null=True, blank=True)
    rating = models.IntegerField("Итоговый ретинг", default=3, null=True, blank=True)

    is_blocked_bot = models.BooleanField("Заблокирован", default=False)
    is_banned = models.BooleanField("Забанен", default=False)
    is_admin = models.BooleanField("Администратор",default=False)
    is_moderator = models.BooleanField("Модератор",default=False)
    random_coffe_on = models.BooleanField("Подключено Random coffe",default=False)
    verified_by_security = models.BooleanField("Проверен службой безопасности",default=False)
    # Бизнес инфо:
    company = models.CharField("Компания", max_length=150, null=True, blank=True)
    job = models.CharField("Должность", max_length=150, null=True, blank=True)
    branch = models.CharField("Отрасль", max_length=150, null=True, blank=True)
    citi = models.CharField("Город", max_length=150, null=True, blank=True)
    job_region = models.CharField("Регион присутствия", max_length=150, null=True, blank=True)
    site = models.CharField("Сайт", max_length=150, null=True, blank=True)
    inn = models.CharField("ИНН", max_length=12, null=True, blank=True)
    # О себе:
    about = models.TextField("О себе", null=True, blank=True)
    sport = models.TextField("Спорт", null=True, blank=True)
    hobby = models.TextField("Хобби", null=True, blank=True)
    tags = models.TextField("Тэги",  null=True, blank=True)
    needs = models.TextField("Потребности", null=True, blank=True)
    comment = models.TextField("комментарий", null=True, blank=True)
    # Дополнительные поля

    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Изменен", auto_now=True)
    language_code = models.CharField(max_length=8, null=True, blank=True, help_text="Telegram client's lang")
    deep_link = models.CharField("Рекомендательная сылка", max_length=64, null=True, blank=True)

    
    def __str__(self):
        res = f'@{self.username}' if self.username is not None else f'{self.user_id}'
        res = " ".join([res, str(self.first_name), str(self.last_name)])
        return res

    def save(self, *args, **kwargs):
        import random
        self.rating = random.randint(0, 5)
        super(User, self).save(*args, **kwargs)
        
    # Here I return the avatar or picture with an owl, if the avatar is not selected
    def get_avatar(self):
        if not self.main_photo:
            return '/media/no_foto.jpg'
        return self.main_photo.url
 
    # method to create a fake table field in read only mode width="100" 
    def avatar_tag(self):
        return mark_safe('<img src="%s" height="150" />' % self.get_avatar())
 
    avatar_tag.short_description = 'Avatar'

    @classmethod
    def get_user_and_created(cls, update, context) -> Tuple["User", bool]:
        """ python-telegram-bot's Update, Context --> User instance """
        data = extract_user_data_from_update(update)
        u, created = cls.objects.update_or_create(user_id=data["user_id"], defaults=data)
 
        if created:
            u.is_blocked_bot = True
            u.comment = "Новый пользователь"
            if context is not None and context.args is not None and len(context.args) > 0:
                payload = context.args[0]
                if str(payload).strip() != str(data["user_id"]).strip():  # you can't invite yourself
                    u.deep_link = payload
                    u.save()
                    reffer = cls. get_user_by_username_or_user_id(str(payload).strip()) # Ищем рекомендателя и приписываем его пользователю
                    if reffer != None:
                        ur = UserReferrers(reffer, u)
                        ur.save()

        return u, created

    @classmethod
    def get_user(cls, update, context) -> "User":
        u, _ = cls.get_user_and_created(update, context)
        return u

    @classmethod
    def get_user_by_username_or_user_id(cls, string) -> "User":
        """ Search user in DB, return User or None if not found """
        username = str(string).replace("@", "").strip().lower()
        if username.isdigit():  # user_id
            return cls.objects.filter(user_id=int(username)).first()
        return cls.objects.filter(username__iexact=username).first()


    @classmethod
    def find_users_by_keywords(cls, keywords) -> list:
        """ осуществляет поиск участников, у которых в любом поле упоминаются ключевые слова """
        q = Q(username__icontains = keywords)| \
            Q(last_name__icontains = keywords)| \
            Q(first_name__icontains = keywords)| \
            Q(sur_name__icontains = keywords)| \
            Q(deep_link__icontains = keywords)| \
            Q(telefon__icontains = keywords)| \
            Q(email__icontains = keywords)| \
            Q(citi__icontains = keywords)| \
            Q(company__icontains = keywords)| \
            Q(job__icontains = keywords)| \
            Q(site__icontains = keywords)| \
            Q(tags__icontains = keywords)| \
            Q(needs__icontains = keywords)| \
            Q(about__icontains = keywords)| \
            Q(comment__icontains = keywords)| \
            Q(job_region__icontains = keywords)| \
            Q(branch__icontains = keywords)| \
            Q(status__name__icontains = keywords)| \
            Q(sport__icontains = keywords)| \
            Q(hobby__icontains = keywords)| \
            Q(offers__offer__icontains = keywords)| \
            Q(socialnets__link__icontains = keywords)| \
            Q(socialnets__soc_net_site__name__icontains = keywords)| \
            Q(usertggroups__group__name__icontains = keywords)|\
            Q(userreferrers_set__referrer__username__icontains = keywords)|\
            Q(userreferrers_set__referrer__last_name__icontains = keywords)
        users = cls.objects.filter(q).distinct()


        return users

    def short_profile(self)->str:
        res = ""
        res += f"<b>Логин телеграм:</b> @{mystr(self.username)}\n"
        res += f"<b>Имя:</b> {mystr(self.last_name)} {mystr(self.first_name)} {mystr(self.sur_name)}\n"
        res += f"<b>Статус:</b> {mystr(self.status)}\n"
        res += f"<b>Отрасль:</b> {mystr(self.branch)}\n"
        res += f"<b>Компания:</b> {mystr(self.company)}\n"
        res += f"<b>Должность:</b> {mystr(self.job)}\n"
        res += f"<b>Сайт:</b> {mystr(self.site)}\n"
        res += f"<b>ИНН:</b> {mystr(self.inn)}\n"
        res += f"<b>Регион работы:</b> {mystr(self.job_region)}\n"
        res += f"<b>Теги:</b> {mystr(self.tags)}\n"
        res += f"<b>Потребности:</b> {mystr(self.needs)}\n"
        offers = get_model_text(Offers,["NN","offer"], self)
        res += f"<b>Предложения:</b> \n{offers}"
        referers = get_model_text(UserReferrers,["NN","referrer"], self)
        res += f"<b>Рекомендатели:</b>\n{referers}"
        return res

    def full_profile(self)->str:
        res = "<b>Пользователь:</b> \n"
        res += str(self)        
        res += "\n<b>Личная информация:</b> "
        res += "\n  <b>e-mail:</b> " + mystr(self.email)
        res += "\n  <b>Телефон:</b> " + mystr(self.telefon)
        res += "\n  <b>Дата рождения:</b> " + self.date_of_birth.strftime("%d.%m.%Y")
        res += "\n  <b>Статус:</b> " + mystr(self.status)
        res += "\n  <b>Группы:</b>\n    " + get_model_text(UsertgGroups,["group"], self).replace("\n", "\n    ")
        res += "\n<b>Бизнес информация:</b> "
        res += "\n  <b>Компания:</b> " + mystr(self.company)
        res += "\n  <b>Должность:</b> " + mystr(self.job)
        res += "\n  <b>Отрасль:</b> " + mystr(self.branch)
        res += "\n  <b>Город:</b> " + mystr(self.citi)
        res += "\n  <b>Регион:</b> " + mystr(self.job_region)
        res += "\n  <b>Сайт:</b> " + mystr(self.site) + "\n"
        res += "\n<b>Информация о себе:</b> "
        res += "\n  <b>О себе:</b> " + mystr(self.about)
        res += "\n  <b>Спорт:</b> " + mystr(self.sport)
        res += "\n  <b>Хобби:</b> " + mystr(self.hobby)
        res += "\n  <b>Соцсети:</b>\n    " + get_model_text(SocialNets,["soc_net_site","link"], self).replace("\n", "\n    ")
        res += "<b>Тэги:</b> " + mystr(self.tags)
        res += "\n<b>Предложения:</b>\n" + get_model_text(Offers,["NN","offer"], self)
        res += "<b>Потребности:</b>\n" + mystr(self.needs)
        res += "\n<b>Рекомендатели:</b>\n" + get_model_text(UserReferrers,["NN","referrer"], self)  
        return res

    def get_users_rating(self):
        avg_rating_set = self.usersratings_set.aggregate(avg_rating = Avg("rating"))
        if avg_rating_set["avg_rating"]:
            res = int(avg_rating_set["avg_rating"])
        else:
            res = None
        return res
    # Получает число опубликованных в группах сообщений    
    def get_user_mess_count(self):
        return self.messagestatistic_set.count()

    # Получает число приглашенных пользователей
    def get_user_refferents_count(self):
        return self.referrer.count()

    def invited_users(self):  # --> User queryset 
        return User.objects.filter(deep_link=str(self.user_id), created_at__gt=self.created_at)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class MessagesToSend(models.Model):
    receiver = models.ForeignKey("User", on_delete=models.CASCADE, related_name="receiver", verbose_name="Получатель", blank=False, null=False)    
    text = models.TextField("Текст сообщения",unique=False, blank=False)
    created_at = models.DateTimeField("Создано в", auto_now_add=True)
    sended_at = models.DateTimeField("Отослано в", blank=True, null=True)
    sended = models.BooleanField("Отослано", default=False)
    recommended_friend = models.ForeignKey("User", on_delete=models.SET_NULL, related_name="recommended_friend", verbose_name="Рекомендованный друг по Random coffe", blank=True, null=True)
    file = models.FileField("Файл", blank=True, null=True, upload_to="messages")
    file_id = models.CharField("file_id", unique=False, max_length=255, blank=True, null = True)
    #photo = models.ImageField("Фото", blank=True, null=True, upload_to="messages")

    def __str__(self):
        return self.text
    class Meta:
        verbose_name_plural = 'Сообщения к отсылке' 
        verbose_name = 'Сообщение к отсылке' 
        ordering = ['created_at']


class MessageTemplates(models.Model):
    code = models.CharField("Код", max_length=256, null=False, blank=False)
    name = models.CharField("Название", max_length=256, null=False, blank=False)
    text = models.TextField("Текст сообщения", blank=False)
    file = models.FileField("Файл", blank=True, null=True, upload_to="templates")

    def __str__(self):
        return self.text
    class Meta:
        verbose_name_plural = 'Шаблоны сообщений' 
        verbose_name = 'Шаблон сообщения' 
        ordering = ['code']

class UserActionLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=128)
    text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"user: {self.user}, made: {self.action}, created at {self.created_at.strftime('(%H:%M, %d %B %Y)')}"

class Config(models.Model):
    """Модель настроек бота."""

    param_name = models.CharField(_('Наименование параметра'), max_length=255)
    param_val = models.TextField(_('Значение параметра'), null=True, blank=True)

    def __str__(self):
        return self.param_name

    class Meta:
        ordering = ['param_name']
        verbose_name = 'Параметр бота'
        verbose_name_plural = 'Параметры бота'

    @classmethod
    def load_config(cls) -> Dict[str, str]:
        config_params = cls.objects.all()
        result = {}
        for config_param in config_params:
            result[config_param.param_name] = config_param.param_val

        return result

# Получает из всех записей модели словарь 
# key - имя поля чье значение попадет в ключ, 
# value имя поля чье значение попадет в значение если "NN" то подставится порядковый номер
# parent значение родительской модели для выборки подчиненных элементов 
def get_model_dict(model, key: str, value: str, parent = None, filter = None):
    res = dict()
    if parent:
        model_set = getattr(parent,model._meta.model_name+"_set") # получаем выборку дочерних записей parent
    else:
        model_set = model.objects # получаем выборку записей
    
    if filter:
        model_set = model_set.filter(**filter)
    else:
        model_set = model_set.all()
    fields = value.split(",")
    str_num = 0
    for elem in model_set:
        str_num += 1
        val_list = []
        for field in fields:
            if field == "NN":
                val_list.append(str(str_num))
            else:
                val_list.append(str(getattr(elem, field.strip())))
        res[str(getattr(elem, key))] = ", ".join(val_list)
    return res

# Получает из всех записей текст 
# fields - список полей которые попадут в текст "NN" - спец поле будет подставляться номер строки
# parent значение родительской модели для выборки подчиненных элементов 
def get_model_text(model, fields: list, parent = None, filter = None ):
    res = ""
    if parent:
        model_set = getattr(parent,model._meta.model_name+"_set") # получаем выборку дочерних записей parent
    else:
        model_set = model.objects # получаем выборку записей
    
    if filter:
        model_set = model_set.filter(**filter)
    else:
        model_set = model_set.all()
    
    str_num = 0
    for elem in model_set:
        str_num += 1
        txt_str_lst = []
        for field in fields:
            if field == "NN":
                txt_str_lst.append(str(str_num)) 
            else:
                txt_str_lst.append(str(getattr(elem, field)))
        txt_str = ", ".join(txt_str_lst)+"\n"
        res += txt_str

    return res



