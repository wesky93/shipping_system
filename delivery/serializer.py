from rest_framework import serializers

from order.models import Order


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'date', 'new_address', 'old_address', 'etc_address', 'state']
