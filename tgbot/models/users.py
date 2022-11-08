# -*- coding: utf-8 -*-

from django.db.models import Q, Avg

from typing import Tuple

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from tgbot.utils import mystr, extract_user_data_from_update
from .utils import get_model_text
from .referrers import UserReferrers
from .offers import Offers
from .tg_groups import UsertgGroups
from .social_nets import SocialNets


class AbstractTgUser(models.Model):
    COMPANY_TURNOVERS_CHOISES = [
        ("under 50 millions", "До 50 млн. руб."),
        ("from 50 to 350 millions", "От 50 до 350 млн. руб."),
        ("from 350 millions to 1 billion", "От 350 млн. до 1 млрд. руб."),
        ("from 1 to 5 billions", "От 1 до 5 млрд. руб."),
        ("more then 5 billions", "Свыше 5 млрд. руб."),
    ]
    COMPANY_NUMBER_OF_EMPLOYESS_CHOISES = [
        ("under 10 employess", "До 10 человек"),
        ("from 10 to 50 employess", "От 10 до 50 человек"),
        ("from 50 to 500 employess", "От 50 человек до 500"),
        ("more then 500 employess", "От 500 и более"),
    ]

    # Личная инфо:
    user_id = models.BigIntegerField(primary_key=True)
    username = models.CharField("Телеграм логин",max_length=32, null=True, blank=True)
    last_name = models.CharField("Фамилия", max_length=256, null=True, blank=True)
    first_name = models.CharField("Имя", max_length=256)
    email = models.EmailField("E-mail", max_length=100, null=True, blank=True)
    telefon = models.CharField("Телефон", max_length=13, null=True, blank=True)
    sur_name = models.CharField("Отчество", max_length=150, null=True, blank=True)
    date_of_birth = models.DateField("Дата рождения", null=True, blank=True)
    main_photo = models.ImageField("Основное фото", upload_to='user_fotos', null=True, blank=True)
    main_photo_id = models.CharField("id основного фото", max_length=150, null=True, blank=True)

    # Бизнес инфо:
    company = models.CharField("Компания", max_length=150, null=True, blank=True)
    job = models.CharField("Должность", max_length=150, null=True, blank=True)
    branch = models.CharField("Отрасль", max_length=150, null=True, blank=True)
    citi = models.CharField("Город", max_length=150, null=True, blank=True)
    job_region = models.CharField("Регион присутствия", max_length=150, null=True, blank=True)
    site = models.CharField("Сайт", max_length=150, null=True, blank=True)
    resident_urbanius_club = models.BooleanField("Член клуба URBANIUS CLUB", default=False)
    business_club_member = models.CharField("Членство в бизнес клубах", max_length=150, null=True, blank=True)
    business_needs = models.ManyToManyField(
        "BusinessNeeds",
        verbose_name=_("Потребности бизнеса"),
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",
        blank=True
    )
    # turnover =  models.IntegerField("Оборот компании",default=0 , null=True, blank=True)
    number_of_employees = models.CharField(
        _("Численность сотрудников"),
        max_length=50,
        default="under 10 employess",
        choices=COMPANY_NUMBER_OF_EMPLOYESS_CHOISES
    )
    company_turnover = models.CharField(
        _("Оборот компании в год"),
        max_length=50,
        default="under 50 millions",
        choices=COMPANY_TURNOVERS_CHOISES
    )

    # О себе:
    about = models.TextField("О себе", null=True, blank=True)

    # Дополнительные поля
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    language_code = models.CharField(max_length=8, null=True, blank=True, help_text="Telegram client's lang")
    deep_link = models.CharField("Рекомендательная сылка", max_length=64, null=True, blank=True)
    registered = models.BooleanField("Зарегистрирован", default=False)

    class Meta:
        abstract = True

    def __str__(self):
        res = f'@{self.username}' if self.username is not None else f'{self.user_id}'
        res = " ".join([res, str(self.first_name), str(self.last_name)])
        return res

