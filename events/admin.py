from django.contrib import admin
from .models import *

class EventPricesInline(admin.TabularInline):
    model = EventPrices

class AnonsesInline(admin.TabularInline):
    model = Anonses

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

class AnonsesDatesInline(admin.TabularInline):
    model = AnonsesDates
@admin.register(Anonses)
class AnonsesAdmin(admin.ModelAdmin):
    list_display = ("event","show_groups") 
    list_display_links = ("event","show_groups") 
    search_fields = ("event",)
    filter_horizontal = ('sending_groups',)
    inlines = [AnonsesDatesInline]