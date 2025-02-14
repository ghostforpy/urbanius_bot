import random
import telegram
from django.db import models
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.forms import TextInput, Textarea, NumberInput
from dtb.constants import StatusCode

# from dtb.settingsa import DEBUG
# from django.conf import settings

from .models import *
from tgbot.forms import BroadcastForm
from tgbot.handlers import utils
from sheduler.models import MessagesToSend


@admin.register(Offers)
class OffersAdmin(admin.ModelAdmin): 
    readonly_fields = ['created_at',]
    list_display = [
        'offer', 'user', 'from_user',
    ]

class IncomeOffersInline(admin.TabularInline):
    model = Offers
    fk_name = "user"
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':50})},
    }

class OutputOffersInline(admin.TabularInline):
    model = Offers
    fk_name = "from_user"
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':50})},
    }

class SocialNetsInline(admin.TabularInline):
    model = SocialNets

class UsertgGroupsInline(admin.TabularInline):
    model = UsertgGroups

class UserReferrersInline(admin.TabularInline):
    model = UserReferrers
    fk_name = "user"

@admin.register(User)
class UserAdmin(admin.ModelAdmin):   
    readonly_fields = ['avatar_tag','user_id', 'username', 'deep_link'] # Be sure to read only mode
    list_display = [
        'user_id', 'username', 'first_name', 'last_name', 
        'created_at',  'is_blocked_bot', "random_coffe_on", 'comment'
    ]
    list_display_links = ['user_id', 'username', 'first_name', 'last_name']
    list_filter = ["is_blocked_bot", "is_banned", "random_coffe_on", "status",] 
    search_fields = ('username', 'user_id', 'first_name', 'last_name', 'sur_name')
    fields = [('user_id', 'username', 'deep_link'), 
              ('last_name', 'first_name', 'sur_name', 'date_of_birth'), 
              ('avatar_tag', 'main_photo', 'telefon', 'email'),
              ('status', 'rating'),
              ('is_blocked_bot', 'is_banned', 'is_admin', 'is_moderator'),
              ("verified_by_security", "random_coffe_on", "resident_urbanius_club",),
              ('company', 'job', 'branch', 'inn'),
              ('citi', 'job_region', 'site', 'number_of_employees'),
              ('segment', 'company_turnover'),
              ('business_needs', 'created_business_needs'),
              ('business_benefits', 'created_business_benefits'),
              ('business_branches'),
               'about',
               'sport',
               'hobby',
               'tags',
               'needs',
               'comment'
              ]
    inlines = [
        IncomeOffersInline, 
        OutputOffersInline,
        UsertgGroupsInline, 
        SocialNetsInline, 
        UserReferrersInline
    ]
    formfield_overrides = {
        models.IntegerField: {'widget': NumberInput(attrs={'size':'20'})},
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':100})},
    }
    actions = ['broadcast', 'reg_confirm']

    def invited_users(self, obj):
        return obj.invited_users().count()

    @admin.action(description='Разослать сообщения')
    def broadcast(self, request, queryset):
        """ Select users via check mark in django-admin panel, then select "Broadcast" to send message"""
        if 'apply' in request.POST:
            broadcast_message_text = request.POST["broadcast_text"]

            for user in queryset:
                new_mess = MessagesToSend()
                new_mess.receiver = user  
                new_mess.text = broadcast_message_text
                new_mess.save()
            self.message_user(request, "Broadcasting of %d messages has been started" % len(queryset))

            return HttpResponseRedirect(request.get_full_path())

        form = BroadcastForm(initial={'_selected_action': queryset.values_list('user_id', flat=True)})
        return render(
            request, "admin/broadcast_message.html", {'items': queryset,'form': form, 'title':u' '}
        )
    
    @admin.action(description='Подтвердить регистрацию')
    def reg_confirm(self, request, queryset):
        """ Select users via check mark in django-admin panel, then select "Broadcast" to send message"""
        if 'apply' in request.POST:
            broadcast_message_text = request.POST["broadcast_text"]
            # снимаем блокировку
            for u in queryset:
                u.is_blocked_bot = False
                u.status =  Status.objects.get(code = StatusCode.GROUP_MEMBER)
                u.comment = "Регистрация подтверждена"
                u.save()
                for user in queryset:
                    new_mess = MessagesToSend()
                    new_mess.receiver = user  
                    new_mess.text = broadcast_message_text
                    new_mess.save()
            # TODO: for all platforms?
            self.message_user(request, "Broadcasting of %d messages has been started" % len(queryset))

            return HttpResponseRedirect(request.get_full_path())
        text = "Ваша регистрация подтверждена. Наберите /start для обновления меню."
        form = BroadcastForm(initial={"broadcast_text":text,'_selected_action': queryset.values_list('user_id', flat=True)})
        return render(
            request, "admin/confirm_registration.html", {'items': queryset,'form': form, 'title':u' '}
        )


@admin.register(NewUser)
class NewUserAdmin(admin.ModelAdmin) :
    list_display = ('user_id', 'username', 'first_name', 'last_name','registered' ) 
    list_display_links = ('user_id', 'username', 'first_name', 'last_name',) 
    search_fields = ('user_id', 'username', 'first_name', 'last_name',)
    list_filter = ["registered", ] 


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    readonly_fields = ["code"]
    list_display = ("code", "name",) 
    list_display_links = ("name", ) 
    search_fields = ("name",)

@admin.register(BusinessNeeds)
class BusinessNeedsAdmin(admin.ModelAdmin):
    list_display = ("title", "order_number", "admin_aprooved",)
    list_editable =("order_number", "admin_aprooved",)
    fields = (
        "title", "order_number",
        "admin_aprooved", 
        # "creators_tgbot_users", 
        # "tgbot_user_related", "creators_tgbot_newuser_related", "tgbot_newuser_related"
        )

@admin.register(BusinessBenefits)
class BusinessBenefitsAdmin(admin.ModelAdmin):
    list_display = ("title", "order_number", "admin_aprooved",)
    list_editable =("order_number", "admin_aprooved",)
    fields = (
        "title", "order_number",
        "admin_aprooved", 
        # "creators_tgbot_user_related", 
        # "tgbot_user_related", "creators_tgbot_newuser_related", "tgbot_newuser_related"
        )

@admin.register(BusinessBranches)
class BusinessBranchesAdmin(admin.ModelAdmin):
    list_display = ("title", "order_number") 
    list_editable =("order_number",)

@admin.register(tgGroups)
class tgGroupsAdmin(admin.ModelAdmin) :
    list_display = ("name", "chat_id", "link", "show_for_users", "send_new_users", "send_advertisements",) 
    list_display_links = ("name", )
    list_editable =("show_for_users", "send_new_users", "send_advertisements",)
    search_fields = ("name",)
    readonly_fields = ["file_id"]
    
@admin.register(UsersRatings)
class UsersRatingsAdmin(admin.ModelAdmin) :
    list_display = ("user","rating","comment","created_at") 
    list_display_links = ("user","rating","comment") 
    search_fields = ("user","rating")

# @admin.register(UserActionLog)
# class UserActionLogAdmin(admin.ModelAdmin):
#     list_display = ['user', 'action', 'created_at']


# @admin.register(Config)
# class ConfigAdmin(admin.ModelAdmin):
#     list_display = ['param_name', 'param_val']
