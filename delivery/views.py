# Create your views here.
from datetime import datetime

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from delivery.serializer import TaskSerializer
from order.models import Order

task_response = openapi.Response('주문 정보', TaskSerializer)


class TaskViewSet(viewsets.ViewSet):
    def get_queryset(self):
        return Order.objects.filter(date=datetime.now().date())

    @swagger_auto_schema(
        operation_id='today_order_list',
        operation_summary='오늘 배송 물량',
        responses={"200": task_response}
    )
    def list(self, request):
        orders = self.get_queryset().filter(deliverer__user=request.user)
        serializer = TaskSerializer(orders,many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_id='pickup',
        operation_summary='픽업', )
    @action(detail=True, methods=['post'])
    def pickup(self, request, pk=None):
        qs = self.get_queryset().filter(deliverer__user=request.user).filter(pk=pk).first()
        if qs:
            qs.departure()
            qs.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_id='deliver_completed',
        operation_summary='배송 완료', )
    @action(detail=True, methods=['post'])
    def done(self, request, pk=None):
        qs = self.get_queryset().filter(deliverer__user=request.user).filter(pk=pk).first()
        if qs:
            qs.finish()
            qs.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
