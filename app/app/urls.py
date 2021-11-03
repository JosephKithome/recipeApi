from django.conf.urls.static import static
from django.conf import settings


from django.contrib import admin
from django.urls import path,include
from rest_framework import permissions 
from drf_yasg.views import get_schema_view 
from drf_yasg import openapi
schema_view = get_schema_view( # new
    openapi.Info(
        title="RECIPE API",
        default_version="v1",
        description="Recipe API with TDD",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="hello@example.com"),
        license=openapi.License(name="BSD License"),
    ),
public=True,
permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/',include('user.urls')),
    path('api/recipe/', include('recipe.urls')),

    path('', schema_view.with_ui( # new
        'swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui( # new
        'redoc', cache_timeout=0), name='schema-redoc'),
    

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
