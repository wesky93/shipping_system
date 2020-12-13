from rest_framework import routers

from base.views import AddressViewSet, UserViewSet

router = routers.SimpleRouter()
router.register(r'user', UserViewSet, basename='user')
router.register(r'address', AddressViewSet, basename='address')