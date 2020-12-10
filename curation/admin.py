from adminsortable2.admin import SortableInlineAdminMixin
from django.contrib import admin

# Register your models here.
from curation.models import Curation, Menu, SetMenu


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    model = Menu


@admin.register(SetMenu)
class SetMenuAdmin(admin.ModelAdmin):
    model = SetMenu


class CurationPriorityTabularInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Curation.set_menus.through


@admin.register(Curation)
class CurationAdmin(admin.ModelAdmin):
    model = Curation
    inlines = (CurationPriorityTabularInline,)