class NewUser(AbstractTgUser):
    # business_needs = models.ManyToManyField(
    #     "business_needs",
    #     verbose_name=_("Потребност бизнеса"),
    #     related_name="new_users",
    #     blank=True,
    # )
    class Meta:
        verbose_name = 'Новый пользователь'
        verbose_name_plural = 'Новые пользователи'

class User(AbstractTgUser):
    # Личная инфо:
    status = models.ForeignKey("Status", on_delete=models.PROTECT, verbose_name="Статус",null=True, blank=True)
    rating = models.IntegerField("Итоговый ретинг", default=3, null=True, blank=True)

    is_blocked_bot = models.BooleanField("Заблокирован", default=False)
    is_banned = models.BooleanField("Забанен", default=False)
    is_admin = models.BooleanField("Администратор",default=False)
    is_moderator = models.BooleanField("Модератор",default=False)
    random_coffe_on = models.BooleanField("Подключено Random coffee",default=False)
    verified_by_security = models.BooleanField("Проверен службой безопасности",default=False)
    # Бизнес инфо:
    # business_needs = models.ManyToManyField(
    #     "business_needs",
    #     verbose_name=_("Потребност бизнеса"),
    #     related_name="users",
    #     blank=True,
    # )
    inn = models.CharField("ИНН", max_length=12, null=True, blank=True)
    segment = models.CharField("Сегмент", max_length=150, null=True, blank=True)
    # turnover =  models.IntegerField("Оборот компании",default=0 , null=True, blank=True)
    
    # О себе:
    sport = models.TextField("Спорт", null=True, blank=True)
    hobby = models.TextField("Хобби", null=True, blank=True)
    tags = models.TextField("Тэги",  null=True, blank=True)
    needs = models.TextField("Потребности", null=True, blank=True)
    comment = models.TextField("комментарий", null=True, blank=True)

    # Дополнительные поля
    updated_at = models.DateTimeField("Изменен", auto_now=True)

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
 
    avatar_tag.short_description = 'Основное фото preview'

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
            Q(segment__icontains = keywords)| \
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
        res += f"<b>Рейтинг:</b> {mystr(self.rating)}\n"
        res += f"<b>Отрасль:</b> {mystr(self.branch)}\n"
        res += f"<b>Компания:</b> {mystr(self.company)}\n"
        res += f"<b>Сегмент:</b> {mystr(self.segment)}\n" 
        res += f"<b>Оборот:</b> {mystr(self.turnover)}\n"
        res += f"<b>Должность:</b> {mystr(self.job)}\n"
        res += f"<b>Сайт:</b> {mystr(self.site)}\n"
        res += f"<b>ИНН:</b> {mystr(self.inn)}\n"
        res += f"<b>Регион работы:</b> {mystr(self.job_region)}\n" 
        res += f"<b>Теги:</b> {mystr(self.tags)}\n"
        res += f"<b>Потребности:</b> {mystr(self.needs)}\n"
        offers = get_model_text(Offers,["NN","offer","image"], self)
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
        res += "\n  <b>Дата рождения:</b> " + mystr(self.date_of_birth)
        res += "\n  <b>Статус:</b> " + mystr(self.status)
        res += "\n  <b>Рейтинг:</b> " + mystr(self.rating)
        res += "\n  <b>Группы:</b>\n    " + get_model_text(UsertgGroups,["group"], self).replace("\n", "\n    ")
        res += "\n<b>Бизнес информация:</b> "
        res += "\n  <b>Компания:</b> " + mystr(self.company)
        res += "\n  <b>Сегмент:</b>  " + mystr(self.segment) 
        res += "\n  <b>Оборот:</b>  " + mystr(self.turnover) 
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
        res = res[:-2] + "<b>Тэги:</b> " + mystr(self.tags)
        res += "\n<b>Предложения:</b>\n" + get_model_text(Offers,["NN","offer","image"], self)
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


    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'