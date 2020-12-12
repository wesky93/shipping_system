from django.contrib import admin

# Register your models here.
from delivery.models import Deliverer


class RegionInlineAdmin(admin.TabularInline):
    verbose_name = '배송 가능 지역'
    verbose_name_plural = '배송 가능 지역들'

    model = Deliverer.available_region.through


@admin.register(Deliverer)
class DelivererAdmin(admin.ModelAdmin):
    model = Deliverer
    fieldsets = ((None, {'fields': ('user',)}),)
    inlines = (RegionInlineAdmin,)
