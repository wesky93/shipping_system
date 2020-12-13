from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from base.models import Address, Region, User
from base.utils import normalize_address


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'name', 'date_joined']


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'name', 'password', ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            name=validated_data['name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id','old', 'new', 'zip', 'etc']


class CreateAddressSchema(serializers.Serializer):
    address = serializers.CharField(required=True)
    etc = serializers.CharField(default='', required=False)


class CreateAddressSerializer(serializers.Serializer):
    user = serializers.ModelField(model_field=Address()._meta.get_field('user'))
    address = serializers.CharField(required=True)
    etc = serializers.CharField(default='', required=False)

    def create(self, validated_data):
        obj = Address(
            user_id=validated_data['user'],
            etc=validated_data['etc'],
        )
        try:
            address = normalize_address(validated_data['address'])
        except Exception as _:
            raise ValidationError('주소를 상세하게 입력해주세요')

        obj.old = address.old
        obj.new = address.new
        obj.zip = address.zip
        obj.region, _ = Region.objects.get_or_create(city=address.city,
                                                     district=address.district,
                                                     town=address.town)

        obj.save()
        return obj
