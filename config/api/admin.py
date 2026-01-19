from django.contrib import admin
from .models import Event, TicketPurchase, TicketType

admin.site.register(Event)
admin.site.register(TicketType)
admin.site.register(TicketPurchase)
        