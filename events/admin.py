from django.contrib import admin
from .models import *

class EventPricesInline(admin.TabularInline):
    model = EventPrices

@admin.register(EventTypes)
class EventTypesAdmin(admin.ModelAdmin):
    readonly_fields = ["code"]
    list_display = ("code","name") 
    list_display_links = ("code","name") 
    search_fields = ("name",)

@admin.register(Events)
class EventsAdmin(admin.ModelAdmin) :
    exclude = ['file_id','invite_file_id'] # Be sure to read only mode
    list_display = ("date","time","name","type") 
    list_display_links = ("date","time","name") 
    search_fields = ("name","date")
    inlines = [EventPricesInline]

@admin.register(EventRequests)
class EventRequestsAdmin(admin.ModelAdmin) :
    list_display = ("number","created_at","event","user", "price", "payed", "confirmed") 
    list_display_links = ("number","created_at","event","user", "price",) 
    search_fields = ("event","user",)
    list_filter = ["payed", "confirmed",]