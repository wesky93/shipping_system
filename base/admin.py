from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import Address, Region, User
from .utils import normalize_address


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('address', 'etc', 'old', 'new', 'region')

        widgets = {
            'old': forms.TextInput(attrs={'disabled': True}),
            'new': forms.TextInput(attrs={'disabled': True}),
            'etc': forms.TextInput(attrs={'placeholder': '나머지 주소를 입력하세요'}, ),
            'region': forms.TextInput(attrs={'disabled': True}),

        }

    address = forms.CharField(
        label='주소',
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': '주소를 입력하세요'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        try:
            address = normalize_address(cleaned_data.get('address'))
        except Exception as _:
            raise ValidationError('주소를 상세하게 입력해주세요. https://www.juso.go.kr/openIndexPage.do')

        cleaned_data['old'] = address.old
        cleaned_data['new'] = address.new
        cleaned_data['zip'] = address.zip
        cleaned_data['region'], _ = Region.objects.get_or_create(city=address.city,
                                                                 district=address.district,
                                                                 town=address.town)
        return cleaned_data


class AddressInlineAdmin(admin.TabularInline):
    model = Address
    form = AddressForm


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    model = Address


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    model = Region


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    model = User
    fieldsets = (
        (None, {'fields': ('email', 'name')}),
        ('권한',
         {'fields': ('is_active', 'is_superuser', 'is_staff', 'groups', 'user_permissions'), 'classes': ['collapse']})
    )

    inlines = (AddressInlineAdmin,)
