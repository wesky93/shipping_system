# Create your views here.
from django.contrib.auth.models import AnonymousUser
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response

from base.models import Address, User
from base.serializer import AddressSerializer, CreateAddressSchema, CreateAddressSerializer, CreateUserSerializer, \
    UserSerializer

user_response = openapi.Response('사용자 정보', UserSerializer)

address_response = openapi.Response('사용자 주소', AddressSerializer)


class UserViewSet(viewsets.ViewSet):
    queryset = User.objects.all()

    @swagger_auto_schema(
        operation_id='user_info',
        operation_summary='내 정보',
        responses={"200": user_response}
    )
    def list(self, request):
        if isinstance(request.user, AnonymousUser):
            return NotAuthenticated()

        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_id='sign_up',
        operation_summary='회원가입',
        request_body=CreateUserSerializer,
        responses={"200": user_response})
    def create(self, request):

        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddressViewSet(viewsets.ViewSet):

    def get_queryset(self):
        return Address.objects.all()

    @swagger_auto_schema(
        operation_id='my_address_list',
        operation_summary='내 주소 조회',
        responses={"200": address_response}
    )
    def list(self, request):
        qs = self.get_queryset().filter(user=request.user)
        serializer = AddressSerializer(qs, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_id='add_my_address',
        operation_summary='내 주소 추가',
        request_body=CreateAddressSchema,
        responses={"200": address_response}
    )
    def create(self, request):
        data = request.data
        data['user'] = request.user.id

        serializer = CreateAddressSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(AddressSerializer(serializer.instance).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        operation_id='delete_my_address',
        operation_summary='내 주소 삭제',
    )
    def destroy(self, request, pk=None):
        self.get_queryset().filter(user=request.user, id=pk).delete()
        return Response(status=status.HTTP_200_OK)
