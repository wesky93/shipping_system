"""shipping_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import debug_toolbar
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions, routers
from rest_framework_jwt.views import obtain_jwt_token

from base.urls import router as base_router

schema_url_patterns = [
    path('account/', include(base_router.urls)),
    url(r'^auth/', obtain_jwt_token),

]
schema_view = get_schema_view(
    openapi.Info(
        title="Food API",
        default_version='v1',
        description="food api",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=schema_url_patterns
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
urlpatterns += schema_url_patterns

if settings.DEBUG:
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls)), ]
