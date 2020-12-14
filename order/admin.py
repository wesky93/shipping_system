# Register your models here.
import logging
from datetime import datetime

from django import forms
from django.contrib import admin, messages
from django.contrib.admin.helpers import ActionForm
from django.contrib.admin.widgets import AutocompleteSelect
from django.db import transaction
from django.db.models import Exists, OuterRef
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django_fsm_log.admin import StateLogInline
from fsm_admin.mixins import FSMTransitionMixin

from base.models import Address, User
from curation.models import Curation
from .models import Order


class UserAddressChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.id}:{obj.user.name}:{obj.new}"


class ModelAutocompleteSelect(AutocompleteSelect):
    def get_url(self):
        model = self.rel
        return reverse(self.url_name % (self.admin_site.name, model._meta.app_label, model._meta.model_name))


class OrderActionForm(ActionForm):
    curation_menu = forms.ModelChoiceField(
        queryset=Curation.objects.all(),
        required=False,
        widget=ModelAutocompleteSelect(Curation, admin_site=admin.site)
    )


@admin.register(Order)
class OrderAdmin(FSMTransitionMixin, admin.ModelAdmin):
    model = Order
    search_fields = ('user__name', 'user__email', 'date', 'region__city', 'region__district', 'region__town',)
    readonly_fields = ('user', 'new_address', 'old_address', 'etc_address', 'zip', 'region', 'state', 'stocks')
    list_display = ('date', 'state', 'user',)
    list_filter = ('state', 'date', 'region',)
    fsm_field = ['state', ]
    fieldsets = [
        (None, {'fields': ['state', 'date', 'user']}),
        ('배송지 정보', {'fields': ['new_address', 'old_address', 'etc_address', 'zip', 'region', ]}),
        ('음식', {'fields': ['stocks', ]}),

    ]
    change_list_template = 'change_list.html'
    inlines = [StateLogInline]
    actions = ['do_curation', 'assignment_deliverer', 'departure', 'delivered']
    action_form = OrderActionForm

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def do_curation(self, request, queryset):
        total = 0
        fail = 0
        success = 0
        with transaction.atomic():
            curation = Curation.objects.get(pk=request.POST['curation_menu'])
            for order in queryset:
                try:
                    order.curation(curation)
                    order.save()
                    success += 1
                except Exception as e:
                    logging.exception(e)
                    messages.error(request, f"{e}")
                    fail += 1
                total += 1
            if success:
                messages.success(request, f'{total}개중 {success}개 주문에 음식을 배정 했습니다.')
            if fail:
                messages.error(request, f'{total}개중 {fail}개 주문에 음식을 배정하지 못했습니다.')

    do_curation.short_description = '큐레이팅 하기'

    def assignment_deliverer(self, request, queryset):
        total = 0
        fail = 0
        success = 0
        with transaction.atomic():
            for order in queryset:
                try:
                    order.deliverer_assignment()
                    order.save()
                    success += 1
                except Exception as e:
                    logging.exception(e)
                    messages.error(request, f"{e}")
                    fail += 1
                total += 1
            if success:
                messages.success(request, f'{total}개중 {success}개 주문에 배달원을 할당 했습니다')
            if fail:
                messages.error(request, f'{total}개중 {fail}개 주문에 배달원을 할당 하지 못했습니다')

    assignment_deliverer.short_description = '배달 할당'

    def get_urls(self):
        urls = super().get_urls()
        extend_urls = [
            path('create_orders/', self.create_orders, name='create_orders'),
        ]
        return extend_urls + urls

    def create_orders(self, request):
        date = datetime.strptime(request.POST.get('date'), '%Y-%m-%d').date()
        users = User.objects.all().prefetch_related('address_set', ).filter(
            Exists(Address.objects.filter(user_id=OuterRef('pk'))))
        for user in users:
            address = user.address_set.first()
            Order.objects.create(user=user, date=date,
                                 new_address=address.new, old_address=address.old, zip=address.zip,
                                 region=address.region)
        self.message_user(request, f"총 {users.count()}건의 주문이 생성 되었습니다.")
        return HttpResponseRedirect("../")

    def departure(self, request, queryset):
        total = 0
        fail = 0
        success = 0
        with transaction.atomic():
            for order in queryset:
                try:
                    order.departure()
                    order.save()
                    success += 1
                except Exception as e:
                    logging.exception(e)
                    messages.error(request, f"{e}")
                    fail += 1
                total += 1

            if success:
                messages.success(request, f'{total}개중 {success}개 주문이 배달을 출발 했습니다')
            if fail:
                messages.error(request, f'{total}개중 {fail}개가 작업을 실패 했습니다')


    departure.short_description = '배송 출발'

    def delivered(self, request, queryset):
        total = 0
        fail = 0
        success = 0
        with transaction.atomic():
            for order in queryset:
                try:
                    order.finish()
                    order.save()
                    success += 1
                except Exception as e:
                    logging.exception(e)
                    messages.error(request, f"{e}")
                    fail += 1
                total += 1

            if success:
                messages.success(request, f'{total}개중 {success}개 주문에 배당을 완료 했습니다.')
            if fail:
                messages.error(request, f'{total}개중 {fail}개가 작업을 실패 했습니다.')

    delivered.short_description = '배송 완료'
