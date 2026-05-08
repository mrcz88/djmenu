from django.contrib import admin
from .models import Item

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'item_price', 'item_desc', 'item_image', 'item_created_at', 'item_updated_at')
    list_filter = ('item_created_at', 'item_updated_at')
    search_fields = ('item_name', 'item_desc')
    list_per_page = 10
    list_max_show_all = 100
    list_editable = ('item_price', 'item_desc', 'item_image')
    list_display_links = ('item_name', 'item_created_at', 'item_updated_at')
    # Item has no relational fields; don't use select_related here.
    
# Register your models here.
