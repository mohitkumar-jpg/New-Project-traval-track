from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf.urls.static import static
from django.conf import settings
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

def root_redirect(request):
    return redirect("super_admin:login")


urlpatterns = [
    path("", root_redirect),   # 👈 ROOT FIX
    path("admin/", admin.site.urls),
    path("api/super-admin/", include("dashboards.super_admin.api.urls")),
    path("api/branch/", include("dashboards.branch.api.urls")),
    path("api/users/", include("dashboards.users.api.urls")),
    path("api/clients/", include("dashboards.clients.api.urls")),


     # 🔹 Swagger
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui",),
    


]
if settings.DEBUG:
       urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
       urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
