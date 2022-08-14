from django.contrib import admin
from .models import *

@admin.register(Events)
class EventsAdmin(admin.ModelAdmin) :
    list_display = ("date","time","name") 
    list_display_links = ("date","time","name") 
    search_fields = ("name","date")
