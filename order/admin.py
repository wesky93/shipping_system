# Register your models here.
from datetime import datetime

from django import forms
from django.contrib import admin
from django.db.models import Exists, OuterRef
from django.http import HttpResponseRedirect
from django.urls import path

from base.models import Address, User
from .models import Order


class UserAddressChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.id}:{obj.user.name}:{obj.new}"


class NewOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('date', 'user', 'new_address', 'old_address', 'zip', 'user')
        widgets = {
            'new_address': forms.TextInput(attrs={'disabled': True}),
            'old_address': forms.TextInput(attrs={'disabled': True}),
            'etc': forms.TextInput(attrs={'placeholder': '나머지 주소를 입력하세요'}, ),
            'region': forms.TextInput(attrs={'disabled': True}),
            'zip': forms.TextInput(attrs={'disabled': True}),

        }

    date = forms.DateField()

    def clean(self):
        cleaned_data = super().clean()
        address = cleaned_data['user']

        cleaned_data['user'] = address.user
        cleaned_data['new_address'] = address.new
        cleaned_data['old_address'] = address.old
        cleaned_data['zip'] = address.zip
        cleaned_data['region'] = address.region
        return cleaned_data


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    model = Order
    # form = NewOrderForm
    search_fields = ('user__name', 'user__email', 'date', 'region__city', 'region__district', 'region__town',)
    readonly_fields = ('user', 'new_address', 'old_address', 'etc_address', 'zip', 'region', 'state')
    list_display = ('date', 'state', 'user',)
    list_filter = ('state', 'date', 'region',)
    fieldsets = [
        (None, {'fields': ['state', 'date', 'user']}),
        ('배송지 정보', {'fields': ['new_address', 'old_address', 'etc_address', 'zip', 'region', ]})
    ]
    change_list_template = 'change_list.html'

    def has_add_permission(self, request):
        return False

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
