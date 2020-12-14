from rest_framework import routers

from delivery.views import TaskViewSet

router = routers.SimpleRouter()
router.register(r'', TaskViewSet, basename='deliver')
