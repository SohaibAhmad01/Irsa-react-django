from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import  settings

# router = DefaultRouter()
# router.register("adminuser", AdminUserView)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('irsa/v1/', include('adminapp.urls')),
    path('irsa/v1/', include('teacherapp.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)