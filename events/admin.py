from django.contrib import admin
from .models import *

@admin.register(EventTypes)
class EventTypesAdmin(admin.ModelAdmin) :
    list_display = ("code","name") 
    list_display_links = ("code","name") 
    search_fields = ("name",)
    filter_horizontal = ('for_status',)

@admin.register(Events)
class EventsAdmin(admin.ModelAdmin) :
    list_display = ("date","time","name","type") 
    list_display_links = ("date","time","name") 
    search_fields = ("name","date")
