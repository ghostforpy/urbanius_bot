import random
import telegram
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.forms import TextInput, Textarea

from dtb.settings import DEBUG

from .models import *
from tgbot.forms import BroadcastForm
from tgbot.handlers import utils


class OffersInline(admin.TabularInline):
    model = Offers
    formfield_overrides = {
        #models.CharField: {'widget': TextInput(attrs={'size':'20'})},
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':100})},
    }
    
class SocialNetsInline(admin.TabularInline):
    model = SocialNets

class UserNeedsInline(admin.TabularInline):
    model = UserNeeds

class UserSportInline(admin.TabularInline):
    model = UserSport

class UserHobbyInline(admin.TabularInline):
    model = UserHobby

class UsertgGroupsInline(admin.TabularInline):
    model = UsertgGroups

class UserReferrersInline(admin.TabularInline):
    model = UserReferrers
    fk_name = "user"

@admin.register(User)
class UserAdmin(admin.ModelAdmin):   
    readonly_fields = ['avatar_tag'] # Be sure to read only mode
    list_display = [
        'user_id', 'username', 'first_name', 'last_name', 
        'created_at',  'is_blocked_bot', "comment"
    ]
    list_filter = ["is_blocked_bot", "is_moderator"]
    search_fields = ('username', 'user_id', 'last_name')
    fields = [('user_id', 'username', 'deep_link'), 
              ('last_name', 'first_name', 'sur_name', 'date_of_birth'), 
              ('avatar_tag', 'main_photo', 'telefon', 'email'),
              ('status', 'club_groups'),
              ('is_blocked_bot', 'is_banned', 'is_admin', 'is_moderator'),
              ('job_region', 'citi', 'branch'), 
              ('company', 'job', 'site', 'tags'),
              'about',              
              'comment'
              ]
    inlines = [UsertgGroupsInline, OffersInline, SocialNetsInline, UserNeedsInline, UserSportInline, UserHobbyInline, UserReferrersInline]
    formfield_overrides = {
        #models.CharField: {'widget': TextInput(attrs={'size':'20'})},
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':100})},
    }
    actions = ['broadcast']

    def invited_users(self, obj):
        return obj.invited_users().count()

    def broadcast(self, request, queryset):
        """ Select users via check mark in django-admin panel, then select "Broadcast" to send message"""
        if 'apply' in request.POST:
            broadcast_message_text = request.POST["broadcast_text"]

            # TODO: for all platforms?
            if len(queryset) <= 3 or DEBUG:  # for test / debug purposes - run in same thread
                for u in queryset:
                    utils.send_message(user_id=u.id, text=broadcast_message_text, parse_mode=telegram.ParseMode.MARKDOWN)
                self.message_user(request, "Just broadcasted to %d users" % len(queryset))
            else:
                user_ids = list(set(u.user_id for u in queryset))
                random.shuffle(user_ids)
                #broadcast_message.delay(message=broadcast_message_text, user_ids=user_ids)
                self.message_user(request, "Broadcasting of %d messages has been started" % len(queryset))

            return HttpResponseRedirect(request.get_full_path())

        form = BroadcastForm(initial={'_selected_action': queryset.values_list('user_id', flat=True)})
        return render(
            request, "admin/broadcast_message.html", {'items': queryset,'form': form, 'title':u' '}
        )

@admin.register(Sport)
class SportAdmin(admin.ModelAdmin) :
    list_display = ("name",) 
    list_display_links = ("name", ) 
    search_fields = ("name",)

@admin.register(Hobby)
class HobbyAdmin(admin.ModelAdmin) :
    list_display = ("name",) 
    list_display_links = ("name", ) 
    search_fields = ("name",)

@admin.register(JobRegions)
class JobRegionsAdmin(admin.ModelAdmin) :
    list_display = ("name",) 
    list_display_links = ("name", ) 
    search_fields = ("name",)

@admin.register(Needs)
class NeedsAdmin(admin.ModelAdmin) :
    list_display = ("name",) 
    list_display_links = ("name", ) 
    search_fields = ("name",)

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin) :
    list_display = ("name",) 
    list_display_links = ("name", ) 
    search_fields = ("name",)

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin) :
    list_display = ("stat_id", "name",) 
    list_display_links = ("name", ) 
    search_fields = ("name",)

@admin.register(tgGroups)
class tgGroupsAdmin(admin.ModelAdmin) :
    list_display = ("name", "chat_id",) 
    list_display_links = ("name", ) 
    search_fields = ("name",)



# @admin.register(Location)
# class LocationAdmin(admin.ModelAdmin):
#     list_display = ['id', 'user_id', 'created_at']


# @admin.register(Arcgis)
# class ArcgisAdmin(admin.ModelAdmin):
#     list_display = ['location', 'city', 'country_code']


# @admin.register(UserActionLog)
# class UserActionLogAdmin(admin.ModelAdmin):
#     list_display = ['user', 'action', 'created_at']


# @admin.register(Config)
# class ConfigAdmin(admin.ModelAdmin):
#     list_display = ['param_name', 'param_val']
