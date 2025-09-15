from django.contrib import admin
from .models import Order, Item

admin.site.register(Order)

class ItemAdmin(admin.ModelAdmin):
    list_display = ('movie', 'quantity', 'price') 

admin.site.register(Item, ItemAdmin)
