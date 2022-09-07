import io
import csv
from django.contrib import admin
from django.urls import path, re_path
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponse
from django.conf import settings

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
    list_display = ("date","time","name","type","event_actions") 
    list_display_links = ("date","time","name") 
    search_fields = ("name","date")
    readonly_fields = ["event_actions"]
    inlines = [EventPricesInline]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            re_path(r'^(?P<event_pk>.+)/csv/$', self.admin_site.admin_view(self.process_download_requests), name='download-requests'),
        ]
        return custom_urls + urls
 
    def event_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">Выгрузить заявки</a> ',
            reverse('admin:download-requests', args=[obj.pk]),
        )
    event_actions.short_description = 'Действия с мероприятием'
    event_actions.allow_tags = True
    
    def process_download_requests(self, request, event_pk):
        event = Events.objects.get(pk = event_pk)        
        out = io.StringIO()
        writer = csv.writer(out, delimiter=';', lineterminator='\n')
        writer.writerow(["number", "created_at", "event", "user_id", "user", "for_status",
                        "price", "payed", "confirmed", "rating", "rating_comment",]) 
        for request in event.eventrequests_set.all():
            writer.writerow([str(request.number), 
                             str(request.created_at),
                             str(request.event),
                             str(request.user_id),
                             str(request.user),
                             str(request.for_status),
                             str(request.price),
                             str(request.payed),
                             str(request.confirmed),
                             str(request.rating),
                             str(request.rating_comment),                             
                             ])  
                  
        content = out.getvalue()
        out.close()
        return HttpResponse(content,
                            headers={
                                'Content-Type': 'text/txt',
                                'Content-Disposition': 'attachment; filename="event_requests.txt"',
                            })

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
    #filter_horizontal = ('sending_groups',)
    inlines = [AnonsesDatesInline]